import uuid
from datetime import date
from pydantic import BaseModel, Field, field_validator


class DashboardStatsResponse(BaseModel):
    accounts_count: int
    journals_count: int
    entries_count: int
    draft_entries_count: int
    validated_entries_count: int
    fiscal_years_count: int
    open_fiscal_years_count: int
    periods_count: int = 0
    open_periods_count: int = 0
    locked_periods_count: int = 0
    third_parties_count: int
    total_debit: str = "0"
    total_credit: str = "0"


class AccountCreate(BaseModel):
    dossier_id: uuid.UUID
    number: str = Field(min_length=1, max_length=10)
    label: str = Field(min_length=1, max_length=255)
    account_class: int = Field(ge=1, le=9)
    account_type: str = "detail"
    nature: str = "debit"
    is_lettrable: bool = False
    default_tva_rate: str | None = None
    parent_number: str | None = None


class AccountResponse(BaseModel):
    id: uuid.UUID
    dossier_id: uuid.UUID
    number: str
    label: str
    account_class: int
    account_type: str
    nature: str
    is_system: bool
    is_lettrable: bool
    default_tva_rate: str | None = None
    parent_number: str | None = None

    model_config = {"from_attributes": True}

    @field_validator("default_tva_rate", mode="before")
    @classmethod
    def decimal_to_str(cls, v):
        if v is not None:
            return str(v)
        return v


class JournalCreate(BaseModel):
    dossier_id: uuid.UUID
    code: str = Field(min_length=1, max_length=10)
    label: str = Field(min_length=1, max_length=255)
    journal_type: str
    counterpart_account_id: uuid.UUID | None = None


class JournalResponse(BaseModel):
    id: uuid.UUID
    dossier_id: uuid.UUID
    code: str
    label: str
    journal_type: str
    counterpart_account_id: uuid.UUID | None = None

    model_config = {"from_attributes": True}


class ThirdPartyCreate(BaseModel):
    dossier_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
    party_type: str = "client"
    ice: str | None = None
    if_number: str | None = None
    rc: str | None = None
    address: str | None = None
    city: str | None = None
    phone: str | None = None
    email: str | None = None
    default_account_id: uuid.UUID | None = None


class ThirdPartyResponse(BaseModel):
    id: uuid.UUID
    dossier_id: uuid.UUID
    name: str
    party_type: str
    ice: str | None = None
    if_number: str | None = None

    model_config = {"from_attributes": True}


class EntryLineCreate(BaseModel):
    account_id: uuid.UUID
    label: str = Field(min_length=1, max_length=255)
    debit: str = "0.00"
    credit: str = "0.00"
    third_party_id: uuid.UUID | None = None


class EntryLineResponse(BaseModel):
    id: uuid.UUID
    line_number: int
    account_id: uuid.UUID
    label: str
    debit: str
    credit: str
    third_party_id: uuid.UUID | None = None
    lettrage_code: str | None = None
    account_number: str | None = None
    account_label: str | None = None

    model_config = {"from_attributes": True}

    @field_validator("debit", "credit", mode="before")
    @classmethod
    def decimal_to_str(cls, v):
        return str(v)


class JournalEntryCreate(BaseModel):
    dossier_id: uuid.UUID
    journal_id: uuid.UUID
    period_id: uuid.UUID
    entry_date: date
    label: str = Field(min_length=1, max_length=255)
    reference: str | None = None
    lines: list[EntryLineCreate] = Field(min_length=2)


class JournalEntryResponse(BaseModel):
    id: uuid.UUID
    dossier_id: uuid.UUID
    journal_id: uuid.UUID
    period_id: uuid.UUID
    entry_date: date
    piece_number: str
    label: str
    status: str
    reference: str | None = None
    reversal_of_id: uuid.UUID | None = None
    lines: list[EntryLineResponse] = []
    total_debit: str = "0.00"
    total_credit: str = "0.00"

    model_config = {"from_attributes": True}

    @field_validator("total_debit", "total_credit", mode="before")
    @classmethod
    def decimal_to_str(cls, v):
        return str(v)
