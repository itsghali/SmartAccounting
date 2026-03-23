APP_DB_ROLE = "easy_app"
AUTH_DB_ROLE = "easy_auth"


def build_enable_rls_sql(table_name: str) -> list[str]:
    app_policy = f"{table_name}_tenant_app_policy"
    auth_policy = f"{table_name}_tenant_auth_policy"
    return [
        f'ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY',
        f'ALTER TABLE "{table_name}" FORCE ROW LEVEL SECURITY',
        (
            f'CREATE POLICY "{app_policy}" ON "{table_name}" '
            f"FOR ALL TO {APP_DB_ROLE} "
            f"USING (tenant_id = app.current_tenant_id()) "
            f"WITH CHECK (tenant_id = app.current_tenant_id())"
        ),
        (
            f'CREATE POLICY "{auth_policy}" ON "{table_name}" '
            f"FOR ALL TO {AUTH_DB_ROLE} "
            f"USING (true) "
            f"WITH CHECK (true)"
        ),
    ]


def build_disable_rls_sql(table_name: str) -> list[str]:
    app_policy = f"{table_name}_tenant_app_policy"
    auth_policy = f"{table_name}_tenant_auth_policy"
    return [
        f'DROP POLICY IF EXISTS "{auth_policy}" ON "{table_name}"',
        f'DROP POLICY IF EXISTS "{app_policy}" ON "{table_name}"',
        f'ALTER TABLE "{table_name}" NO FORCE ROW LEVEL SECURITY',
        f'ALTER TABLE "{table_name}" DISABLE ROW LEVEL SECURITY',
    ]
