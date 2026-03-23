"""base clean

Revision ID: 0001_base_clean
Revises:
Create Date: 2026-03-19 17:00:00.000000

"""

from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_base_clean"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PERMISSIONS = [
    ("admin.users.manage", "Gestion des utilisateurs du tenant", "admin"),
    ("admin.roles.read", "Consultation des roles systeme", "admin"),
    ("admin.dossiers.manage", "Gestion des societes et dossiers", "admin"),
    ("admin.seed", "Seed et maintenance des donnees systeme", "admin"),
    ("comptabilite.write", "Creation et modification des donnees comptables", "comptabilite"),
    ("comptabilite.validate", "Validation et contrepassation des ecritures", "comptabilite"),
    ("tva.read", "Consultation de la TVA", "tva"),
    ("tva.manage", "Parametrage TVA", "tva"),
    ("tva.liquidate", "Liquidation TVA", "tva"),
    ("closing.read", "Consultation des workflows de cloture", "closing"),
    ("closing.execute", "Execution des operations de cloture", "closing"),
    ("closing.reopen", "Reouverture des exercices clotures", "closing"),
    ("templates.manage", "Gestion des modeles d'ecritures", "accounting"),
    ("imports.execute", "Execution des imports comptables", "accounting"),
    ("central_journal.read", "Consultation du journal central", "accounting"),
    ("fixed_assets.read", "Consultation des immobilisations", "fixed_assets"),
    ("fixed_assets.manage", "Gestion des immobilisations", "fixed_assets"),
    ("fixed_assets.post", "Generation des dotations et ecritures", "fixed_assets"),
]


