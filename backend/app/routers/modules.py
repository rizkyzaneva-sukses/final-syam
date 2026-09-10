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
    x=db.query(models.Customer).filter(models.Customer.id==customer_id).first()
    if not x: raise HTTPException(404,"Customer not found")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(x,k,v)
    db.commit(); db.refresh(x); return x

@router.delete("/cmo/customers/{customer_id}")
def delete_customer(customer_id:int, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER))):
    x=db.query(models.Customer).filter(models.Customer.id==customer_id).first()
    if not x: raise HTTPException(404,"Customer not found")
    db.delete(x); db.commit(); return {"ok":True}

class OrderUpdate(BaseModel):
    buyer:Optional[str]=None; order_type:Optional[str]=None; buyer_deadline:Optional[date]=None
    finance_status:Optional[str]=None; material_status:Optional[str]=None; shipment_status:Optional[str]=None
    overall_status:Optional[str]=None; projected_shipment:Optional[date]=None; buffer_days:Optional[int]=None; notes:Optional[str]=None

@router.patch("/orders/{order_id}")
def update_order(order_id:str, data:OrderUpdate, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CMO_MANAGER,models.Role.CMO_SUPPORT,models.Role.COO_MANAGER))):
    x=db.query(models.Order).filter(models.Order.order_id==order_id).first()
    if not x: raise HTTPException(404,"Order not found")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(x,k,v)
    db.commit(); db.refresh(x); return x

class MaterialIn(BaseModel):
    order_fk:int; item_name:str; qty:float; unit:Optional[str]=None; required_date:Optional[date]=None

@router.get("/coo/material-requests")
def material_requests(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.MaterialRequest).order_by(desc(models.MaterialRequest.id)).all()

@router.post("/coo/material-requests")
def create_material_request(data:MaterialIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER,models.Role.PRODUCTION_PIC))):
    x=models.MaterialRequest(**data.model_dump(),requested_by=user.name); db.add(x); db.commit(); db.refresh(x); return x

class MovementIn(BaseModel):
    article_id:int; process:str; qty_in:int=0; qty_done:int=0; qty_reject:int=0; status:str="IN_PROCESS"; pic_name:Optional[str]=None

@router.post("/coo/movements")
def create_movement(data:MovementIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.COO_MANAGER,models.Role.PRODUCTION_PIC,models.Role.PRINTING_PIC,models.Role.SAMPLE_PIC))):
    if data.qty_done > data.qty_in: raise HTTPException(400,"qty_done cannot exceed qty_in")
    x=models.ProductionMovement(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

class InvoiceIn(BaseModel):
    invoice_no:str; order_fk:int; amount:float; due_date:Optional[date]=None

@router.get("/cfo/invoices")
def invoices(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Invoice).order_by(desc(models.Invoice.id)).all()

@router.post("/cfo/invoices")
def create_invoice(data:InvoiceIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER,models.Role.FINANCE_SUPPORT))):
    x=models.Invoice(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

class EmployeeIn(BaseModel):
    employee_no:str; name:str; division:Optional[str]=None; position:Optional[str]=None

@router.get("/chro/employees")
def employees(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Employee).order_by(models.Employee.name).all()

@router.post("/chro/employees")
def create_employee(data:EmployeeIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CHRO_MANAGER,models.Role.HR_SUPPORT))):
    x=models.Employee(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

class DecisionIn(BaseModel):
    order_fk:Optional[int]=None; decision_type:str; subject:str; decision:Optional[str]=None; reason:Optional[str]=None; owner_name:Optional[str]=None; due_date:Optional[date]=None

@router.get("/ceo/decisions")
def decisions(db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    return db.query(models.CEODecision).order_by(desc(models.CEODecision.id)).all()

@router.post("/ceo/decisions")
def create_decision(data:DecisionIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CEO))):
    x=models.CEODecision(**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x

class ShipmentGateIn(BaseModel):
    finance_gate:str
    ceo_approval:Optional[str]=None

@router.patch("/cfo/shipments/{shipment_id}/gate")
def shipment_gate(shipment_id:int, data:ShipmentGateIn, db:Session=Depends(get_db), user=Depends(require_roles(models.Role.CFO_MANAGER))):
    x=db.query(models.Shipment).filter(models.Shipment.id==shipment_id).first()
    if not x: raise HTTPException(404,"Shipment not found")
    if float(x.outstanding_amount or 0) > 0 and data.finance_gate in ["CLEAR","SHIPPED"] and data.ceo_approval!="APPROVED":
        raise HTTPException(400,"Outstanding shipment requires CEO approval")
    x.finance_gate=data.finance_gate
    if data.ceo_approval: x.ceo_approval=data.ceo_approval
    db.commit(); db.refresh(x); return x
