from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequestError(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnbalancedEntryError(BadRequestError):
    def __init__(self):
        super().__init__(detail="Journal entry is not balanced: total debit must equal total credit")


class PeriodClosedError(BadRequestError):
    def __init__(self):
        super().__init__(detail="Cannot modify entries in a closed or locked period")


class ImmutableEntryError(BadRequestError):
    def __init__(self):
        super().__init__(detail="Validated entries are immutable. Use reversal to correct.")
