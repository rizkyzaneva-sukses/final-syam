from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from .models import Role, OrderType

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    class Config:
        from_attributes = True

class ArticleCreate(BaseModel):
    article_code: str
    garment_type: Optional[str] = None
    qty: int = Field(gt=0)
    size_breakdown: Optional[str] = None
    sample_required: bool = False
    production_route: Optional[str] = None

class OrderCreate(BaseModel):
    buyer: str
    order_type: OrderType
    buyer_deadline: Optional[date] = None
    notes: Optional[str] = None
    articles: List[ArticleCreate]

class ArticleOut(BaseModel):
    id: int
    article_code: str
    garment_type: Optional[str]
    qty: int
    size_breakdown: Optional[str]
    sample_required: bool
    sample_status: str
    production_route: Optional[str]
    production_status: str
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    order_id: str
    buyer: str
    order_type: OrderType
    order_date: date
    buyer_deadline: Optional[date]
    finance_status: str
    material_status: str
    shipment_status: str
    customer_close_status: str
    financial_close_status: str
    overall_status: str
    projected_shipment: Optional[date]
    buffer_days: Optional[int]
    notes: Optional[str]
    articles: List[ArticleOut] = []
    class Config:
        from_attributes = True

class MovementOut(BaseModel):
    process: str
    qty_in: int
    qty_done: int
    qty_reject: int
    status: str
    pic_name: Optional[str]
    target_date: Optional[date]
    updated_at: datetime
    class Config:
        from_attributes = True
