from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional
from datetime import date
from ..database import get_db
from ..auth import get_current_user, require_roles
from .. import models
from ..audit import log_audit

router = APIRouter(tags=["modules"])

# ──────────── HELPERS ────────────
def get_or_404(db, model, id, label="Not found"):
    x = db.query(model).filter(model.id == id).first()
    if not x: raise HTTPException(404, label)
    return x

def apply_update(obj, data, db, user=None, entity_name=None):
    changes = []
    for k,v in data.model_dump(exclude_unset=True).items():
        old = getattr(obj, k, None)
        setattr(obj, k, v)
        if old != v: changes.append(f"{k}={v}")
    db.commit(); db.refresh(obj)
    if user and entity_name:
        log_audit(db, user, "UPDATE", entity_name, obj.id, "; ".join(changes))
    return obj

# ──────────── CMO: CUSTOMERS ────────────
class CustomerIn(BaseModel):
    name:str; country:Optional[str]=None; contact_name:Optional[str]=None; contact_info:Optional[str]=None; notes:Optional[str]=None

@router.get("/cmo/customers")
def customers(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Customer).order_by(models.Customer.name).all()

@router.post("/cmo/customers")
def create_customer(data:CustomerIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER,models.Role.CMO_SUPPORT))):
    x=models.Customer(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); log_audit(db, "CREATE", "Customer", x.id, x.name); return x

class CustomerUpdate(BaseModel):
    name:Optional[str]=None; country:Optional[str]=None; contact_name:Optional[str]=None; contact_info:Optional[str]=None; notes:Optional[str]=None

@router.patch("/cmo/customers/{customer_id}")
def update_customer(customer_id:int, data:CustomerUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER,models.Role.CMO_SUPPORT))):
    return apply_update(get_or_404(db,models.Customer,customer_id,"Customer not found"), data, db)

@router.delete("/cmo/customers/{customer_id}")
def delete_customer(customer_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER))):
    x=get_or_404(db,models.Customer,customer_id,"Customer not found"); name=x.name; db.delete(x); db.commit(); log_audit(user, "DELETE", "Customer", customer_id, name); return {"ok":True}

# ──────────── CMO: QUOTATIONS ────────────
class QuotationIn(BaseModel):
    quotation_no:str; order_fk:Optional[int]=None; amount:float; status:str="DRAFT"; valid_until:Optional[date]=None; notes:Optional[str]=None

class QuotationUpdate(BaseModel):
    amount:Optional[float]=None; status:Optional[str]=None; valid_until:Optional[date]=None; notes:Optional[str]=None

@router.get("/cmo/quotations")
def list_quotations(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Quotation).order_by(desc(models.Quotation.id)).all()

@router.post("/cmo/quotations")
def create_quotation(data:QuotationIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER,models.Role.CMO_SUPPORT))):
    x=models.Quotation(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/cmo/quotations/{q_id}")
def update_quotation(q_id:int, data:QuotationUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER))):
    return apply_update(get_or_404(db,models.Quotation,q_id,"Quotation not found"), data, db)

@router.delete("/cmo/quotations/{q_id}")
def delete_quotation(q_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER))):
    x=get_or_404(db,models.Quotation,q_id); db.delete(x); db.commit(); return {"ok":True}

# ──────────── CMO: SAMPLE RECORDS ────────────
class SampleIn(BaseModel):
    order_fk:int; article_code:str; status:str="PROCESS"; notes:Optional[str]=None; requested_date:Optional[date]=None; completed_date:Optional[date]=None

class SampleUpdate(BaseModel):
    status:Optional[str]=None; notes:Optional[str]=None; completed_date:Optional[date]=None

@router.get("/cmo/samples")
def list_samples(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.SampleRecord).order_by(desc(models.SampleRecord.id)).all()

@router.post("/cmo/samples")
def create_sample(data:SampleIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER,models.Role.SAMPLE_PIC))):
    x=models.SampleRecord(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/cmo/samples/{s_id}")
def update_sample(s_id:int, data:SampleUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER,models.Role.SAMPLE_PIC))):
    return apply_update(get_or_404(db,models.SampleRecord,s_id,"Sample not found"), data, db)

# ──────────── CMO: SPK ────────────
class SPKIn(BaseModel):
    order_fk:int; spk_no:str; status:str="NEW"; notes:Optional[str]=None

