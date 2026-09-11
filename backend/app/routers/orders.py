from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Order, Article, Role, User
from ..schemas import OrderCreate, OrderOut
from ..auth import get_current_user, require_roles

router = APIRouter(prefix="/orders", tags=["orders"])

@router.get("", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Order).options(joinedload(Order.articles)).order_by(Order.buyer_deadline.asc().nullslast()).all()

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = db.query(Order).options(joinedload(Order.articles)).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("", response_model=OrderOut)
def create_order(payload: OrderCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.CMO_MANAGER, Role.CMO_SUPPORT))):
    # Generate SO-XXX format based on max existing SO-* orders
    from sqlalchemy import func
    max_so = db.query(func.max(Order.order_id)).filter(Order.order_id.like("SO-%")).scalar()
    if max_so:
        try:
            next_num = int(max_so[3:]) + 1
        except ValueError:
            next_num = db.query(Order).count() + 1
    else:
        next_num = 1
    oid = f"SO-{next_num:03d}"
    order = Order(order_id=oid, buyer=payload.buyer, order_type=payload.order_type, buyer_deadline=payload.buyer_deadline, notes=payload.notes, created_by_id=user.id)
    for a in payload.articles:
        order.articles.append(Article(**a.model_dump(), sample_status="PROCESS" if a.sample_required else "NOT_REQUIRED"))
    db.add(order); db.commit(); db.refresh(order)
    return order
