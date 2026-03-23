from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.shared.exceptions import BadRequestError

BUSINESS_TIMEZONE = ZoneInfo("Africa/Casablanca")


def get_business_today() -> date:
    return datetime.now(BUSINESS_TIMEZONE).date()


def ensure_not_past_business_date(value: date, field_label: str) -> date:
    if value < get_business_today():
        raise BadRequestError(
            f"La {field_label} ne peut pas etre anterieure a la date du jour."
        )
    return value
