import enum
from datetime import datetime, date
from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from .database import Base

class Role(str, enum.Enum):
    CEO = "CEO"
    CMO_MANAGER = "CMO_MANAGER"
    CMO_SUPPORT = "CMO_SUPPORT"
    CFO_MANAGER = "CFO_MANAGER"
    FINANCE_SUPPORT = "FINANCE_SUPPORT"
    COO_MANAGER = "COO_MANAGER"
    SAMPLE_PIC = "SAMPLE_PIC"
    PRINTING_PIC = "PRINTING_PIC"
    PRODUCTION_PIC = "PRODUCTION_PIC"
    CHRO_MANAGER = "CHRO_MANAGER"
    HR_SUPPORT = "HR_SUPPORT"
    SHIPMENT_ADMIN = "SHIPMENT_ADMIN"

class OrderType(str, enum.Enum):
    SAMPLE_ONLY = "SAMPLE_ONLY"
    SAMPLE_PRODUCTION = "SAMPLE_PRODUCTION"
    REPEAT_PRODUCTION = "REPEAT_PRODUCTION"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(Role), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    order_id = Column(String(64), unique=True, index=True, nullable=False)
    buyer = Column(String(160), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    order_date = Column(Date, default=date.today, nullable=False)
    buyer_deadline = Column(Date, nullable=True)
    finance_status = Column(String(32), default="UNPAID", nullable=False)
    material_status = Column(String(32), default="NOT_REQUESTED", nullable=False)
    shipment_status = Column(String(32), default="NOT_READY", nullable=False)
    customer_close_status = Column(String(32), default="OPEN", nullable=False)
    financial_close_status = Column(String(32), default="OPEN", nullable=False)
    overall_status = Column(String(32), default="NEW", nullable=False)
    projected_shipment = Column(Date, nullable=True)
    buffer_days = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    articles = relationship("Article", back_populates="order", cascade="all, delete-orphan")

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=False)
    article_code = Column(String(80), nullable=False)
    garment_type = Column(String(80), nullable=True)
    mockup_url = Column(String(500), nullable=True)
    qty = Column(Integer, nullable=False)
    size_breakdown = Column(Text, nullable=True)  # JSON string for starter; normalize further when needed
    sample_required = Column(Boolean, default=False, nullable=False)
    sample_status = Column(String(32), default="NOT_REQUIRED", nullable=False)
    production_route = Column(String(500), nullable=True)
    production_status = Column(String(32), default="PLANNED", nullable=False)
    order = relationship("Order", back_populates="articles")

