"""Flow Engine — manages order lifecycle steps for three order types.

Provides flow definitions, transition validation, and auto-status-update logic.
"""
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models
from .audit import log_audit


# ──────────── FLOW DEFINITIONS ────────────

FLOW_DEFINITIONS = {
    "SAMPLE_ONLY": [
        "ORDER", "INVOICE", "PPM", "SAMPLE", "SAMPLE_APPROVED",
        "FOLLOW_UP", "CLOSED",
    ],
    "SAMPLE_PRODUCTION": [
        "ORDER", "INVOICE", "SAMPLE", "SAMPLE_APPROVED", "SPK",
        "PRODUCTION", "QC", "SHIPMENT", "DELIVERED", "CLOSED",
    ],
    "REPEAT_PRODUCTION": [
        "ORDER", "INVOICE", "PPM", "SPK", "PRODUCTION", "QC",
        "SHIPMENT", "DELIVERED", "CLOSED",
    ],
}

STEP_LABELS = {
    "ORDER": "Order Diterima",
    "INVOICE": "Invoice & Pembayaran",
    "PPM": "PPM / Penyesuaian",
    "SAMPLE": "Sample / PPM",
    "SAMPLE_APPROVED": "Sample Disetujui",
    "FOLLOW_UP": "Follow-up / Pengembangan",
    "SPK": "SPK Release",
    "PRODUCTION": "Produksi",
    "QC": "QC & Packing",
    "SHIPMENT": "Pengiriman",
    "DELIVERED": "Diterima Customer",
    "CLOSED": "Order Selesai",
}

STEP_GATES = {
    "ORDER": "CMO",
    "INVOICE": "CFO",
    "PPM": "CMO+COO",
    "SAMPLE": "SAMPLE_PIC",
    "SAMPLE_APPROVED": "CMO",
    "FOLLOW_UP": "CMO",
    "SPK": "CMO",
    "PRODUCTION": "COO",
    "QC": "PRODUCTION_PIC",
    "SHIPMENT": "SHIPMENT_ADMIN",
    "DELIVERED": "CMO",
    "CLOSED": "CMO+CFO",
}


