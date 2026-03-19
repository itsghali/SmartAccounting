import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field


class FiscalYearCreate(BaseModel):
    dossier_id: uuid.UUID
    name: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date


class FiscalYearResponse(BaseModel):
    id: uuid.UUID
    dossier_id: uuid.UUID
    name: str
    start_date: date
    end_date: date
    status: str

    model_config = {"from_attributes": True}


class PeriodResponse(BaseModel):
    id: uuid.UUID
    fiscal_year_id: uuid.UUID
    name: str
    start_date: date
    end_date: date
    period_number: int
    status: str

    model_config = {"from_attributes": True}


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    action: str
    entity_type: str
    entity_id: str
    old_values: dict | None
    new_values: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