def upgrade() -> None:
    ddl = """
    CREATE TABLE permissions (
        id UUID PRIMARY KEY,
        code VARCHAR(100) NOT NULL UNIQUE,
        description TEXT,
        module VARCHAR(50) NOT NULL
    );

    CREATE TABLE tenants (
        id UUID PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        plan VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );

    CREATE TABLE companies (
        id UUID PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        legal_form VARCHAR(50),
        ice VARCHAR(15),
        if_number VARCHAR(20),
        rc VARCHAR(50),
        patente VARCHAR(50),
        cnss_employer VARCHAR(20),
        address TEXT,
        city VARCHAR(100),
        phone VARCHAR(20),
        email VARCHAR(255),
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_companies_tenant_id_id UNIQUE (tenant_id, id)
    );
    CREATE INDEX ix_companies_tenant_id ON companies (tenant_id);

    CREATE TABLE dossiers (
        id UUID PRIMARY KEY,
        company_id UUID NOT NULL REFERENCES companies(id),
        name VARCHAR(255) NOT NULL,
        status VARCHAR(50) NOT NULL,
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_dossiers_tenant_id_id UNIQUE (tenant_id, id),
        CONSTRAINT fk_dossiers_company_tenant FOREIGN KEY (tenant_id, company_id)
            REFERENCES companies (tenant_id, id)
    );
    CREATE INDEX ix_dossiers_tenant_id ON dossiers (tenant_id);

    CREATE TABLE roles (
        id UUID PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        is_system BOOLEAN NOT NULL DEFAULT false,
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_role_tenant_name UNIQUE (tenant_id, name),
        CONSTRAINT uq_roles_tenant_id_id UNIQUE (tenant_id, id)
    );
    CREATE INDEX ix_roles_tenant_id ON roles (tenant_id);

    CREATE TABLE users (
        id UUID PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        password_hash TEXT NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT true,
        mfa_secret VARCHAR(64),
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT ck_users_email_lowercase CHECK (email = lower(email)),
        CONSTRAINT uq_users_email UNIQUE (email),
        CONSTRAINT uq_users_tenant_id_id UNIQUE (tenant_id, id)
    );
    CREATE INDEX ix_users_tenant_id ON users (tenant_id);

    CREATE TABLE role_permissions (
        role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
        permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        PRIMARY KEY (role_id, permission_id),
        CONSTRAINT fk_role_permissions_role_tenant FOREIGN KEY (tenant_id, role_id)
            REFERENCES roles (tenant_id, id) ON DELETE CASCADE,
        CONSTRAINT uq_role_permissions_tenant_role_permission UNIQUE (tenant_id, role_id, permission_id)
    );
    CREATE INDEX ix_role_permissions_tenant_id ON role_permissions (tenant_id);

    CREATE TABLE user_roles (
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        PRIMARY KEY (user_id, role_id),
        CONSTRAINT fk_user_roles_user_tenant FOREIGN KEY (tenant_id, user_id)
            REFERENCES users (tenant_id, id) ON DELETE CASCADE,
        CONSTRAINT fk_user_roles_role_tenant FOREIGN KEY (tenant_id, role_id)
            REFERENCES roles (tenant_id, id) ON DELETE CASCADE,
        CONSTRAINT uq_user_roles_tenant_user_role UNIQUE (tenant_id, user_id, role_id)
    );
    CREATE INDEX ix_user_roles_tenant_id ON user_roles (tenant_id);

    CREATE TABLE audit_logs (
        id UUID PRIMARY KEY,
        user_id UUID,
        action VARCHAR(50) NOT NULL,
        entity_type VARCHAR(100) NOT NULL,
        entity_id VARCHAR(100) NOT NULL,
        old_values JSONB,
        new_values JSONB,
        ip_address VARCHAR(45),
        user_agent TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        CONSTRAINT uq_audit_logs_tenant_id_id UNIQUE (tenant_id, id)
    );
    CREATE INDEX ix_audit_logs_tenant_id ON audit_logs (tenant_id);

    CREATE TABLE documents (
        id UUID PRIMARY KEY,
        filename VARCHAR(500) NOT NULL,
        mime_type VARCHAR(100) NOT NULL,
        size_bytes INTEGER NOT NULL,
        storage_path VARCHAR(1000) NOT NULL,
        checksum_sha256 VARCHAR(64),
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_documents_tenant_id_id UNIQUE (tenant_id, id)
    );
    CREATE INDEX ix_documents_tenant_id ON documents (tenant_id);

    CREATE TABLE document_links (
        id UUID PRIMARY KEY,
        document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        entity_type VARCHAR(100) NOT NULL,
        entity_id UUID NOT NULL,
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_document_links_tenant_id_id UNIQUE (tenant_id, id),
        CONSTRAINT fk_document_links_document_tenant FOREIGN KEY (tenant_id, document_id)
            REFERENCES documents (tenant_id, id) ON DELETE CASCADE
    );
    CREATE INDEX ix_document_links_tenant_id ON document_links (tenant_id);

    CREATE TABLE accounts (
        id UUID PRIMARY KEY,
        dossier_id UUID NOT NULL REFERENCES dossiers(id),
        number VARCHAR(10) NOT NULL,
        label VARCHAR(255) NOT NULL,
        account_class INTEGER NOT NULL,
        account_type VARCHAR(20) NOT NULL DEFAULT 'detail',
        nature VARCHAR(10) NOT NULL DEFAULT 'debit',
        is_system BOOLEAN NOT NULL DEFAULT false,
        is_lettrable BOOLEAN NOT NULL DEFAULT false,
        default_tva_rate NUMERIC(5, 2),
        parent_number VARCHAR(10),
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_account_dossier_number UNIQUE (dossier_id, number),
        CONSTRAINT uq_accounts_tenant_id_id UNIQUE (tenant_id, id),
        CONSTRAINT fk_accounts_dossier_tenant FOREIGN KEY (tenant_id, dossier_id)
            REFERENCES dossiers (tenant_id, id)
    );
    CREATE INDEX ix_accounts_tenant_id ON accounts (tenant_id);

    CREATE TABLE fiscal_years (
        id UUID PRIMARY KEY,
        dossier_id UUID NOT NULL REFERENCES dossiers(id),
        name VARCHAR(100) NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'CREATED',
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_fiscal_years_tenant_id_id UNIQUE (tenant_id, id),
        CONSTRAINT fk_fiscal_years_dossier_tenant FOREIGN KEY (tenant_id, dossier_id)
            REFERENCES dossiers (tenant_id, id)
    );
    CREATE INDEX ix_fiscal_years_tenant_id ON fiscal_years (tenant_id);

    CREATE TABLE user_dossier_assignments (
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        dossier_id UUID NOT NULL REFERENCES dossiers(id) ON DELETE CASCADE,
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        PRIMARY KEY (user_id, dossier_id),
        CONSTRAINT fk_user_dossier_assignments_user_tenant FOREIGN KEY (tenant_id, user_id)
            REFERENCES users (tenant_id, id) ON DELETE CASCADE,
        CONSTRAINT fk_user_dossier_assignments_dossier_tenant FOREIGN KEY (tenant_id, dossier_id)
            REFERENCES dossiers (tenant_id, id) ON DELETE CASCADE,
        CONSTRAINT uq_user_dossier_assignments_tenant_user_dossier UNIQUE (tenant_id, user_id, dossier_id)
    );
    CREATE INDEX ix_user_dossier_assignments_tenant_id ON user_dossier_assignments (tenant_id);

    CREATE TABLE accounting_periods (
        id UUID PRIMARY KEY,
        fiscal_year_id UUID NOT NULL REFERENCES fiscal_years(id),
        dossier_id UUID NOT NULL REFERENCES dossiers(id),
        name VARCHAR(50) NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        period_number INTEGER NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_accounting_periods_tenant_id_id UNIQUE (tenant_id, id),
        CONSTRAINT fk_accounting_periods_fiscal_year_tenant FOREIGN KEY (tenant_id, fiscal_year_id)
            REFERENCES fiscal_years (tenant_id, id),
        CONSTRAINT fk_accounting_periods_dossier_tenant FOREIGN KEY (tenant_id, dossier_id)
            REFERENCES dossiers (tenant_id, id)
    );
    CREATE INDEX ix_accounting_periods_tenant_id ON accounting_periods (tenant_id);

    CREATE TABLE journals (
        id UUID PRIMARY KEY,
        dossier_id UUID NOT NULL REFERENCES dossiers(id),
        code VARCHAR(10) NOT NULL,
        label VARCHAR(255) NOT NULL,
        journal_type VARCHAR(20) NOT NULL,
        counterpart_account_id UUID REFERENCES accounts(id),
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_journal_dossier_code UNIQUE (dossier_id, code),
        CONSTRAINT uq_journals_tenant_id_id UNIQUE (tenant_id, id),
        CONSTRAINT fk_journals_dossier_tenant FOREIGN KEY (tenant_id, dossier_id)
            REFERENCES dossiers (tenant_id, id),
        CONSTRAINT fk_journals_counterpart_account_tenant FOREIGN KEY (tenant_id, counterpart_account_id)
            REFERENCES accounts (tenant_id, id)
    );
    CREATE INDEX ix_journals_tenant_id ON journals (tenant_id);

    CREATE TABLE third_parties (
        id UUID PRIMARY KEY,
        dossier_id UUID NOT NULL REFERENCES dossiers(id),
        name VARCHAR(255) NOT NULL,
        party_type VARCHAR(20) NOT NULL,
        ice VARCHAR(15),
        if_number VARCHAR(20),
        rc VARCHAR(50),
        address TEXT,
        city VARCHAR(100),
        phone VARCHAR(20),
        email VARCHAR(255),
        default_account_id UUID REFERENCES accounts(id),
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_third_parties_tenant_id_id UNIQUE (tenant_id, id),
        CONSTRAINT fk_third_parties_dossier_tenant FOREIGN KEY (tenant_id, dossier_id)
            REFERENCES dossiers (tenant_id, id),
        CONSTRAINT fk_third_parties_default_account_tenant FOREIGN KEY (tenant_id, default_account_id)
            REFERENCES accounts (tenant_id, id)
    );
    CREATE INDEX ix_third_parties_tenant_id ON third_parties (tenant_id);

    CREATE TABLE journal_entries (
        id UUID PRIMARY KEY,
        dossier_id UUID NOT NULL REFERENCES dossiers(id),
        journal_id UUID NOT NULL REFERENCES journals(id),
        period_id UUID NOT NULL REFERENCES accounting_periods(id),
        entry_date DATE NOT NULL,
        piece_number VARCHAR(50) NOT NULL,
        label VARCHAR(255) NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
        reference VARCHAR(100),
        reversal_of_id UUID REFERENCES journal_entries(id),
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_journal_entries_tenant_id_id UNIQUE (tenant_id, id),
        CONSTRAINT fk_journal_entries_dossier_tenant FOREIGN KEY (tenant_id, dossier_id)
            REFERENCES dossiers (tenant_id, id),
        CONSTRAINT fk_journal_entries_journal_tenant FOREIGN KEY (tenant_id, journal_id)
            REFERENCES journals (tenant_id, id),
        CONSTRAINT fk_journal_entries_period_tenant FOREIGN KEY (tenant_id, period_id)
            REFERENCES accounting_periods (tenant_id, id),
        CONSTRAINT fk_journal_entries_reversal_tenant FOREIGN KEY (tenant_id, reversal_of_id)
            REFERENCES journal_entries (tenant_id, id)
    );
    CREATE INDEX ix_journal_entries_tenant_id ON journal_entries (tenant_id);

    CREATE TABLE journal_entry_lines (
        id UUID PRIMARY KEY,
        entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
        line_number INTEGER NOT NULL,
        account_id UUID NOT NULL REFERENCES accounts(id),
        third_party_id UUID REFERENCES third_parties(id),
        label VARCHAR(255) NOT NULL,
        debit NUMERIC(15, 2) NOT NULL DEFAULT 0,
        credit NUMERIC(15, 2) NOT NULL DEFAULT 0,
        lettrage_code VARCHAR(10),
        tenant_id UUID NOT NULL REFERENCES tenants(id),
        CONSTRAINT uq_journal_entry_lines_tenant_id_id UNIQUE (tenant_id, id),
        CONSTRAINT fk_journal_entry_lines_entry_tenant FOREIGN KEY (tenant_id, entry_id)
            REFERENCES journal_entries (tenant_id, id) ON DELETE CASCADE,
        CONSTRAINT fk_journal_entry_lines_account_tenant FOREIGN KEY (tenant_id, account_id)
            REFERENCES accounts (tenant_id, id),
        CONSTRAINT fk_journal_entry_lines_third_party_tenant FOREIGN KEY (tenant_id, third_party_id)
            REFERENCES third_parties (tenant_id, id)
    );
    CREATE INDEX ix_journal_entry_lines_tenant_id ON journal_entry_lines (tenant_id);
    """

    for statement in [chunk.strip() for chunk in ddl.split(";\n") if chunk.strip()]:
        op.execute(sa.text(statement))

    permission_table = sa.table(
        "permissions",
        sa.column("id", sa.UUID()),
        sa.column("code", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("module", sa.String()),
    )
    op.bulk_insert(
        permission_table,
        [
            {
                "id": uuid.uuid4(),
                "code": code,
                "description": description,
                "module": module,
            }
            for code, description, module in PERMISSIONS
        ],
    )


def downgrade() -> None:
    ddl = """
    DROP TABLE IF EXISTS journal_entry_lines;
    DROP TABLE IF EXISTS journal_entries;
    DROP TABLE IF EXISTS third_parties;
    DROP TABLE IF EXISTS journals;
    DROP TABLE IF EXISTS accounting_periods;
    DROP TABLE IF EXISTS user_dossier_assignments;
    DROP TABLE IF EXISTS fiscal_years;
    DROP TABLE IF EXISTS accounts;
    DROP TABLE IF EXISTS document_links;
    DROP TABLE IF EXISTS documents;
    DROP TABLE IF EXISTS audit_logs;
    DROP TABLE IF EXISTS user_roles;
    DROP TABLE IF EXISTS role_permissions;
    DROP TABLE IF EXISTS users;
    DROP TABLE IF EXISTS roles;
    DROP TABLE IF EXISTS dossiers;
    DROP TABLE IF EXISTS companies;
    DROP TABLE IF EXISTS tenants;
    DROP TABLE IF EXISTS permissions;
    """
    for statement in [chunk.strip() for chunk in ddl.split(";\n") if chunk.strip()]:
        op.execute(sa.text(statement))