class SPKUpdate(BaseModel):
    status:Optional[str]=None; notes:Optional[str]=None

@router.get("/cmo/spk")
def list_spk(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.SPK).order_by(desc(models.SPK.id)).all()

@router.post("/cmo/spk")
def create_spk(data:SPKIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER,models.Role.CMO_SUPPORT))):
    x=models.SPK(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); log_audit(user, "CREATE", "SPK", x.id, x.spk_no); return x

@router.patch("/cmo/spk/{spk_id}")
def update_spk(spk_id:int, data:SPKUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER))):
    return apply_update(get_or_404(db,models.SPK,spk_id,"SPK not found"), data, db)

@router.delete("/cmo/spk/{spk_id}")
def delete_spk(spk_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER))):
    x=get_or_404(db,models.SPK,spk_id); info=x.spk_no; db.delete(x); db.commit(); log_audit(user, "DELETE", "SPK", spk_id, info); return {"ok":True}

# ──────────── CFO: INVOICES ────────────
class InvoiceIn(BaseModel):
    invoice_no:str; order_fk:int; amount:float; paid_amount:float=0; due_date:Optional[date]=None; status:str="UNPAID"

class InvoiceUpdate(BaseModel):
    amount:Optional[float]=None; paid_amount:Optional[float]=None; due_date:Optional[date]=None; status:Optional[str]=None

@router.get("/cfo/invoices")
def invoices(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Invoice).order_by(desc(models.Invoice.id)).all()

@router.post("/cfo/invoices")
def create_invoice(data:InvoiceIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER,models.Role.FINANCE_SUPPORT))):
    x=models.Invoice(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); log_audit(user, "CREATE", "Invoice", x.id, x.invoice_no); return x

@router.patch("/cfo/invoices/{inv_id}")
def update_invoice(inv_id:int, data:InvoiceUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER))):
    x = get_or_404(db,models.Invoice,inv_id,"Invoice not found")
    result = apply_update(x, data, db)
    # Auto-update order.finance_status
    if x.order_fk and (data.status or data.paid_amount is not None):
        from sqlalchemy import func
        total = db.query(func.coalesce(func.sum(models.Invoice.amount),0)).filter(models.Invoice.order_fk==x.order_fk).scalar() or 0
        paid = db.query(func.coalesce(func.sum(models.Invoice.paid_amount),0)).filter(models.Invoice.order_fk==x.order_fk).scalar() or 0
        order = db.query(models.Order).get(x.order_fk)
        if order:
            if float(paid) >= float(total) and float(total) > 0:
                order.finance_status = "PAID"
            elif float(paid) > 0:
                order.finance_status = "PARTIAL"
            else:
                order.finance_status = "UNPAID"
            db.commit()
    return result

@router.delete("/cfo/invoices/{inv_id}")
def delete_invoice(inv_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER))):
    x=get_or_404(db,models.Invoice,inv_id); info=x.invoice_no; db.delete(x); db.commit(); log_audit(user, "DELETE", "Invoice", inv_id, info); return {"ok":True}

# ──────────── CFO: PURCHASE ORDERS ────────────
class POIn(BaseModel):
    po_no:str; order_fk:Optional[int]=None; item:str; qty:float; unit:Optional[str]=None; supplier:Optional[str]=None; amount:Optional[float]=0; status:str="PENDING"

class POUpdate(BaseModel):
    item:Optional[str]=None; qty:Optional[float]=None; unit:Optional[str]=None; supplier:Optional[str]=None; amount:Optional[float]=None; status:Optional[str]=None; arrival_date:Optional[date]=None; material_status:Optional[str]=None

@router.get("/cfo/purchase-orders")
def list_pos(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.PurchaseOrder).order_by(desc(models.PurchaseOrder.id)).all()

@router.post("/cfo/purchase-orders")
def create_po(data:POIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER,models.Role.FINANCE_SUPPORT))):
    x=models.PurchaseOrder(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); log_audit(user, "CREATE", "PurchaseOrder", x.id, x.po_no); return x

@router.patch("/cfo/purchase-orders/{po_id}")
def update_po(po_id:int, data:POUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER))):
    return apply_update(get_or_404(db,models.PurchaseOrder,po_id,"PO not found"), data, db)

