from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional
from datetime import date
from ..database import get_db
from ..auth import get_current_user, require_roles
from .. import models

router = APIRouter(tags=["modules"])

# ──────────── HELPERS ────────────
def get_or_404(db, model, id, label="Not found"):
    x = db.query(model).filter(model.id == id).first()
    if not x: raise HTTPException(404, label)
    return x

def apply_update(obj, data, db):
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return obj

# ──────────── CMO: CUSTOMERS ────────────
class CustomerIn(BaseModel):
    name:str; country:Optional[str]=None; contact_name:Optional[str]=None; contact_info:Optional[str]=None; notes:Optional[str]=None

@router.get("/cmo/customers")
def customers(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Customer).order_by(models.Customer.name).all()

@router.post("/cmo/customers")
def create_customer(data:CustomerIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER,models.Role.CMO_SUPPORT))):
    x=models.Customer(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

class CustomerUpdate(BaseModel):
    name:Optional[str]=None; country:Optional[str]=None; contact_name:Optional[str]=None; contact_info:Optional[str]=None; notes:Optional[str]=None

@router.patch("/cmo/customers/{customer_id}")
def update_customer(customer_id:int, data:CustomerUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER,models.Role.CMO_SUPPORT))):
    return apply_update(get_or_404(db,models.Customer,customer_id,"Customer not found"), data, db)

@router.delete("/cmo/customers/{customer_id}")
def delete_customer(customer_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER))):
    x=get_or_404(db,models.Customer,customer_id,"Customer not found"); db.delete(x); db.commit(); return {"ok":True}

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
    x=models.SPK(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/cmo/spk/{spk_id}")
def update_spk(spk_id:int, data:SPKUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER))):
    return apply_update(get_or_404(db,models.SPK,spk_id,"SPK not found"), data, db)

@router.delete("/cmo/spk/{spk_id}")
def delete_spk(spk_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER))):
    x=get_or_404(db,models.SPK,spk_id); db.delete(x); db.commit(); return {"ok":True}

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
    x=models.Invoice(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/cfo/invoices/{inv_id}")
def update_invoice(inv_id:int, data:InvoiceUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER))):
    return apply_update(get_or_404(db,models.Invoice,inv_id,"Invoice not found"), data, db)

@router.delete("/cfo/invoices/{inv_id}")
def delete_invoice(inv_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER))):
    x=get_or_404(db,models.Invoice,inv_id); db.delete(x); db.commit(); return {"ok":True}

# ──────────── CFO: PURCHASE ORDERS ────────────
class POIn(BaseModel):
    po_no:str; order_fk:Optional[int]=None; item:str; qty:float; unit:Optional[str]=None; supplier:Optional[str]=None; amount:Optional[float]=0; status:str="PENDING"

class POUpdate(BaseModel):
    item:Optional[str]=None; qty:Optional[float]=None; unit:Optional[str]=None; supplier:Optional[str]=None; amount:Optional[float]=None; status:Optional[str]=None

@router.get("/cfo/purchase-orders")
def list_pos(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.PurchaseOrder).order_by(desc(models.PurchaseOrder.id)).all()

@router.post("/cfo/purchase-orders")
def create_po(data:POIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER,models.Role.FINANCE_SUPPORT))):
    x=models.PurchaseOrder(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/cfo/purchase-orders/{po_id}")
def update_po(po_id:int, data:POUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER))):
    return apply_update(get_or_404(db,models.PurchaseOrder,po_id,"PO not found"), data, db)

@router.delete("/cfo/purchase-orders/{po_id}")
def delete_po(po_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER))):
    x=get_or_404(db,models.PurchaseOrder,po_id); db.delete(x); db.commit(); return {"ok":True}

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

@router.post("/coo/movements")
def create_movement(data:MovementIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER,models.Role.PRODUCTION_PIC,models.Role.PRINTING_PIC,models.Role.SAMPLE_PIC))):
    if data.qty_done > data.qty_in: raise HTTPException(400,"qty_done cannot exceed qty_in")
    x=models.ProductionMovement(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.get("/coo/movements")
def list_movements(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.ProductionMovement).order_by(desc(models.ProductionMovement.id)).all()

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
class ShipmentGateIn(BaseModel):
    finance_gate:str
    ceo_approval:Optional[str]=None

@router.patch("/cfo/shipments/{shipment_id}/gate")
def shipment_gate(shipment_id:int, data:ShipmentGateIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER))):
    x=get_or_404(db,models.Shipment,shipment_id,"Shipment not found")
    if float(x.outstanding_amount or 0) > 0 and data.finance_gate in ["CLEAR","SHIPPED"] and data.ceo_approval!="APPROVED":
        raise HTTPException(400,"Outstanding shipment requires CEO approval")
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
    x=models.Employee(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

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
    x=models.EmployeeIssue(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/chro/issues/{iss_id}")
def update_issue(iss_id:int, data:IssueUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER))):
    return apply_update(get_or_404(db,models.EmployeeIssue,iss_id,"Issue not found"), data, db)

@router.delete("/chro/issues/{iss_id}")
def delete_issue(iss_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER))):
    x=get_or_404(db,models.EmployeeIssue,iss_id); db.delete(x); db.commit(); return {"ok":True}

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
    x=models.CEODecision(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/ceo/decisions/{dec_id}")
def update_decision(dec_id:int, data:DecisionUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    return apply_update(get_or_404(db,models.CEODecision,dec_id,"Decision not found"), data, db)

@router.delete("/ceo/decisions/{dec_id}")
def delete_decision(dec_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    x=get_or_404(db,models.CEODecision,dec_id); db.delete(x); db.commit(); return {"ok":True}

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
    x=models.ExceptionItem(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/exceptions/{exc_id}")
def update_exception(exc_id:int, data:ExceptionUpdate, db:Session=Depends(get_db), user=Depends(get_current_user)):
    return apply_update(get_or_404(db,models.ExceptionItem,exc_id,"Exception not found"), data, db)

@router.delete("/exceptions/{exc_id}")
def delete_exception(exc_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    x=get_or_404(db,models.ExceptionItem,exc_id); db.delete(x); db.commit(); return {"ok":True}

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
    x=models.Task(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

@router.patch("/tasks/{task_id}")
def update_task(task_id:int, data:TaskUpdate, db:Session=Depends(get_db), user=Depends(get_current_user)):
    return apply_update(get_or_404(db,models.Task,task_id,"Task not found"), data, db)

@router.delete("/tasks/{task_id}")
def delete_task(task_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    x=get_or_404(db,models.Task,task_id); db.delete(x); db.commit(); return {"ok":True}

# ──────────── USERS ────────────
@router.get("/users")
def list_users(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return [{"id":u.id,"name":u.name,"role":u.role.value} for u in db.query(models.User).filter(models.User.is_active==True).order_by(models.User.name).all()]
