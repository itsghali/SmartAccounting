from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import (
    LoginRequest,
    PasswordChange,
    ProfileUpdate,
    RegisterRequest,
    RoleResponse,
    TokenResponse,
    UserCreateRequest,
    UserResponse,
)
from app.auth.service import (
    authenticate_user,
    change_password,
    create_user,
    list_roles,
    list_users,
    register_user,
    update_profile,
)
from app.database import get_app_db, get_auth_db
from app.dependencies import get_current_user, require_permission

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_auth_db)):
    return await register_user(db, data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_auth_db)):
    return await authenticate_user(db, data.email, data.password)


@router.get("/me", response_model=UserResponse)
async def me(current_user=Depends(get_current_user)):
    user = current_user["user"]
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        tenant_id=user.tenant_id,
        roles=[ur.role.name for ur in user.user_roles],
    )


@router.put("/profile", response_model=UserResponse)
async def put_profile(
    data: ProfileUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_app_db),
):
    user = await update_profile(db, current_user["user"], data)
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        tenant_id=user.tenant_id,
        roles=[ur.role.name for ur in user.user_roles],
    )


@router.post("/change-password", status_code=204)
async def post_change_password(
    data: PasswordChange,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_app_db),
):
    await change_password(db, current_user["user"], data)


@router.get(
    "/users",
    response_model=list[UserResponse],
)
async def get_users(
    current_user=Depends(require_permission("admin.users.manage")),
    db: AsyncSession = Depends(get_app_db),
):
    users = await list_users(db, current_user["tenant_id"])
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            tenant_id=user.tenant_id,
            roles=[ur.role.name for ur in user.user_roles],
        )
        for user in users
    ]


@router.get(
    "/roles",
    response_model=list[RoleResponse],
)
async def get_roles(
    current_user=Depends(require_permission("admin.roles.read")),
    db: AsyncSession = Depends(get_app_db),
):
    return await list_roles(db, current_user["tenant_id"])


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=201,
)
async def post_user(
    data: UserCreateRequest,
    current_user=Depends(require_permission("admin.users.manage")),
    db: AsyncSession = Depends(get_app_db),
):
    actor_role_names = {ur.role.name for ur in current_user["user"].user_roles}
    user = await create_user(
        db,
        current_user["tenant_id"],
        data,
        actor_role_names=actor_role_names,
    )
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        tenant_id=user.tenant_id,
        roles=[ur.role.name for ur in user.user_roles],
    )