@router.delete("/cfo/purchase-orders/{po_id}")
def delete_po(po_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER))):
    x=get_or_404(db,models.PurchaseOrder,po_id); info=x.po_no; db.delete(x); db.commit(); log_audit(user, "DELETE", "PurchaseOrder", po_id, info); return {"ok":True}

# ──────────── CFO: PAYMENTS ────────────
class PaymentIn(BaseModel):
    invoice_no:str; amount:float; payment_date:Optional[date]=None; method:Optional[str]=None; notes:Optional[str]=None

@router.get("/cfo/payments")
def list_payments(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Payment).order_by(desc(models.Payment.id)).all()

@router.post("/cfo/payments")
def create_payment(data:PaymentIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER,models.Role.FINANCE_SUPPORT))):
    x=models.Payment(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

# ──────────── COO: MATERIAL REQUESTS ────────────
class MaterialIn(BaseModel):
    order_fk:int; item_name:str; qty:float; unit:Optional[str]=None; required_date:Optional[date]=None

@router.get("/coo/material-requests")
def material_requests(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.MaterialRequest).order_by(desc(models.MaterialRequest.id)).all()

@router.post("/coo/material-requests")
def create_material_request(data:MaterialIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER,models.Role.PRODUCTION_PIC))):
    x=models.MaterialRequest(**data.model_dump(),requested_by=user.name); db.add(x); db.commit(); db.refresh(x); return x

class MaterialRequestUpdate(BaseModel):
    item_name:Optional[str]=None; qty:Optional[float]=None; unit:Optional[str]=None; status:Optional[str]=None; required_date:Optional[date]=None

@router.patch("/coo/material-requests/{mr_id}")
def update_material_request(mr_id:int, data:MaterialRequestUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER,models.Role.PRODUCTION_PIC))):
    return apply_update(get_or_404(db,models.MaterialRequest,mr_id,"Material request not found"), data, db)

@router.delete("/coo/material-requests/{mr_id}")
def delete_material_request(mr_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER))):
    x=get_or_404(db,models.MaterialRequest,mr_id); db.delete(x); db.commit(); return {"ok":True}

# ──────────── COO: PRODUCTION MOVEMENTS ────────────
class MovementIn(BaseModel):
    article_id:int; process:str; qty_in:int=0; qty_done:int=0; qty_reject:int=0; status:str="IN_PROCESS"; pic_name:Optional[str]=None

class MovementUpdate(BaseModel):
    qty_in:Optional[int]=None; qty_done:Optional[int]=None; qty_reject:Optional[int]=None; status:Optional[str]=None; pic_name:Optional[str]=None; reject_reason:Optional[str]=None; target_date:Optional[date]=None

@router.post("/coo/movements")
def create_movement(data:MovementIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER,models.Role.PRODUCTION_PIC,models.Role.PRINTING_PIC,models.Role.SAMPLE_PIC))):
    if data.qty_done > data.qty_in: raise HTTPException(400,"qty_done cannot exceed qty_in")
    x=models.ProductionMovement(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.get("/coo/movements")
def list_movements(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.ProductionMovement).order_by(desc(models.ProductionMovement.id)).all()

@router.patch("/coo/movements/{mov_id}")
def update_movement(mov_id:int, data:MovementUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER,models.Role.PRODUCTION_PIC))):
    return apply_update(get_or_404(db,models.ProductionMovement,mov_id,"Movement not found"), data, db)

# ──────────── COO: PRODUCTION PLANS ────────────
class PlanIn(BaseModel):
    order_fk:int; plan_date:Optional[date]=None; status:str="PLANNING"; notes:Optional[str]=None

class PlanUpdate(BaseModel):
    order_fk:Optional[int]=None; plan_date:Optional[date]=None; status:Optional[str]=None; notes:Optional[str]=None

@router.get("/coo/production-plans")
def list_plans(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.ProductionPlan).order_by(desc(models.ProductionPlan.id)).all()

@router.post("/coo/production-plans")
def create_plan(data:PlanIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER))):
    x=models.ProductionPlan(**data.model_dump(), created_by_id=user.id); db.add(x); db.commit(); db.refresh(x); log_audit(db, user, "CREATE", "ProductionPlan", x.id, f"order={data.order_fk}"); return x

