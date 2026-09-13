from datetime import date, timedelta
from sqlalchemy.orm import Session
from ..auth import hash_password
from ..config import settings
from ..models import (User, Role, Order, OrderType, Article, ProductionMovement,
    ExceptionItem, CapacitySnapshot, Task, Customer, Employee, Invoice, Quotation,
    SampleRecord, SPK, QCRecord, Shipment, PurchaseOrder, Payment, EmployeeIssue,
    CEODecision, TrainingRecord, PerformanceRecord, ProductionPlan, DeliveryConfirmation, OrderClosing)

DEMO_PASSWORD="demo123"

def seed(db: Session):
    if settings.app_env != "development" or not settings.seed_demo:
        raise RuntimeError("Demo seed requires APP_ENV=development and SEED_DEMO=true")
    if db.query(User).count() > 0:
        return

    # --- USERS (8 roles) ---
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

    # --- CUSTOMERS ---
    c1 = Customer(name="FRAMSTER", country="US", contact_name="John Smith", contact_info="+1-555-0101", notes="Regular buyer, hoodie specialist")
    c2 = Customer(name="MADRID CO", country="ES", contact_name="Carlos Garcia", contact_info="+34-600-2002", notes="Jacket orders, high quality requirement")
    c3 = Customer(name="TOKYO STYLE", country="JP", contact_name="Yuki Tanaka", contact_info="+81-90-3003", notes="Streetwear, quick turnaround")
    c4 = Customer(name="BERLIN WEAR", country="DE", contact_name="Hans Mueller", contact_info="+49-170-4004", notes="Eco fabric focus")
    c5 = Customer(name="SEOUL FASHION", country="KR", contact_name="Kim Soo-jin", contact_info="+82-10-5005", notes="Korean wave trends")
    db.add_all([c1,c2,c3,c4,c5]); db.flush()

    # --- ORDERS + ARTICLES ---
    o1 = Order(order_id="SO-001", buyer="FRAMSTER", order_type=OrderType.SAMPLE_PRODUCTION, buyer_deadline=today+timedelta(days=7), finance_status="PAID", material_status="READY", shipment_status="NOT_READY", overall_status="ACTIVE", flow_step="SAMPLE_APPROVED", projected_shipment=today+timedelta(days=5), buffer_days=2, created_by_id=users[1].id)
    a1 = Article(order=o1, article_code="HD-CLASSIC", garment_type="Hoodie", qty=200, sample_required=True, sample_status="APPROVED", production_route="Cutting>Sortir>Printing>Sewing>Accessories>QC>Packing", production_status="IN_PROCESS")
    o2 = Order(order_id="SO-014", buyer="MADRID CO", order_type=OrderType.REPEAT_PRODUCTION, buyer_deadline=today+timedelta(days=3), finance_status="PARTIAL", material_status="DELAYED", shipment_status="NOT_READY", overall_status="HOLD", flow_step="INVOICE", projected_shipment=today+timedelta(days=7), buffer_days=-4, created_by_id=users[1].id)
    a2 = Article(order=o2, article_code="JK-014", garment_type="Jacket", qty=300, sample_required=False, sample_status="NOT_REQUIRED", production_route="Cutting>Sortir>Bordir>Sewing>Accessories>QC>Packing", production_status="WAITING_MATERIAL")
    o3 = Order(order_id="SO-021", buyer="TOKYO STYLE", order_type=OrderType.SAMPLE_ONLY, buyer_deadline=today+timedelta(days=14), finance_status="UNPAID", material_status="NOT_REQUESTED", shipment_status="NOT_READY", overall_status="NEW", flow_step="INVOICE", projected_shipment=today+timedelta(days=12), buffer_days=2, created_by_id=users[1].id)
    a3 = Article(order=o3, article_code="TW-021", garment_type="T-Shirt", qty=500, sample_required=True, sample_status="PROCESS", production_route="Cutting>Sewing>QC>Packing", production_status="SAMPLE_PENDING")
    o4 = Order(order_id="SO-033", buyer="BERLIN WEAR", order_type=OrderType.REPEAT_PRODUCTION, buyer_deadline=today+timedelta(days=10), finance_status="UNPAID", material_status="READY", shipment_status="NOT_READY", overall_status="ACTIVE", flow_step="PRODUCTION", projected_shipment=today+timedelta(days=8), buffer_days=2, created_by_id=users[1].id)
    a4 = Article(order=o4, article_code="BW-ECO-01", garment_type="Polo Shirt", qty=1000, sample_required=False, sample_status="NOT_REQUIRED", production_route="Cutting>Sortir>Sewing>QC>Packing", production_status="IN_PROCESS")
    o5 = Order(order_id="SO-042", buyer="SEOUL FASHION", order_type=OrderType.SAMPLE_PRODUCTION, buyer_deadline=today+timedelta(days=21), finance_status="UNPAID", material_status="WAITING", shipment_status="NOT_READY", overall_status="ACTIVE", flow_step="SAMPLE_APPROVED", projected_shipment=today+timedelta(days=18), buffer_days=3, created_by_id=users[1].id)
    a5 = Article(order=o5, article_code="SF-HOODIE-2", garment_type="Hoodie", qty=150, sample_required=True, sample_status="APPROVED", production_route="Cutting>Printing>Sewing>QC>Packing", production_status="WAITING_MATERIAL")
    for order, customer in zip([o1,o2,o3,o4,o5], [c1,c2,c3,c4,c5]):
        order.customer_id = customer.id
    db.add_all([o1,o2,o3,o4,o5]); db.flush()

    # --- PRODUCTION MOVEMENTS ---
    for process, qin, qdone, status, pic in [
        ("Cutting",200,200,"DONE","Siti"),("Sortir",200,200,"DONE","Siti"),("Printing",200,150,"IN_PROCESS","Iman"),("Sewing",150,80,"IN_PROCESS","Siti"),("Accessories",0,0,"WAITING","Siti"),("QC",0,0,"WAITING","Siti"),("Packing",0,0,"WAITING","Siti")]:
        db.add(ProductionMovement(article_id=a1.id, process=process, qty_in=qin, qty_done=qdone, status=status, pic_name=pic, target_date=today))
    for process, qin, qdone, status, pic in [
        ("Cutting",1000,750,"IN_PROCESS","Siti"),("Sortir",750,700,"IN_PROCESS","Siti"),("Sewing",500,200,"IN_PROCESS","Siti")]:
        db.add(ProductionMovement(article_id=a4.id, process=process, qty_in=qin, qty_done=qdone, status=status, pic_name=pic, target_date=today))

    # --- EXCEPTIONS ---
    db.add_all([
        ExceptionItem(order_fk=o2.id, severity="RED", category="Material", title="Material terlambat", owner_role="CFO_MANAGER", owner_name="Lutfi", due_date=today, next_action="Follow-up supplier"),
        ExceptionItem(order_fk=o1.id, severity="YELLOW", category="Production", title="Printing tersisa 50 pcs", owner_role="PRINTING_PIC", owner_name="Iman", due_date=today, next_action="Selesaikan target hari ini"),
        ExceptionItem(order_fk=o3.id, severity="YELLOW", category="Quality", title="Sample belum approved", owner_role="SAMPLE_PIC", owner_name="Fahrul", due_date=today+timedelta(days=5), next_action="Submit sample ke buyer"),
        ExceptionItem(order_fk=o5.id, severity="RED", category="Material", title="Kain PO belum datang", owner_role="CFO_MANAGER", owner_name="Lutfi", due_date=today+timedelta(days=2), next_action="Urgent follow-up supplier kain"),
    ])

    # --- WIP CAPACITY (tanpa date filter — berlaku terus) ---
    for p,c,l,w in [("Cutting",1500,1200,200),("Printing",1500,2100,620),("Sewing",2000,1800,450),("Accessories",800,600,150),("QC",1000,700,100),("Packing",1000,600,120)]:
        db.add(CapacitySnapshot(snapshot_date=today, process=p, capacity=c, planned_load=l, current_wip=w))

    # --- TASKS ---
    db.add_all([
        Task(title="Follow-up material SO-014", assigned_to_id=users[3].id, order_fk=o2.id, due_date=today),
        Task(title="Submit sample HD-CLASSIC ke buyer", assigned_to_id=users[5].id, order_fk=o1.id, due_date=today+timedelta(days=2)),
        Task(title="Selesaikan printing SO-001", assigned_to_id=users[6].id, order_fk=o1.id, due_date=today),
        Task(title="Input QC record SO-033", assigned_to_id=users[4].id, order_fk=o4.id, due_date=today+timedelta(days=3)),
        Task(title="Persiapan packing SO-001", assigned_to_id=users[4].id, order_fk=o1.id, due_date=today+timedelta(days=4)),
    ])

    # --- EMPLOYEES ---
    emp_data = [
        ("EMP-001","Ahmad Ridwan","Production","Operator Cutting","ACTIVE"),
        ("EMP-002","Budi Santoso","Cutting","Supervisor","ACTIVE"),
        ("EMP-003","Dewi Lestari","Sewing","Operator","ACTIVE"),
        ("EMP-004","Eko Prasetyo","Printing","Operator","ACTIVE"),
        ("EMP-005","Fitri Handayani","QC","QC Inspector","ACTIVE"),
        ("EMP-006","Gunawan Wibowo","Packing","Operator","ACTIVE"),
        ("EMP-007","Hendra Kurniawan","HR","Staff HRD","ACTIVE"),
        ("EMP-008","Indah Permata","Finance","Staff Finance","ACTIVE"),
        ("EMP-009","Joko Widodo","Warehouse","Gudang","ON_LEAVE"),
        ("EMP-010","Kartika Sari","Marketing","Sales","ACTIVE"),
    ]
    employees = []
    for eno,name,div,pos,st in emp_data:
        e = Employee(employee_no=eno,name=name,division=div,position=pos,employment_status=st)
        db.add(e); employees.append(e)
    db.flush()

    # --- TRAINING RECORDS ---
    db.add_all([
        TrainingRecord(employee_id=employees[0].id, title="Safety Cutting Machine", start_date=today-timedelta(days=30), end_date=today-timedelta(days=29), result="Pass", evaluator="Budi Santoso"),
        TrainingRecord(employee_id=employees[4].id, title="QC Standard Update", start_date=today-timedelta(days=15), end_date=today-timedelta(days=15), result="Pass", evaluator="Yuni"),
        TrainingRecord(employee_id=employees[2].id, title="Sewing Quality Improvement", start_date=today-timedelta(days=7), end_date=today-timedelta(days=5), result="Pass", evaluator="Yuni"),
    ])

    # --- PERFORMANCE RECORDS ---
    db.add_all([
        PerformanceRecord(employee_id=employees[0].id, period="Q2-2026", quality=85, responsibility=80, discipline=90, spiritual=75, attitude=88, skill=82, total_score=83.33, notes="Consistent performer"),
        PerformanceRecord(employee_id=employees[2].id, period="Q2-2026", quality=92, responsibility=88, discipline=85, spiritual=80, attitude=90, skill=95, total_score=88.33, notes="Top performer"),
        PerformanceRecord(employee_id=employees[4].id, period="Q2-2026", quality=90, responsibility=92, discipline=88, spiritual=78, attitude=85, skill=87, total_score=86.67, notes="Reliable QC"),
    ])

    # --- EMPLOYEE ISSUES ---
    db.add_all([
        EmployeeIssue(employee_id=employees[5].id, issue_type="Attendance", description="Terlambat 3x bulan ini", severity="YELLOW", status="OPEN", reported_by="Yuni"),
        EmployeeIssue(employee_id=employees[3].id, issue_type="Quality", description="Reject rate Printing tinggi", severity="RED", status="IN_PROGRESS", reported_by="Yuni"),
    ])

    # --- INVOICES ---
    db.add_all([
        Invoice(invoice_no="INV-001", order_fk=o1.id, amount=50000000, paid_amount=50000000, due_date=today-timedelta(days=5), status="PAID"),
        Invoice(invoice_no="INV-002", order_fk=o2.id, amount=75000000, paid_amount=30000000, due_date=today+timedelta(days=10), status="PARTIAL"),
        Invoice(invoice_no="INV-003", order_fk=o4.id, amount=120000000, paid_amount=0, due_date=today+timedelta(days=15), status="UNPAID"),
    ])

    # --- QUOTATIONS ---
    db.add_all([
        Quotation(quotation_no="QT-001", order_fk=o1.id, amount=50000000, status="APPROVED", valid_until=today+timedelta(days=30)),
        Quotation(quotation_no="QT-002", order_fk=o3.id, amount=80000000, status="SENT", valid_until=today+timedelta(days=14)),
        Quotation(quotation_no="QT-003", order_fk=o5.id, amount=45000000, status="DRAFT", valid_until=today+timedelta(days=21)),
    ])

    # --- SAMPLE RECORDS ---
    db.add_all([
        SampleRecord(order_fk=o1.id, article_code="HD-CLASSIC", status="APPROVED", notes="Sample approved by buyer", requested_date=today-timedelta(days=20), completed_date=today-timedelta(days=5)),
        SampleRecord(order_fk=o3.id, article_code="TW-021", status="PROCESS", notes="Sample sedang dibuat", requested_date=today-timedelta(days=3)),
        SampleRecord(order_fk=o5.id, article_code="SF-HOODIE-2", status="APPROVED", notes="Sample OK, lanjut produksi", requested_date=today-timedelta(days=15), completed_date=today-timedelta(days=8)),
    ])

    # --- SPK ---
    db.add_all([
        SPK(order_fk=o1.id, spk_no="SPK-001", status="IN_PROCESS", notes="SPK Cutting+Printing selesai, lanjut Sewing"),
        SPK(order_fk=o4.id, spk_no="SPK-002", status="IN_PROCESS", notes="SPK produksi 1000 pcs Polo Eco"),
    ])

    # --- QC RECORDS ---
    db.add_all([
        QCRecord(order_fk=o1.id, article_code="HD-CLASSIC", process="Cutting", total_checked=200, total_pass=198, total_reject=2, reject_reason="Kurang rapi", inspector="Fitri", status="PASS"),
        QCRecord(order_fk=o1.id, article_code="HD-CLASSIC", process="Sortir", total_checked=200, total_pass=200, total_reject=0, reject_reason="", inspector="Fitri", status="PASS"),
        QCRecord(order_fk=o4.id, article_code="BW-ECO-01", process="Cutting", total_checked=750, total_pass=742, total_reject=8, reject_reason="Gunting meleset", inspector="Fitri", status="PASS"),
    ])

    # --- SHIPMENTS ---
    db.add_all([
        Shipment(order_fk=o1.id, shipment_no="SHP-001", status="PREPARING", finance_gate="PENDING", ceo_approval="NOT_REQUIRED", notes="Belum selesai packing", shipped_date=None, tracking_no=None),
        Shipment(order_fk=o2.id, shipment_no="SHP-002", status="NOT_READY", finance_gate="BLOCKED", ceo_approval="NOT_REQUIRED", notes="Material delay, shipment blocked", shipped_date=None, tracking_no=None),
    ])

    # --- PURCHASE ORDERS ---
    db.add_all([
        PurchaseOrder(po_no="PO-001", order_fk=o2.id, item="Kain Polyester", qty=500, unit="meter", supplier="PT Textile Jaya", amount=25000000, status="ORDERED", arrival_date=None, material_status="WAITING"),
        PurchaseOrder(po_no="PO-002", order_fk=o5.id, item="Kain Fleece", qty=200, unit="meter", supplier="PT Kain Nusantara", amount=18000000, status="PENDING", arrival_date=None, material_status="WAITING"),
    ])

    # --- PAYMENTS ---
    db.add_all([
        Payment(invoice_no="INV-001", amount=50000000, payment_date=today-timedelta(days=5), method="Bank Transfer", notes="Full payment received"),
        Payment(invoice_no="INV-002", amount=30000000, payment_date=today-timedelta(days=2), method="Bank Transfer", notes="DP 40%"),
    ])

    # --- CEO DECISIONS ---
    db.add_all([
        CEODecision(order_fk=o2.id, decision_type="Override", subject="Approve SO-014 despite material delay", decision="Approved dengan catatan deadline fleksibel", reason="Buyer urgent, material ready dalam 2 hari", owner_name="Lutfi", action_status="APPROVED"),
        CEODecision(decision_type="Financial Gate", subject="Approve shipment SO-001", decision="Approved", reason="Invoice sudah lunas", owner_name="Lutfi", action_status="APPROVED"),
    ])

    # --- PRODUCTION PLANS ---
    db.add_all([
        ProductionPlan(order_fk=o1.id, plan_date=today, status="PLANNING",
            notes="Planning cutting 200 pcs Hoodie HD-CLASSIC", created_by_id=users[4].id),
        ProductionPlan(order_fk=o4.id, plan_date=today, status="IN_PROGRESS",
            notes="Produksi 1000 pcs Polo Shirt BW-ECO-01 sedang jalan", created_by_id=users[4].id),
    ])

    # --- DELIVERY CONFIRMATIONS ---
    db.flush()
    for payment in db.query(Payment).all():
        invoice = db.query(Invoice).filter_by(invoice_no=payment.invoice_no).one()
        payment.invoice_id = invoice.id
    shp1 = db.query(Shipment).filter_by(shipment_no="SHP-001").first()
    shp2 = db.query(Shipment).filter_by(shipment_no="SHP-002").first()
    db.add_all([
        DeliveryConfirmation(shipment_fk=shp1.id, confirmed_by_customer="John Smith (FRAMSTER)",
            confirmation_date=None, feedback="Menunggu pengiriman", status="PENDING"),
        DeliveryConfirmation(shipment_fk=shp2.id, confirmed_by_customer="Carlos Garcia (MADRID CO)",
            confirmation_date=None, feedback="Menunggu pengiriman", status="PENDING"),
    ])

    # --- ORDER CLOSINGS ---
    db.add_all([
        OrderClosing(order_fk=o1.id, customer_close_status="OPEN",
            financial_close_status="OPEN", order_close_status="OPEN",
            closed_by=None, notes="Order masih dalam produksi"),
        OrderClosing(order_fk=o2.id, customer_close_status="OPEN",
            financial_close_status="OPEN", order_close_status="OPEN",
            closed_by=None, close_date=None, notes="Sebagian closed, tunggu material"),
    ])

    # --- ADD arrival_date & material_status to existing POs ---
    # (PurchaseOrder already has these columns; update via flush)

    db.commit()
