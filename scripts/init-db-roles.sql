DO
$$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'easy_app') THEN
        CREATE ROLE easy_app LOGIN PASSWORD 'easy_app';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'easy_auth') THEN
        CREATE ROLE easy_auth LOGIN PASSWORD 'easy_auth';
    END IF;
END
$$;

ALTER DATABASE easyaccounting OWNER TO easy_owner;

GRANT CONNECT ON DATABASE easyaccounting TO easy_app, easy_auth;
