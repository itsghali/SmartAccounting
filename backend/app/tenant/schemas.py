import uuid
from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    legal_form: str | None = None
    ice: str | None = None
    if_number: str | None = None
    rc: str | None = None
    patente: str | None = None
    cnss_employer: str | None = None
    address: str | None = None
    city: str | None = None
    phone: str | None = None
    email: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    legal_form: str | None = None
    ice: str | None = None
    if_number: str | None = None
    rc: str | None = None
    patente: str | None = None
    cnss_employer: str | None = None
    address: str | None = None
    city: str | None = None
    phone: str | None = None
    email: str | None = None


class CompanyResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    legal_form: str | None = None
    ice: str | None = None
    if_number: str | None = None
    rc: str | None = None
    patente: str | None = None
    cnss_employer: str | None = None
    address: str | None = None
    city: str | None = None
    phone: str | None = None
    email: str | None = None

    model_config = {"from_attributes": True}


class DossierCreate(BaseModel):
    company_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)


class DossierResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    company_id: uuid.UUID
    name: str
    status: str

    model_config = {"from_attributes": True}
