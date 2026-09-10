
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..auth import get_current_user
from .. import models

router = APIRouter(tags=["dashboards"])

def count(db, model):
    return db.query(func.count(model.id)).scalar() or 0

@router.get("/dashboard/{module}")
def dashboard(module: str, db: Session=Depends(get_db), user=Depends(get_current_user)):
    m = module.upper()
    if m == "CMO":
        return {
            "module":"CMO",
            "cards":[
                {"label":"Total Order","value":count(db,models.Order)},
                {"label":"Customer","value":count(db,models.Customer)},
                {"label":"Quotation","value":count(db,models.Quotation)},
                {"label":"Sample/PPM","value":count(db,models.SampleRecord)},
                {"label":"SPK","value":count(db,models.SPK)},
            ],
            "flows":["Sales Pipeline","Buyer CRM","Quotation","Order Management","Sample / PPM","SPK","Demand Gap","Content & Ads","Customer Communication"]
        }
    if m == "CFO":
        outstanding = db.query(func.coalesce(func.sum(models.Invoice.amount-models.Invoice.paid_amount),0)).scalar()
        return {
            "module":"CFO",
            "cards":[
                {"label":"Invoice","value":count(db,models.Invoice)},
                {"label":"Outstanding","value":float(outstanding or 0)},
                {"label":"Purchase Order","value":count(db,models.PurchaseOrder)},
                {"label":"Material Request","value":count(db,models.MaterialRequest)},
            ],
            "flows":["Pricing & HPP","Invoice & Payment","AR/AP","Purchasing","Operational Cost","Attendance","Payroll & Team Bonus","Accounting","Cash Planning","Shipment Finance Gate","Financial Closing"]
        }
    if m == "COO":
        return {
            "module":"COO",
            "cards":[
                {"label":"SPK","value":count(db,models.SPK)},
                {"label":"Material Request","value":count(db,models.MaterialRequest)},
                {"label":"WIP Records","value":count(db,models.ProductionMovement)},
                {"label":"QC Records","value":count(db,models.QCRecord)},
                {"label":"Shipment","value":count(db,models.Shipment)},
            ],
            "flows":["Sample Process","SPK Queue","Production Planning","Material Gate","Production Queue","WIP","QC & Rework","Packing","Ready to Ship"]
        }
    if m == "CHRO":
        return {
            "module":"CHRO",
            "cards":[
                {"label":"Employee","value":count(db,models.Employee)},
                {"label":"Training","value":count(db,models.TrainingRecord)},
                {"label":"Performance","value":count(db,models.PerformanceRecord)},
                {"label":"People Issue","value":count(db,models.EmployeeIssue)},
            ],
            "flows":["Manpower Planning","Recruitment","Onboarding & Training","Placement","Employee Master","Skill Matrix","Performance","Employee Issue & Discipline"]
        }
    if m == "CEO":
        reds = db.query(func.count(models.ExceptionItem.id)).filter(models.ExceptionItem.severity=="RED", models.ExceptionItem.status=="OPEN").scalar() or 0
        return {
            "module":"CEO",
            "cards":[
                {"label":"Order Aktif","value":db.query(func.count(models.Order.id)).filter(models.Order.overall_status!="CLOSED").scalar() or 0},
                {"label":"Critical Issue","value":reds},
                {"label":"Decision / Action","value":db.query(func.count(models.CEODecision.id)).filter(models.CEODecision.action_status!="CLOSED").scalar() or 0},
                {"label":"Customer","value":count(db,models.Customer)},
            ],
            "flows":["Company Health","Decision Needed","Cash & Collection","Production Today","Sales Opportunity","People Issue","CEO Action Tracker"]
        }
    if m == "TASK":
        open_tasks = db.query(func.count(models.Task.id)).filter(models.Task.status=="OPEN").scalar() or 0
        return {"module":"TASK","cards":[
            {"label":"Open Tasks","value":open_tasks},
            {"label":"Total Tasks","value":count(db,models.Task)},
        ],"flows":["My Task","Update Progress","Exception / Note","History"]}
    if m == "EXCEPTION":
        reds = db.query(func.count(models.ExceptionItem.id)).filter(models.ExceptionItem.severity=="RED",models.ExceptionItem.status=="OPEN").scalar() or 0
        yellows = db.query(func.count(models.ExceptionItem.id)).filter(models.ExceptionItem.severity=="YELLOW",models.ExceptionItem.status=="OPEN").scalar() or 0
        return {"module":"EXCEPTION","cards":[
            {"label":"RED Open","value":reds},
            {"label":"YELLOW Open","value":yellows},
            {"label":"Total Exception","value":count(db,models.ExceptionItem)},
        ],"flows":["Identify Issue","Assign Owner","Action Required","Resolve & Close"]}
    if m in ["SAMPLE","PRINTING","PRODUCTION","SHIPMENT"]:
        return {"module":m,"cards":[],"flows":["My Task","Update Progress","Exception / Note","History"]}
    raise HTTPException(404,"Unknown module")

@router.get("/users")
def list_users(db:Session=Depends(get_db), user=Depends(get_current_user)):
    return [{"id":u.id,"name":u.name,"role":u.role.value} for u in db.query(models.User).filter(models.User.is_active==True).order_by(models.User.name).all()]