@router.patch("/coo/production-plans/{plan_id}")
def update_plan(plan_id:int, data:PlanUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER))):
    return apply_update(get_or_404(db,models.ProductionPlan,plan_id,"Plan not found"), data, db, user, "ProductionPlan")

@router.delete("/coo/production-plans/{plan_id}")
def delete_plan(plan_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER))):
    x=get_or_404(db,models.ProductionPlan,plan_id,"Plan not found"); db.delete(x); db.commit(); log_audit(db, user, "DELETE", "ProductionPlan", plan_id); return {"ok":True}

# ──────────── COO: WIP SUMMARY ────────────
@router.get("/coo/wip-summary")
def wip_summary(db:Session=Depends(get_db), user=Depends(get_current_user)):
    from sqlalchemy import func
    rows=db.query(models.ProductionMovement.process,
        func.sum(models.ProductionMovement.qty_in).label("qty_in"),
        func.sum(models.ProductionMovement.qty_done).label("qty_done"),
        func.sum(models.ProductionMovement.qty_reject).label("qty_reject")
    ).group_by(models.ProductionMovement.process).all()
    return [{"process":r.process,"qty_in":int(r.qty_in or 0),"qty_done":int(r.qty_done or 0),"qty_reject":int(r.qty_reject or 0),"wip":int((r.qty_in or 0)-(r.qty_done or 0)-(r.qty_reject or 0))} for r in rows]

# ──────────── COO: QC RECORDS ────────────
class QCIn(BaseModel):
    order_fk:int; article_code:str; process:str; total_checked:int=0; total_pass:int=0; total_reject:int=0; reject_reason:Optional[str]=None; inspector:Optional[str]=None; status:str="PASS"

class QCUpdate(BaseModel):
    total_checked:Optional[int]=None; total_pass:Optional[int]=None; total_reject:Optional[int]=None; reject_reason:Optional[str]=None; inspector:Optional[str]=None; status:Optional[str]=None

@router.get("/coo/qc-records")
def list_qc(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.QCRecord).order_by(desc(models.QCRecord.id)).all()

@router.post("/coo/qc-records")
def create_qc(data:QCIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER,models.Role.PRODUCTION_PIC))):
    x=models.QCRecord(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/coo/qc-records/{qc_id}")
def update_qc(qc_id:int, data:QCUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER))):
    return apply_update(get_or_404(db,models.QCRecord,qc_id,"QC Record not found"), data, db)

@router.delete("/coo/qc-records/{qc_id}")
def delete_qc(qc_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER))):
    x=get_or_404(db,models.QCRecord,qc_id); db.delete(x); db.commit(); return {"ok":True}

# ──────────── COO: SHIPMENTS ────────────
class ShipmentIn(BaseModel):
    order_fk:int; shipment_no:str; status:str="PREPARING"; finance_gate:str="PENDING"; ceo_approval:str="NOT_REQUIRED"; notes:Optional[str]=None

class ShipmentUpdate(BaseModel):
    status:Optional[str]=None; finance_gate:Optional[str]=None; ceo_approval:Optional[str]=None; notes:Optional[str]=None

@router.get("/coo/shipments")
def list_shipments(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Shipment).order_by(desc(models.Shipment.id)).all()

@router.post("/coo/shipments")
def create_shipment(data:ShipmentIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER,models.Role.SHIPMENT_ADMIN))):
    x=models.Shipment(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/coo/shipments/{sh_id}")
def update_shipment(sh_id:int, data:ShipmentUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER,models.Role.SHIPMENT_ADMIN))):
    return apply_update(get_or_404(db,models.Shipment,sh_id,"Shipment not found"), data, db)

# ──────────── CFO: SHIPMENT GATE ────────────
class ShipmentFinanceGateIn(BaseModel):
    action:str
    reason:Optional[str]=None

@router.post("/cfo/shipments/{shipment_id}/gate")
def cfo_shipment_gate(shipment_id:int, data:ShipmentFinanceGateIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER))):
    x=get_or_404(db,models.Shipment,shipment_id,"Shipment not found")
    if data.action not in ["APPROVE","REJECT"]:
        raise HTTPException(400,"action must be APPROVE or REJECT")
    if data.action == "APPROVE":
        x.finance_gate = "CLEAR"
    else:
        x.finance_gate = "REJECTED"
    db.commit(); db.refresh(x)
    log_audit(db, user, f"SHIPMENT_GATE_{data.action}", "Shipment", shipment_id, data.reason or "")
    return x
