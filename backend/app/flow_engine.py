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
        for i in range(current_idx + 1, target_idx + 1):
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
        db = Session.object_session(order)
        if not db:
            return True, ""

        oid = order.id

        if step == "INVOICE":
            inv = (
                db.query(models.Invoice)
                .filter(models.Invoice.order_fk == oid)
                .first()
            )
            if not inv:
                return False, "No invoice found"

        elif step == "SAMPLE":
            sr = (
                db.query(models.SampleRecord)
                .filter(models.SampleRecord.order_fk == oid)
                .first()
            )
            if not sr:
                return False, "No sample record found"

        elif step == "SAMPLE_APPROVED":
            samples = (
                db.query(models.SampleRecord)
                .filter(models.SampleRecord.order_fk == oid)
                .all()
            )
            if not samples:
                return False, "No sample records found"
            if not any(s.status == "APPROVED" for s in samples):
                return False, "No sample has APPROVED status"

        elif step == "SPK":
            spk = (
                db.query(models.SPK)
                .filter(models.SPK.order_fk == oid)
                .first()
            )
            if not spk:
                return False, "No SPK found"

        elif step == "PRODUCTION":
            total_movements = (
                db.query(func.count(models.ProductionMovement.id))
                .join(
                    models.Article,
                    models.ProductionMovement.article_id == models.Article.id,
                )
                .filter(models.Article.order_fk == oid)
                .scalar()
                or 0
            )
            if total_movements == 0:
                return False, "No production movements found"
            done_movements = (
                db.query(func.count(models.ProductionMovement.id))
                .join(
                    models.Article,
                    models.ProductionMovement.article_id == models.Article.id,
                )
                .filter(
                    models.Article.order_fk == oid,
                    models.ProductionMovement.status == "DONE",
                )
                .scalar()
                or 0
            )
            if done_movements == total_movements:
                return False, "All production movements are DONE"

        elif step == "QC":
            qc = (
                db.query(models.QCRecord)
                .filter(models.QCRecord.order_fk == oid)
                .first()
            )
            if not qc:
                return False, "No QC records found"

        elif step == "SHIPMENT":
            shp = (
                db.query(models.Shipment)
                .filter(models.Shipment.order_fk == oid)
                .first()
            )
            if not shp:
                return False, "No shipments found"
            if shp.finance_gate != "CLEAR":
                return (
                    False,
                    f"Finance gate is '{shp.finance_gate}', must be CLEAR",
                )

        elif step == "DELIVERED":
            shipments = (
                db.query(models.Shipment)
                .filter(models.Shipment.order_fk == oid)
                .all()
            )
            if not shipments:
                return False, "No shipments found"
            has_confirmed = False
            for shp_item in shipments:
                dc = (
                    db.query(models.DeliveryConfirmation)
                    .filter(
                        models.DeliveryConfirmation.shipment_fk == shp_item.id,
                        models.DeliveryConfirmation.status == "CONFIRMED",
                    )
                    .first()
                )
                if dc:
                    has_confirmed = True
                    break
            if not has_confirmed:
                return False, "No confirmed delivery confirmation found"

        elif step == "CLOSED":
            closings = (
                db.query(models.OrderClosing)
                .filter(models.OrderClosing.order_fk == oid)
                .all()
            )
            if not closings:
                return False, "No order closing records found"
            if not all(c.order_close_status == "CLOSED" for c in closings):
                return False, "Not all order closings are CLOSED"

        return True, ""

    # ────── ADVANCE ──────
    @staticmethod
    def advance(order, target_step: str, user=None) -> dict:
        """Advance order to target_step with validation.

        Returns transition info dict.
        """
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

        db.commit()
        db.refresh(order)

        detail = f"flow_step: {old_step} -> {target_step}"
        log_audit(db, user, "FLOW_ADVANCE", "Order", order.id, detail)

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
