from datetime import date, timedelta
from sqlalchemy.orm import Session
from ..auth import hash_password
from ..models import User, Role, Order, OrderType, Article, ProductionMovement, ExceptionItem, CapacitySnapshot, Task

DEMO_PASSWORD = "demo123"

def seed(db: Session):
    if db.query(User).count() > 0:
        return
    users = [
        User(name="Iyan", email="iyan@syams.local", role=Role.CEO, password_hash=hash_password(DEMO_PASSWORD)),
        User(name="Cecep", email="cecep@syams.local", role=Role.CMO_MANAGER, password_hash=hash_password(DEMO_PASSWORD)),
        User(name="Deby", email="deby@syams.local", role=Role.CMO_SUPPORT, password_hash=hash_password(DEMO_PASSWORD)),
        User(name="Lutfi", email="lutfi@syams.local", role=Role.CFO_MANAGER, password_hash=hash_password(DEMO_PASSWORD)),
        User(name="Siti", email="siti@syams.local", role=Role.COO_MANAGER, password_hash=hash_password(DEMO_PASSWORD)),
        User(name="Fahrul", email="fahrul@syams.local", role=Role.SAMPLE_PIC, password_hash=hash_password(DEMO_PASSWORD)),
        User(name="Iman", email="iman@syams.local", role=Role.PRINTING_PIC, password_hash=hash_password(DEMO_PASSWORD)),
        User(name="Yuni", email="yuni@syams.local", role=Role.CHRO_MANAGER, password_hash=hash_password(DEMO_PASSWORD)),
    ]
    db.add_all(users); db.flush()
    today = date.today()
    o1 = Order(order_id="SO-001", buyer="FRAMSTER", order_type=OrderType.SAMPLE_PRODUCTION, buyer_deadline=today+timedelta(days=7), finance_status="PAID", material_status="READY", shipment_status="NOT_READY", overall_status="ACTIVE", projected_shipment=today+timedelta(days=5), buffer_days=2, created_by_id=users[1].id)
    a1 = Article(order=o1, article_code="HD-CLASSIC", garment_type="Hoodie", qty=200, sample_required=True, sample_status="APPROVED", production_route="Cutting>Sortir>Printing>Sewing>Accessories>QC>Packing", production_status="IN_PROCESS")
    o2 = Order(order_id="SO-014", buyer="MADRID CO", order_type=OrderType.REPEAT_PRODUCTION, buyer_deadline=today+timedelta(days=3), finance_status="PARTIAL", material_status="DELAYED", shipment_status="NOT_READY", overall_status="HOLD", projected_shipment=today+timedelta(days=7), buffer_days=-4, created_by_id=users[1].id)
    a2 = Article(order=o2, article_code="JK-014", garment_type="Jacket", qty=300, sample_required=False, sample_status="NOT_REQUIRED", production_route="Cutting>Sortir>Bordir>Sewing>Accessories>QC>Packing", production_status="WAITING_MATERIAL")
    db.add_all([o1,o2]); db.flush()
    for process, qin, qdone, status, pic in [
        ("Cutting",200,200,"DONE","Siti"),("Sortir",200,200,"DONE","Siti"),("Printing",200,150,"IN_PROCESS","Iman"),("Sewing",150,80,"IN_PROCESS","Siti"),("Accessories",0,0,"WAITING","Siti"),("QC",0,0,"WAITING","Siti"),("Packing",0,0,"WAITING","Siti")]:
        db.add(ProductionMovement(article_id=a1.id, process=process, qty_in=qin, qty_done=qdone, status=status, pic_name=pic, target_date=today))
    db.add_all([
        ExceptionItem(order_fk=o2.id, severity="RED", category="MATERIAL", title="Material terlambat", owner_role="CFO_MANAGER", owner_name="Lutfi", due_date=today, next_action="Follow-up supplier"),
        ExceptionItem(order_fk=o1.id, severity="YELLOW", category="PRODUCTION", title="Printing tersisa 50 pcs", owner_role="PRINTING_PIC", owner_name="Iman", due_date=today, next_action="Selesaikan target hari ini"),
    ])
    for p,c,l,w in [("Cutting",1500,1200,200),("Printing",1500,2100,620),("Sewing",2000,1800,450),("Accessories",800,600,150),("QC",1000,700,100),("Packing",1000,600,120)]:
        db.add(CapacitySnapshot(snapshot_date=today, process=p, capacity=c, planned_load=l, current_wip=w))
    db.add(Task(title="Follow-up material SO-014", assigned_to_id=users[3].id, order_fk=o2.id, due_date=today))
    db.commit()