class ShipmentGateIn(BaseModel):
    finance_gate:str
    ceo_approval:Optional[str]=None

@router.patch("/cfo/shipments/{shipment_id}/gate")
def shipment_gate(shipment_id:int, data:ShipmentGateIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER))):
    x=get_or_404(db,models.Shipment,shipment_id,"Shipment not found")
    # Check outstanding from invoices
    from sqlalchemy import func
    total_inv = db.query(func.coalesce(func.sum(models.Invoice.amount), 0)).filter(models.Invoice.order_fk == x.order_fk).scalar() or 0
    total_paid = db.query(func.coalesce(func.sum(models.Invoice.paid_amount), 0)).filter(models.Invoice.order_fk == x.order_fk).scalar() or 0
    outstanding = float(total_inv) - float(total_paid)
    if outstanding > 0 and data.finance_gate in ["CLEAR","SHIPPED"] and data.ceo_approval!="APPROVED":
        raise HTTPException(400,f"Outstanding Rp {outstanding:,.0f} requires CEO approval")
    x.finance_gate=data.finance_gate
    if data.ceo_approval: x.ceo_approval=data.ceo_approval
    db.commit(); db.refresh(x); return x

# ──────────── CHRO: EMPLOYEES ────────────
class EmployeeIn(BaseModel):
    employee_no:str; name:str; division:Optional[str]=None; position:Optional[str]=None; employment_status:str="ACTIVE"

@router.get("/chro/employees")
def employees(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Employee).order_by(models.Employee.name).all()

@router.post("/chro/employees")
def create_employee(data:EmployeeIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER,models.Role.HR_SUPPORT))):
    x=models.Employee(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); log_audit(user, "CREATE", "Employee", x.id, x.name); return x

@router.patch("/chro/employees/{emp_id}")
def update_employee(emp_id:int, data:EmployeeIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER))):
    return apply_update(get_or_404(db,models.Employee,emp_id,"Employee not found"), data, db)

@router.delete("/chro/employees/{emp_id}")
def delete_employee(emp_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER))):
    x=get_or_404(db,models.Employee,emp_id); db.delete(x); db.commit(); return {"ok":True}

# ──────────── CHRO: TRAININGS ────────────
class TrainingIn(BaseModel):
    employee_id:int; title:str; start_date:Optional[date]=None; end_date:Optional[date]=None; result:Optional[str]=None; evaluator:Optional[str]=None

class TrainingUpdate(BaseModel):
    title:Optional[str]=None; start_date:Optional[date]=None; end_date:Optional[date]=None; result:Optional[str]=None; evaluator:Optional[str]=None

@router.get("/chro/trainings")
def trainings(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.TrainingRecord).order_by(desc(models.TrainingRecord.id)).all()

@router.post("/chro/trainings")
def create_training(data:TrainingIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER,models.Role.HR_SUPPORT))):
    x=models.TrainingRecord(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/chro/trainings/{tr_id}")
def update_training(tr_id:int, data:TrainingUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER))):
    return apply_update(get_or_404(db,models.TrainingRecord,tr_id,"Training not found"), data, db)

@router.delete("/chro/trainings/{tr_id}")
def delete_training(tr_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER))):
    x=get_or_404(db,models.TrainingRecord,tr_id); db.delete(x); db.commit(); return {"ok":True}

# ──────────── CHRO: PERFORMANCES ────────────
class PerformanceIn(BaseModel):
    employee_id:int; period:str; quality:Optional[float]=None; responsibility:Optional[float]=None; discipline:Optional[float]=None; spiritual:Optional[float]=None; attitude:Optional[float]=None; skill:Optional[float]=None; notes:Optional[str]=None

@router.get("/chro/performances")
def performances(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.PerformanceRecord).order_by(desc(models.PerformanceRecord.id)).all()

