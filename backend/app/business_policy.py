"""CEO-owned business thresholds. No implicit financial thresholds are invented."""
import json
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from fastapi import HTTPException
from .models import SystemConfig


class BusinessPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    minimum_margin_percent: Decimal = Field(ge=0, le=100)
    minimum_dp_percent: Decimal = Field(ge=0, le=100)
    cfo_quotation_limit: Decimal = Field(gt=0)
    allow_credit_terms: bool = False


def get_policy(db):
    record = db.query(SystemConfig).filter_by(key="business_policy").first()
    if not record:
        raise HTTPException(409, "CEO must configure pricing and payment policy before approval")
    return BusinessPolicy.model_validate(json.loads(record.value))
