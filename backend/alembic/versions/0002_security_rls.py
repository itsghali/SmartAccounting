"""security rls

Revision ID: 0002_security_rls
Revises: 0001_base_clean
Create Date: 2026-03-19 17:15:00.000000

"""

from typing import Sequence, Union
import importlib.util
from pathlib import Path

from alembic import op
import sqlalchemy as sa

_HELPER_PATH = Path(__file__).resolve().parents[1] / "rls_helpers.py"
_HELPER_SPEC = importlib.util.spec_from_file_location("ea_rls_helpers", _HELPER_PATH)
_HELPER_MODULE = importlib.util.module_from_spec(_HELPER_SPEC)
assert _HELPER_SPEC is not None and _HELPER_SPEC.loader is not None
_HELPER_SPEC.loader.exec_module(_HELPER_MODULE)

APP_DB_ROLE = _HELPER_MODULE.APP_DB_ROLE
AUTH_DB_ROLE = _HELPER_MODULE.AUTH_DB_ROLE
build_disable_rls_sql = _HELPER_MODULE.build_disable_rls_sql
build_enable_rls_sql = _HELPER_MODULE.build_enable_rls_sql

# revision identifiers, used by Alembic.
revision: str = "0002_security_rls"
down_revision: Union[str, None] = "0001_base_clean"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TENANT_TABLES = [
    "companies",
    "dossiers",
    "users",
    "roles",
    "role_permissions",
    "user_roles",
    "user_dossier_assignments",
    "fiscal_years",
    "accounting_periods",
    "audit_logs",
    "documents",
    "document_links",
    "accounts",
    "journals",
    "third_parties",
    "journal_entries",
    "journal_entry_lines",
]

APP_TABLES = TENANT_TABLES.copy()
AUTH_TABLES = [
    "tenants",
    "permissions",
    "companies",
    "dossiers",
    "users",
    "roles",
    "role_permissions",
    "user_roles",
    "accounts",
    "journals",
]


def upgrade() -> None:
    statements = [
        "CREATE SCHEMA IF NOT EXISTS app",
        (
            """
            CREATE OR REPLACE FUNCTION app.current_tenant_id()
            RETURNS uuid
            LANGUAGE sql
            STABLE
            AS $$
                SELECT NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
            $$
            """
        ),
        (
            """
            CREATE OR REPLACE FUNCTION app.current_user_id()
            RETURNS uuid
            LANGUAGE sql
            STABLE
            AS $$
                SELECT NULLIF(current_setting('app.current_user_id', true), '')::uuid
            $$
            """
        ),
        f"GRANT USAGE ON SCHEMA public TO {APP_DB_ROLE}, {AUTH_DB_ROLE}",
        f"GRANT USAGE ON SCHEMA app TO {APP_DB_ROLE}, {AUTH_DB_ROLE}",
        f"GRANT SELECT ON TABLE permissions TO {APP_DB_ROLE}, {AUTH_DB_ROLE}",
        f"GRANT INSERT, SELECT, UPDATE ON TABLE tenants TO {AUTH_DB_ROLE}",
    ]

    for table_name in APP_TABLES:
        statements.append(
            f'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "{table_name}" TO {APP_DB_ROLE}'
        )

    for table_name in AUTH_TABLES:
        statements.append(
            f'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE "{table_name}" TO {AUTH_DB_ROLE}'
        )

    for statement in statements:
        op.execute(sa.text(statement))

    for table_name in TENANT_TABLES:
        for statement in build_enable_rls_sql(table_name):
            op.execute(sa.text(statement))


def downgrade() -> None:
    for table_name in reversed(TENANT_TABLES):
        for statement in build_disable_rls_sql(table_name):
            op.execute(sa.text(statement))

    statements = [
        f"REVOKE ALL ON SCHEMA app FROM {APP_DB_ROLE}, {AUTH_DB_ROLE}",
        f"REVOKE ALL ON SCHEMA public FROM {APP_DB_ROLE}, {AUTH_DB_ROLE}",
        f"REVOKE ALL ON TABLE permissions FROM {APP_DB_ROLE}, {AUTH_DB_ROLE}",
        f"REVOKE ALL ON TABLE tenants FROM {AUTH_DB_ROLE}",
        "DROP FUNCTION IF EXISTS app.current_user_id()",
        "DROP FUNCTION IF EXISTS app.current_tenant_id()",
        "DROP SCHEMA IF EXISTS app",
    ]

    for table_name in APP_TABLES:
        statements.insert(
            0,
            f'REVOKE ALL ON TABLE "{table_name}" FROM {APP_DB_ROLE}',
        )

    for table_name in AUTH_TABLES:
        statements.insert(
            0,
            f'REVOKE ALL ON TABLE "{table_name}" FROM {AUTH_DB_ROLE}',
        )

    for statement in statements:
        op.execute(sa.text(statement))
