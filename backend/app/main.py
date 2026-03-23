from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.config import get_settings
from app.database import dispose_engines
from app.middleware.tenant import TenantMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await dispose_engines()


def _extract_sqlstate(exc: BaseException) -> str | None:
    sqlstate = getattr(exc, "sqlstate", None)
    if sqlstate:
        return str(sqlstate)

    pgcode = getattr(exc, "pgcode", None)
    if pgcode:
        return str(pgcode)

    orig = getattr(exc, "orig", None)
    if orig is None:
        return None
    return _extract_sqlstate(orig)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TenantMiddleware)

    # Routers
    from app.auth.router import router as auth_router
    from app.tenant.router import router as tenant_router
    from app.core.router import router as core_router
    from app.accounting.router import router as accounting_router
    from app.accounting.reporting_router import router as reporting_router

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(tenant_router, prefix="/api/v1")
    app.include_router(core_router, prefix="/api/v1")
    app.include_router(accounting_router, prefix="/api/v1")
    app.include_router(reporting_router, prefix="/api/v1")

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(_, exc: IntegrityError):
        sqlstate = _extract_sqlstate(exc)
        if sqlstate == "23503":
            return JSONResponse(
                status_code=400,
                content={
                    "detail": (
                        "La ressource liee est introuvable ou hors du perimetre du tenant."
                    )
                },
            )
        if sqlstate == "23505":
            return JSONResponse(
                status_code=400,
                content={"detail": "Cette valeur existe deja."},
            )
        return JSONResponse(
            status_code=400,
            content={"detail": "Operation impossible a cause d'une contrainte de donnees."},
        )

    @app.exception_handler(DBAPIError)
    async def handle_dbapi_error(_, exc: DBAPIError):
        sqlstate = _extract_sqlstate(exc)
        if sqlstate == "42501":
            return JSONResponse(
                status_code=403,
                content={"detail": "Acces interdit ou hors perimetre du tenant."},
            )
        return JSONResponse(
            status_code=500,
            content={"detail": "Une erreur technique est survenue."},
        )

    @app.get("/api/v1/health")
    async def health():
        return {"status": "ok", "version": settings.VERSION}

    return app


app = create_app()