class ProductionMovement(Base):
    __tablename__ = "production_movements"
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), index=True, nullable=False)
    process = Column(String(60), nullable=False)
    qty_in = Column(Integer, default=0, nullable=False)
    qty_done = Column(Integer, default=0, nullable=False)
    qty_reject = Column(Integer, default=0, nullable=False)
    status = Column(String(32), default="WAITING", nullable=False)
    pic_name = Column(String(120), nullable=True)
    target_date = Column(Date, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class ExceptionItem(Base):
    __tablename__ = "exceptions"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), index=True, nullable=True)
    severity = Column(String(12), default="YELLOW", nullable=False)
    category = Column(String(80), nullable=False)
    title = Column(String(250), nullable=False)
    owner_role = Column(String(64), nullable=True)
    owner_name = Column(String(120), nullable=True)
    due_date = Column(Date, nullable=True)
    next_action = Column(String(250), nullable=True)
    status = Column(String(32), default="OPEN", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class CapacitySnapshot(Base):
    __tablename__ = "capacity_snapshots"
    id = Column(Integer, primary_key=True)
    snapshot_date = Column(Date, default=date.today, nullable=False)
    process = Column(String(60), nullable=False)
    capacity = Column(Integer, nullable=False)
    planned_load = Column(Integer, default=0, nullable=False)
    current_wip = Column(Integer, default=0, nullable=False)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(String(32), default="OPEN", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    object_type = Column(String(80), nullable=False)
    object_id = Column(String(100), nullable=False)
    action = Column(String(80), nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String(160), unique=True, nullable=False)
    country = Column(String(80), nullable=True)
    contact_name = Column(String(120), nullable=True)
    contact_info = Column(String(250), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Quotation(Base):
    __tablename__ = "quotations"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    hpp_total = Column(Numeric(18,2), nullable=True)
    sell_total = Column(Numeric(18,2), nullable=True)
    margin_pct = Column(Float, nullable=True)
    status = Column(String(32), default="DRAFT", nullable=False)
    pricing_owner = Column(String(120), nullable=True)
    released_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class SampleRecord(Base):
    __tablename__ = "sample_records"
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    ppm_status = Column(String(32), default="PENDING", nullable=False)
    sample_status = Column(String(32), default="PROCESS", nullable=False)
    customer_decision = Column(String(32), nullable=True)
    pic_name = Column(String(120), nullable=True)
    deadline = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class SPK(Base):
    __tablename__ = "spks"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    spk_no = Column(String(80), unique=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    status = Column(String(32), default="DRAFT", nullable=False)
    generated_by = Column(String(120), nullable=True)
    released_by = Column(String(120), nullable=True)
    released_at = Column(DateTime, nullable=True)
    revision_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class MaterialRequest(Base):
    __tablename__ = "material_requests"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(180), nullable=False)
    qty = Column(Float, nullable=False)
    unit = Column(String(40), nullable=True)
    status = Column(String(32), default="REQUESTED", nullable=False)
    requested_by = Column(String(120), nullable=True)
    required_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True)
    po_no = Column(String(80), unique=True, nullable=False)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    supplier = Column(String(180), nullable=False)
    amount = Column(Numeric(18,2), default=0, nullable=False)
    status = Column(String(32), default="DRAFT", nullable=False)
    eta = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    invoice_no = Column(String(80), unique=True, nullable=False)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(18,2), default=0, nullable=False)
    paid_amount = Column(Numeric(18,2), default=0, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String(32), default="UNPAID", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(18,2), nullable=False)
    paid_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reference = Column(String(180), nullable=True)
    created_by = Column(String(120), nullable=True)

class QCRecord(Base):
    __tablename__ = "qc_records"
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    qty_checked = Column(Integer, default=0, nullable=False)
    qty_pass = Column(Integer, default=0, nullable=False)
    qty_reject = Column(Integer, default=0, nullable=False)
    rework_required = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    shipment_no = Column(String(80), unique=True, nullable=False)
    lot_qty = Column(Integer, nullable=False)
    finance_gate = Column(String(32), default="HOLD", nullable=False)
    outstanding_amount = Column(Numeric(18,2), default=0, nullable=False)
    ceo_approval = Column(String(32), nullable=True)
    courier = Column(String(120), nullable=True)
    tracking_no = Column(String(180), nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    status = Column(String(32), default="NOT_READY", nullable=False)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    employee_no = Column(String(60), unique=True, nullable=False)
    name = Column(String(160), nullable=False)
    division = Column(String(100), nullable=True)
    position = Column(String(120), nullable=True)
    employment_status = Column(String(60), default="ACTIVE", nullable=False)
    skill_matrix = Column(Text, nullable=True)
    joined_at = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class TrainingRecord(Base):
    __tablename__ = "training_records"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(180), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    result = Column(String(80), nullable=True)
    evaluator = Column(String(120), nullable=True)

class PerformanceRecord(Base):
    __tablename__ = "performance_records"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    period = Column(String(40), nullable=False)
    quality = Column(Float, nullable=True)
    responsibility = Column(Float, nullable=True)
    discipline = Column(Float, nullable=True)
    spiritual = Column(Float, nullable=True)
    attitude = Column(Float, nullable=True)
    skill = Column(Float, nullable=True)
    total_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

class EmployeeIssue(Base):
    __tablename__ = "employee_issues"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(100), nullable=False)
    severity = Column(String(20), default="YELLOW", nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(32), default="OPEN", nullable=False)
    owner_name = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class CEODecision(Base):
    __tablename__ = "ceo_decisions"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    decision_type = Column(String(100), nullable=False)
    subject = Column(String(250), nullable=False)
    decision = Column(String(80), nullable=True)
    reason = Column(Text, nullable=True)
    owner_name = Column(String(120), nullable=True)
    due_date = Column(Date, nullable=True)
    action_status = Column(String(32), default="OPEN", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class SystemConfig(Base):
    __tablename__ = "system_configs"
    id = Column(Integer, primary_key=True)
    key = Column(String(120), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    category = Column(String(80), nullable=True)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
