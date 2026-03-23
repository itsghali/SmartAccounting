from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()


def _build_engine(url: str) -> AsyncEngine:
    return create_async_engine(
        url,
        echo=settings.DATABASE_ECHO,
        pool_size=20,
        max_overflow=10,
    )


app_engine = _build_engine(settings.DATABASE_URL)
auth_engine = _build_engine(settings.AUTH_DATABASE_URL)

app_session_factory = async_sessionmaker(
    app_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
auth_session_factory = async_sessionmaker(
    auth_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def apply_rls_context(
    session: AsyncSession,
    tenant_id: str | None,
    user_id: str | None = None,
) -> None:
    await session.execute(
        text(
            """
            select
                set_config('app.current_tenant_id', :tenant_id, true),
                set_config('app.current_user_id', :user_id, true)
            """
        ),
        {
            "tenant_id": tenant_id or "",
            "user_id": user_id or "",
        },
    )


async def _session_dependency(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_app_db(request: Request) -> AsyncGenerator[AsyncSession, None]:  # type: ignore[misc]
    async with app_session_factory() as session:
        try:
            await apply_rls_context(
                session,
                getattr(request.state, "tenant_id", None),
                getattr(request.state, "user_id", None),
            )
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_auth_db() -> AsyncGenerator[AsyncSession, None]:  # type: ignore[misc]
    async for session in _session_dependency(auth_session_factory):
        yield session


async def dispose_engines() -> None:
    await app_engine.dispose()
    await auth_engine.dispose()
