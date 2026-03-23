import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.auth.security import decode_token

logger = logging.getLogger(__name__)

PUBLIC_PATHS = {"/api/v1/auth/register", "/api/v1/auth/login", "/api/v1/health", "/docs", "/openapi.json", "/redoc"}


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in PUBLIC_PATHS or not request.url.path.startswith("/api/"):
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                payload = decode_token(token)
                request.state.tenant_id = payload.get("tid")
                request.state.user_id = payload.get("sub")
                request.state.role = payload.get("role")
            except Exception:
                request.state.tenant_id = None
                request.state.user_id = None
                request.state.role = None
        else:
            request.state.tenant_id = None
            request.state.user_id = None
            request.state.role = None

        return await call_next(request)
