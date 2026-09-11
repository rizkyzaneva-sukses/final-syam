import enum
from datetime import datetime, date
from sqlalchemy import (Column, Integer, String, Float, Text, Boolean, Date,
    DateTime, Numeric, Enum, ForeignKey)
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
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    article_code = Column(String(80), nullable=False)
    garment_type = Column(String(120), nullable=True)
    qty = Column(Integer, default=0, nullable=False)
    size_breakdown = Column(Text, nullable=True)
    sample_required = Column(Boolean, default=False, nullable=False)
    sample_status = Column(String(32), default="NOT_REQUIRED", nullable=False)
    production_route = Column(Text, nullable=True)
    production_status = Column(String(32), default="NOT_STARTED", nullable=False)
    order = relationship("Order", back_populates="articles")

class ProductionMovement(Base):
    __tablename__ = "production_movements"
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    process = Column(String(80), nullable=False)
    qty_in = Column(Integer, default=0, nullable=False)
    qty_done = Column(Integer, default=0, nullable=False)
    qty_reject = Column(Integer, default=0, nullable=False)
    status = Column(String(32), default="WAITING", nullable=False)
    pic_name = Column(String(120), nullable=True)
    target_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class ExceptionItem(Base):
    __tablename__ = "exceptions"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    severity = Column(String(20), default="YELLOW", nullable=False)
    category = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    owner_role = Column(String(80), nullable=True)
    owner_name = Column(String(120), nullable=True)
    due_date = Column(Date, nullable=True)
    next_action = Column(Text, nullable=True)
    status = Column(String(32), default="OPEN", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class CapacitySnapshot(Base):
    __tablename__ = "capacity_snapshots"
    id = Column(Integer, primary_key=True)
    snapshot_date = Column(Date, nullable=False)
    process = Column(String(80), nullable=False)
    capacity = Column(Integer, default=0, nullable=False)
    planned_load = Column(Integer, default=0, nullable=False)
    current_wip = Column(Integer, default=0, nullable=False)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(String(32), default="OPEN", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(80), nullable=False)
    entity = Column(String(80), nullable=False)
    entity_id = Column(Integer, nullable=True)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    country = Column(String(80), nullable=True)
    contact_name = Column(String(120), nullable=True)
    contact_info = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Quotation(Base):
    __tablename__ = "quotations"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    quotation_no = Column(String(80), unique=True, nullable=False)
    amount = Column(Numeric(18,2), default=0, nullable=False)
    valid_until = Column(Date, nullable=True)
    status = Column(String(32), default="DRAFT", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class SampleRecord(Base):
    __tablename__ = "sample_records"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    article_code = Column(String(80), nullable=False)
    status = Column(String(32), default="PROCESS", nullable=False)
    notes = Column(Text, nullable=True)
    requested_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class SPK(Base):
    __tablename__ = "spks"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    spk_no = Column(String(80), unique=True, nullable=False)
    status = Column(String(32), default="NEW", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class MaterialRequest(Base):
    __tablename__ = "material_requests"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    item_name = Column(String(200), nullable=False)
    qty = Column(Numeric(12,2), default=0, nullable=False)
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
    item = Column(String(200), nullable=True)
    qty = Column(Numeric(12,2), default=0, nullable=True)
    unit = Column(String(40), nullable=True)
    supplier = Column(String(180), nullable=True)
    amount = Column(Numeric(18,2), default=0, nullable=False)
    status = Column(String(32), default="PENDING", nullable=False)
    arrival_date = Column(Date, nullable=True)
    material_status = Column(String(32), default="WAITING", nullable=False)
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
    invoice_no = Column(String(80), nullable=False)
    amount = Column(Numeric(18,2), nullable=False)
    payment_date = Column(Date, nullable=True)
    method = Column(String(80), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class QCRecord(Base):
    __tablename__ = "qc_records"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    article_code = Column(String(80), nullable=False)
    process = Column(String(80), nullable=False)
    total_checked = Column(Integer, default=0, nullable=False)
    total_pass = Column(Integer, default=0, nullable=False)
    total_reject = Column(Integer, default=0, nullable=False)
    reject_reason = Column(Text, nullable=True)
    inspector = Column(String(120), nullable=True)
    status = Column(String(32), default="PASS", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    shipment_no = Column(String(80), unique=True, nullable=False)
    status = Column(String(32), default="NOT_READY", nullable=False)
    finance_gate = Column(String(32), default="PENDING", nullable=False)
    ceo_approval = Column(String(32), nullable=True)
    notes = Column(Text, nullable=True)
    delivery_date = Column(Date, nullable=True)
    shipped_date = Column(Date, nullable=True)
    tracking_no = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    employee_no = Column(String(80), unique=True, nullable=False)
    name = Column(String(120), nullable=False)
    division = Column(String(120), nullable=True)
    position = Column(String(120), nullable=True)
    employment_status = Column(String(32), default="ACTIVE", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class TrainingRecord(Base):
    __tablename__ = "training_records"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    result = Column(String(80), nullable=True)
    evaluator = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class PerformanceRecord(Base):
    __tablename__ = "performance_records"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    period = Column(String(60), nullable=False)
    quality = Column(Float, nullable=True)
    responsibility = Column(Float, nullable=True)
    discipline = Column(Float, nullable=True)
    spiritual = Column(Float, nullable=True)
    attitude = Column(Float, nullable=True)
    skill = Column(Float, nullable=True)
    total_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class EmployeeIssue(Base):
    __tablename__ = "employee_issues"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    issue_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="YELLOW", nullable=False)
    status = Column(String(32), default="OPEN", nullable=False)
    reported_by = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class CEODecision(Base):
    __tablename__ = "ceo_decisions"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    decision_type = Column(String(100), nullable=False)
    subject = Column(String(300), nullable=False)
    decision = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    owner_name = Column(String(120), nullable=True)
    due_date = Column(Date, nullable=True)
    action_status = Column(String(32), default="OPEN", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class SystemConfig(Base):
    __tablename__ = "system_config"
    id = Column(Integer, primary_key=True)
    key = Column(String(120), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=False)

class ProductionPlan(Base):
    __tablename__ = "production_plans"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_date = Column(Date, nullable=True)
    status = Column(String(32), default="PLANNING", nullable=False)
    notes = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    order = relationship("Order", backref="production_plans")

class DeliveryConfirmation(Base):
    __tablename__ = "delivery_confirmations"
    id = Column(Integer, primary_key=True)
    shipment_fk = Column(Integer, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False, index=True)
    confirmed_by_customer = Column(String(160), nullable=True)
    confirmation_date = Column(Date, nullable=True)
    feedback = Column(Text, nullable=True)
    status = Column(String(32), default="PENDING", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    shipment = relationship("Shipment", backref="delivery_confirmations")

class OrderClosing(Base):
    __tablename__ = "order_closings"
    id = Column(Integer, primary_key=True)
    order_fk = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_close_status = Column(String(32), default="OPEN", nullable=False)
    financial_close_status = Column(String(32), default="OPEN", nullable=False)
    order_close_status = Column(String(32), default="OPEN", nullable=False)
    closed_by = Column(String(120), nullable=True)
    close_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    order = relationship("Order", backref="order_closings")