@router.post("/chro/performances")
def create_performance(data:PerformanceIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER))):
    scores=[v for v in [data.quality,data.responsibility,data.discipline,data.spiritual,data.attitude,data.skill] if v is not None]
    total=round(sum(scores)/len(scores),2) if scores else 0
    x=models.PerformanceRecord(**data.model_dump(),total_score=total); db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/chro/performances/{pr_id}")
def update_performance(pr_id:int, data:PerformanceIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER))):
    x=get_or_404(db,models.PerformanceRecord,pr_id,"Performance not found")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(x,k,v)
    scores=[v for v in [x.quality,x.responsibility,x.discipline,x.spiritual,x.attitude,x.skill] if v is not None]
    x.total_score=round(sum(scores)/len(scores),2) if scores else 0
    db.commit(); db.refresh(x); return x

# ──────────── CHRO: EMPLOYEE ISSUES ────────────
class IssueIn(BaseModel):
    employee_id:int; issue_type:str; description:str; severity:str="YELLOW"; status:str="OPEN"; reported_by:Optional[str]=None

class IssueUpdate(BaseModel):
    issue_type:Optional[str]=None; description:Optional[str]=None; severity:Optional[str]=None; status:Optional[str]=None; reported_by:Optional[str]=None

@router.get("/chro/issues")
def list_issues(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.EmployeeIssue).order_by(desc(models.EmployeeIssue.id)).all()

@router.post("/chro/issues")
def create_issue(data:IssueIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER,models.Role.HR_SUPPORT))):
    x=models.EmployeeIssue(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); log_audit(user, "CREATE", "EmployeeIssue", x.id, x.issue_type); return x

@router.patch("/chro/issues/{iss_id}")
def update_issue(iss_id:int, data:IssueUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER))):
    return apply_update(get_or_404(db,models.EmployeeIssue,iss_id,"Issue not found"), data, db)

@router.delete("/chro/issues/{iss_id}")
def delete_issue(iss_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER))):
    x=get_or_404(db,models.EmployeeIssue,iss_id); info=x.issue_type; db.delete(x); db.commit(); log_audit(user, "DELETE", "EmployeeIssue", iss_id, info); return {"ok":True}

# ──────────── CEO: DECISIONS ────────────
class DecisionIn(BaseModel):
    order_fk:Optional[int]=None; decision_type:str; subject:str; decision:Optional[str]=None; reason:Optional[str]=None; owner_name:Optional[str]=None; due_date:Optional[date]=None

class DecisionUpdate(BaseModel):
    decision_type:Optional[str]=None; subject:Optional[str]=None; decision:Optional[str]=None; reason:Optional[str]=None; owner_name:Optional[str]=None; due_date:Optional[date]=None; action_status:Optional[str]=None

