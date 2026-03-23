import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decode_token
from app.database import get_app_db
from app.shared.exceptions import NotFoundError

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_app_db),
) -> dict:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    from app.auth.service import ensure_user_has_system_role, get_user_by_id

    try:
        user_id = uuid.UUID(payload["sub"])
        tenant_id = uuid.UUID(payload["tid"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token context",
        )

    try:
        user = await get_user_by_id(db, user_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token context",
        )

    user = await ensure_user_has_system_role(db, user)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
        )

    return {
        "user": user,
        "tenant_id": tenant_id,
    }


def current_user_has_any_role(current_user: dict, allowed_roles: set[str]) -> bool:
    user = current_user["user"]
    user_role_names = {ur.role.name for ur in user.user_roles}
    return bool(user_role_names.intersection(allowed_roles))


def require_permission(permission_code: str):
    async def checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user_has_any_role(current_user, {"Administrateur"}):
            return current_user

        user = current_user["user"]
        user_permissions = set()
        for ur in user.user_roles:
            for rp in ur.role.permissions:
                user_permissions.add(rp.permission.code)

        if permission_code not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission_code}",
            )
        return current_user

    return checker


def require_roles(*allowed_roles: str):
    allowed_roles_set = set(allowed_roles)

    async def checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user_has_any_role(current_user, allowed_roles_set):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Access reserved to roles: "
                + ", ".join(sorted(allowed_roles_set))
            ),
        )

    return checker
