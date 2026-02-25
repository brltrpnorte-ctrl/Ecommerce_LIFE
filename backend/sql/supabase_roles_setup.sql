-- Run in Supabase SQL Editor as an administrative database user.
-- Replace passwords before executing. Do not commit real secrets.

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_owner') THEN
    CREATE ROLE app_owner LOGIN PASSWORD 'REPLACE_WITH_STRONG_OWNER_PASSWORD';
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_runtime') THEN
    CREATE ROLE app_runtime LOGIN PASSWORD 'REPLACE_WITH_STRONG_RUNTIME_PASSWORD';
  END IF;
END
$$;

REVOKE ALL ON DATABASE postgres FROM PUBLIC;

GRANT CONNECT ON DATABASE postgres TO app_runtime;
GRANT USAGE ON SCHEMA public TO app_runtime;

-- Apply to already existing objects
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_runtime;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO app_runtime;