@router.get("/ceo/decisions")
def decisions(db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    return db.query(models.CEODecision).order_by(desc(models.CEODecision.id)).all()

@router.post("/ceo/decisions")
def create_decision(data:DecisionIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    x=models.CEODecision(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); log_audit(user, "CREATE", "CEODecision", x.id, x.subject); return x

@router.patch("/ceo/decisions/{dec_id}")
def update_decision(dec_id:int, data:DecisionUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    return apply_update(get_or_404(db,models.CEODecision,dec_id,"Decision not found"), data, db)

@router.delete("/ceo/decisions/{dec_id}")
def delete_decision(dec_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    x=get_or_404(db,models.CEODecision,dec_id); info=x.subject; db.delete(x); db.commit(); log_audit(user, "DELETE", "CEODecision", dec_id, info); return {"ok":True}

# ──────────── EXCEPTIONS ────────────
class ExceptionIn(BaseModel):
    order_fk:Optional[int]=None; severity:str="YELLOW"; category:str; title:str; owner_role:Optional[str]=None; owner_name:Optional[str]=None; due_date:Optional[date]=None; next_action:Optional[str]=None

class ExceptionUpdate(BaseModel):
    severity:Optional[str]=None; category:Optional[str]=None; title:Optional[str]=None; owner_role:Optional[str]=None; owner_name:Optional[str]=None; due_date:Optional[date]=None; next_action:Optional[str]=None; status:Optional[str]=None

@router.get("/exceptions")
def list_exceptions(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.ExceptionItem).order_by(desc(models.ExceptionItem.id)).all()

@router.post("/exceptions")
def create_exception(data:ExceptionIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER,models.Role.COO_MANAGER,models.Role.CEO,models.Role.CMO_SUPPORT))):
    x=models.ExceptionItem(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); log_audit(user, "CREATE", "ExceptionItem", x.id, x.title); return x

@router.patch("/exceptions/{exc_id}")
def update_exception(exc_id:int, data:ExceptionUpdate, db:Session=Depends(get_db), user=Depends(get_current_user)):
    return apply_update(get_or_404(db,models.ExceptionItem,exc_id,"Exception not found"), data, db)

@router.delete("/exceptions/{exc_id}")
def delete_exception(exc_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    x=get_or_404(db,models.ExceptionItem,exc_id); info=x.title; db.delete(x); db.commit(); log_audit(user, "DELETE", "ExceptionItem", exc_id, info); return {"ok":True}

# ──────────── TASKS ────────────
class TaskIn(BaseModel):
    title:str; assigned_to_id:Optional[int]=None; order_fk:Optional[int]=None; due_date:Optional[date]=None

class TaskUpdate(BaseModel):
    title:Optional[str]=None; assigned_to_id:Optional[int]=None; order_fk:Optional[int]=None; due_date:Optional[date]=None; status:Optional[str]=None

@router.get("/tasks")
def list_tasks(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Task).order_by(desc(models.Task.id)).all()

@router.post("/tasks")
def create_task(data:TaskIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER,models.Role.COO_MANAGER,models.Role.CEO,models.Role.CMO_SUPPORT))):
    x=models.Task(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); log_audit(user, "CREATE", "Task", x.id, x.title); return x

@router.patch("/tasks/{task_id}")
def update_task(task_id:int, data:TaskUpdate, db:Session=Depends(get_db), user=Depends(get_current_user)):
    return apply_update(get_or_404(db,models.Task,task_id,"Task not found"), data, db)

@router.delete("/tasks/{task_id}")
def delete_task(task_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    x=get_or_404(db,models.Task,task_id); info=x.title; db.delete(x); db.commit(); log_audit(user, "DELETE", "Task", task_id, info); return {"ok":True}

# ──────────── USERS ────────────
@router.get("/users")
def list_users(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return [{"id":u.id,"name":u.name,"role":u.role.value} for u in db.query(models.User).filter(models.User.is_active==True).order_by(models.User.name).all()]

# ──────────── AUDIT LOG ────────────
@router.get("/audit-log")
def list_audit_log(db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    logs = db.query(models.AuditLog).order_by(desc(models.AuditLog.id)).limit(100).all()
    result = []
    for l in logs:
        u = db.query(models.User).get(l.user_id) if l.user_id else None
        result.append({
            "id": l.id, "user": u.name if u else "-", "action": l.action,
            "entity": l.entity, "entity_id": l.entity_id, "detail": l.detail,
            "created_at": l.created_at,
        })
    return result


# ──────────── CEO: SHIPMENT APPROVAL ────────────
class ShipmentApprovalIn(BaseModel):
    action:str
    reason:Optional[str]=None

@router.post("/ceo/shipments/{shipment_id}/approve-shipment")
def ceo_approve_shipment(shipment_id:int, data:ShipmentApprovalIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    x=get_or_404(db,models.Shipment,shipment_id,"Shipment not found")
    if data.action not in ["APPROVE","REJECT"]:
        raise HTTPException(400,"action must be APPROVE or REJECT")
    if data.action == "APPROVE":
        x.ceo_approval = "APPROVED"
    else:
        x.ceo_approval = "REJECTED"
    db.commit(); db.refresh(x)
    log_audit(db, user, f"CEO_SHIPMENT_{data.action}", "Shipment", shipment_id, data.reason or "")
    return x

# ──────────── COO: DELIVERY CONFIRMATIONS ────────────
class DeliveryConfirmIn(BaseModel):
    shipment_fk:int; confirmed_by_customer:Optional[str]=None; confirmation_date:Optional[date]=None; feedback:Optional[str]=None; status:str="PENDING"

class DeliveryConfirmUpdate(BaseModel):
    confirmed_by_customer:Optional[str]=None; confirmation_date:Optional[date]=None; feedback:Optional[str]=None; status:Optional[str]=None

@router.get("/coo/deliveries")
def list_deliveries(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.DeliveryConfirmation).order_by(desc(models.DeliveryConfirmation.id)).all()

@router.post("/coo/deliveries")
def create_delivery_confirmation(data:DeliveryConfirmIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER,models.Role.SHIPMENT_ADMIN))):
    x=models.DeliveryConfirmation(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); log_audit(db, user, "CREATE", "DeliveryConfirmation", x.id, f"shipment={data.shipment_fk}"); return x

@router.patch("/coo/deliveries/{del_id}")
def update_delivery_confirmation(del_id:int, data:DeliveryConfirmUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER,models.Role.SHIPMENT_ADMIN))):
    return apply_update(get_or_404(db,models.DeliveryConfirmation,del_id,"Delivery not found"), data, db, user, "DeliveryConfirmation")

# ──────────── COO: ORDER CLOSING ────────────
class OrderClosingIn(BaseModel):
    order_fk:int; customer_close_status:str="OPEN"; financial_close_status:str="OPEN"; order_close_status:str="OPEN"; close_date:Optional[date]=None; notes:Optional[str]=None

class OrderClosingUpdate(BaseModel):
    customer_close_status:Optional[str]=None; financial_close_status:Optional[str]=None; order_close_status:Optional[str]=None; close_date:Optional[date]=None; notes:Optional[str]=None

@router.get("/coo/order-closing/{order_id}")
def get_order_closing(order_id:int, db:Session=Depends(get_db), user=Depends(get_current_user)):
    rec = db.query(models.OrderClosing).filter(models.OrderClosing.order_fk==order_id).order_by(desc(models.OrderClosing.id)).first()
    if not rec: raise HTTPException(404,"No closing record for this order")
    return rec

@router.post("/coo/order-closing/{order_id}")
def create_order_closing(order_id:int, data:OrderClosingIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER))):
    data.order_fk = order_id
    x=models.OrderClosing(**data.model_dump(), closed_by=user.name); db.add(x); db.commit(); db.refresh(x)
    log_audit(db, user, "CREATE", "OrderClosing", x.id, f"order={order_id}")
    return x