class FlowEngine:
    """Engine for managing order lifecycle flows."""

    VALID_STEPS = FLOW_DEFINITIONS

    # ────── GET FLOW ──────
    @staticmethod
    def get_flow(order_type: str) -> list:
        """Return the ordered list of steps for the given order type."""
        flow = FLOW_DEFINITIONS.get(order_type)
        if not flow:
            raise HTTPException(400, f"Unknown order type: {order_type}")
        return list(flow)

    # ────── GET FLOW PROGRESS ──────
    @staticmethod
    def get_flow_progress(order_type: str, current_step: str = "ORDER") -> dict:
        """Return flow definition with steps, current index, and percent."""
        steps = FlowEngine.get_flow(order_type)
        try:
            current_index = steps.index(current_step)
        except ValueError:
            current_index = 0
        percent = (
            round((current_index / (len(steps) - 1)) * 100)
            if len(steps) > 1
            else 100
        )
        return {
            "steps": [
                {
                    "key": s,
                    "label": STEP_LABELS.get(s, s),
                    "gate": STEP_GATES.get(s, ""),
                }
                for s in steps
            ],
            "current_index": current_index,
            "percent": percent,
        }

    # ────── CAN TRANSITION ──────
    @staticmethod
    def can_transition(order, target_step: str) -> tuple:
        """Validate whether order can transition to target_step.

        Returns (bool, reason_string).
        """
        order_type_val = (
            order.order_type.value
            if hasattr(order.order_type, "value")
            else order.order_type
        )
        steps = FlowEngine.get_flow(order_type_val)
        current = order.flow_step or "ORDER"

        if target_step not in steps:
            return (
                False,
                f"Invalid step '{target_step}' for order type {order_type_val}",
            )

        try:
            current_idx = steps.index(current)
            target_idx = steps.index(target_step)
        except ValueError:
            return False, f"Current step '{current}' not in flow"

        if target_idx <= current_idx:
            return (
                False,
                f"Cannot go backwards from '{current}' to '{target_step}'",
            )

        # Check all intermediate steps + the target step have prerequisites met
        for i in range(1, target_idx + 1):
            step = steps[i]
            ok, reason = FlowEngine._check_step_prerequisite(order, step)
            if not ok:
                return False, f"Step '{step}' prerequisite not met: {reason}"

        return True, "OK"

    # ────── CHECK STEP PREREQUISITE ──────
    @staticmethod
    def _check_step_prerequisite(order, step: str) -> tuple:
        """Check if a specific step's prerequisites are satisfied.

        Returns (bool, reason_string).
        """
        from . import workflow as w
        db = Session.object_session(order)
        if not db:
            return False, "No database session available for validation"
        try:
            if step == "INVOICE":
                if not w.quotation_ready(db, order):
                    return False, "Latest quotation must be approved by CFO"
                if not w.finance_ready(db, order):
                    return False, "CFO must approve the documented payment/DP assessment"
            elif step == "SAMPLE":
                if not db.query(models.SampleRecord).filter_by(order_fk=order.id).first():
                    return False, "No sample record found"
            elif step == "SAMPLE_APPROVED":
                if not w.samples_ready(db, order):
                    return False, "Latest sample for every required article needs CMO customer approval"
            elif step == "SPK":
                if not w.spk_ready(db, order):
                    return False, "Latest SPK must be released with a versioned article snapshot"
            elif step == "PRODUCTION":
                w.production_ready(db, order)
            elif step == "QC":
                if not w.qc_ready(db, order):
                    return False, "Latest final QC for every article must pass without unresolved rejects"
            elif step == "SHIPMENT":
                shipments = db.query(models.Shipment).filter_by(order_fk=order.id).all()
                if not shipments:
                    return False, "No shipments found"
                for shipment in shipments:
                    w.shipment_ready(db, shipment)
                    if shipment.status not in ("SHIPPED", "DELIVERED"):
                        return False, "All shipments must be dispatched"
            elif step == "DELIVERED":
                if not w.deliveries_ready(db, order):
                    return False, "Every shipment requires customer confirmation"
            elif step == "CLOSED":
                rec = db.query(models.OrderClosing).filter_by(order_fk=order.id).first()
                total, paid = w.invoices_total(db, order.id)
                if not rec or rec.customer_close_status != "CLOSED" or rec.operational_close_status != "CLOSED" or rec.financial_close_status != "CLOSED" or rec.order_close_status != "CLOSED" or total <= 0 or paid < total:
                    return False, "Customer, operational and financial closing with zero outstanding required"
        except HTTPException as exc:
            return False, str(exc.detail)
        return True, ""

    @staticmethod
    def advance(order, target_step: str, user=None) -> dict:
        """Advance order to target_step with validation.

        Returns transition info dict.
        """
        from .workflow import require
        owners = {
            "INVOICE": ("CFO_MANAGER",), "PPM": ("CMO_MANAGER", "COO_MANAGER"),
            "SAMPLE": ("SAMPLE_PIC", "CMO_MANAGER"), "SAMPLE_APPROVED": ("CMO_MANAGER",),
            "FOLLOW_UP": ("CMO_MANAGER",), "SPK": ("CMO_MANAGER",),
            "PRODUCTION": ("COO_MANAGER",), "QC": ("COO_MANAGER", "PRODUCTION_PIC"),
            "SHIPMENT": ("COO_MANAGER", "SHIPMENT_ADMIN"), "DELIVERED": ("CMO_MANAGER",),
            "CLOSED": ("CMO_MANAGER", "COO_MANAGER", "CFO_MANAGER"),
        }
        require(user, *owners.get(target_step, ()))
        ok, reason = FlowEngine.can_transition(order, target_step)
        if not ok:
            raise HTTPException(400, reason)

        db = Session.object_session(order)
        if not db:
            raise HTTPException(500, "No database session found")

        old_step = order.flow_step or "ORDER"
        order.flow_step = target_step

        # Auto-update overall_status based on target step
        status_map = {
            "ORDER": "NEW",
            "INVOICE": "NEW",
            "PPM": "ACTIVE",
            "SAMPLE": "ACTIVE",
            "SAMPLE_APPROVED": "ACTIVE",
            "FOLLOW_UP": "ACTIVE",
            "SPK": "ACTIVE",
            "PRODUCTION": "ACTIVE",
            "QC": "ACTIVE",
            "SHIPMENT": "ACTIVE",
            "DELIVERED": "COMPLETED",
            "CLOSED": "CLOSED",
        }
        order.overall_status = status_map.get(target_step, order.overall_status)

        detail = f"flow_step: {old_step} -> {target_step}"
        log_audit(db, user, "FLOW_ADVANCE", "Order", order.id, detail)
        db.commit()
        db.refresh(order)

        return {
            "order_id": order.order_id,
            "old_step": old_step,
            "new_step": target_step,
            "overall_status": order.overall_status,
        }

    # ────── GET ALL DEFINITIONS ──────
    @staticmethod
    def get_all_definitions() -> dict:
        """Return all three flow definitions with labels and gates."""
        result = {}
        for order_type, steps in FLOW_DEFINITIONS.items():
            result[order_type] = {
                "steps": [
                    {
                        "key": s,
                        "label": STEP_LABELS.get(s, s),
                        "gate": STEP_GATES.get(s, ""),
                    }
                    for s in steps
                ]
            }
        return result
