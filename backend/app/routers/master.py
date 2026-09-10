from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Order, ExceptionItem, CapacitySnapshot, ProductionMovement, Article, User
from ..auth import get_current_user

router = APIRouter(prefix="/master", tags=["master"])

@router.get("/summary")
def summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    critical = db.query(ExceptionItem).filter(ExceptionItem.status=="OPEN", ExceptionItem.severity=="RED").count()
    attention = db.query(ExceptionItem).filter(ExceptionItem.status=="OPEN", ExceptionItem.severity=="YELLOW").count()
    active = db.query(Order).filter(Order.overall_status.in_(["NEW","ACTIVE","HOLD"])).count()
    waiting = db.query(Order).filter(Order.overall_status=="NEW").count()
    on_track = db.query(Order).filter(Order.buffer_days != None, Order.buffer_days >= 0, Order.overall_status != "CLOSED").count()
    return {"active_orders": active, "critical": critical, "attention": attention, "on_track": on_track, "waiting": waiting}

@router.get("/morning-priority")
def morning_priority(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(ExceptionItem, Order).outerjoin(Order, ExceptionItem.order_fk == Order.id).filter(ExceptionItem.status=="OPEN").order_by(ExceptionItem.severity.desc(), ExceptionItem.due_date.asc().nullslast()).all()
    return [{"id": e.id, "order_id": o.order_id if o else None, "severity": e.severity, "title": e.title, "owner": e.owner_name or e.owner_role, "due_date": e.due_date, "next_action": e.next_action} for e,o in items]

@router.get("/wip-capacity")
def wip_capacity(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(CapacitySnapshot).filter(CapacitySnapshot.snapshot_date==date.today()).all()
    return [{"process":r.process,"capacity":r.capacity,"planned_load":r.planned_load,"current_wip":r.current_wip,"utilization":round((r.planned_load/r.capacity)*100,1) if r.capacity else 0} for r in rows]

@router.get("/forecast")
def forecast(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Order).filter(Order.overall_status != "CLOSED").all()
    out=[]
    for o in rows:
        status = "ON_TRACK" if (o.buffer_days or 0) >= 1 else "AT_RISK" if (o.buffer_days or 0) >= -2 else "LATE_RISK"
        out.append({"order_id":o.order_id,"buyer":o.buyer,"deadline":o.buyer_deadline,"projected_shipment":o.projected_shipment,"buffer_days":o.buffer_days,"status":status})
    return out

@router.get("/process-movement/{order_id}")
def process_movement(order_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.order_id==order_id).first()
    if not order:
        return []
    article_ids = [a.id for a in db.query(Article).filter(Article.order_fk==order.id).all()]
    rows = db.query(ProductionMovement).filter(ProductionMovement.article_id.in_(article_ids)).order_by(ProductionMovement.id.asc()).all() if article_ids else []
    return [{"process":r.process,"qty_in":r.qty_in,"qty_done":r.qty_done,"wip":max(r.qty_in-r.qty_done,0),"qty_reject":r.qty_reject,"status":r.status,"pic":r.pic_name,"target_date":r.target_date} for r in rows]