@router.patch("/coo/order-closing/{order_id}")
def update_order_closing(order_id:int, data:OrderClosingUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER))):
    rec = db.query(models.OrderClosing).filter(models.OrderClosing.order_fk==order_id).order_by(desc(models.OrderClosing.id)).first()
    if not rec: raise HTTPException(404,"No closing record for this order")
    return apply_update(rec, data, db, user, "OrderClosing")

# ──────────── COO: RELEASE TO PURCHASING ────────────
@router.post("/coo/release-to-purchasing/{material_request_id}")
def release_to_purchasing(material_request_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER))):
    mr = get_or_404(db,models.MaterialRequest,material_request_id,"Material request not found")
    if mr.status not in ("REQUESTED","APPROVED"):
        raise HTTPException(400,"Material request must be REQUESTED or APPROVED")
    po_no = f"PO-{mr.id:05d}"
    po = models.PurchaseOrder(
        po_no=po_no, order_fk=mr.order_fk, item=mr.item_name,
        qty=mr.qty, unit=mr.unit, amount=0, status="PENDING"
    )
    db.add(po)
    mr.status = "ORDERED"
    db.commit(); db.refresh(po)
    log_audit(db, user, "RELEASE_TO_PURCHASING", "MaterialRequest", mr.id, f"created PO={po_no}")
    return {"ok":True, "po_id":po.id, "po_no":po_no}

# ──────────── CFO: OUTSTANDING CALCULATION ────────────
@router.get("/cfo/outstanding-summary")
def outstanding_summary(db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER,models.Role.CEO))):
    from sqlalchemy import func
    rows = db.query(
        models.Invoice.order_fk,
        func.sum(models.Invoice.amount).label("total_amount"),
        func.sum(models.Invoice.paid_amount).label("total_paid"),
    ).group_by(models.Invoice.order_fk).all()
    result = []
    for r in rows:
        order = db.query(models.Order).get(r.order_fk) if r.order_fk else None
        outstanding = float(r.total_amount or 0) - float(r.total_paid or 0)
        result.append({
            "order_id": order.order_id if order else "-",
            "buyer": order.buyer if order else "-",
            "total_amount": float(r.total_amount or 0),
            "total_paid": float(r.total_paid or 0),
            "outstanding": outstanding,
        })
    return result
