-- Run this after roles exist.
-- IMPORTANT: execute as `app_owner` (or grant your current admin user membership with SET and then `SET ROLE app_owner`).

SET ROLE app_owner;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_runtime;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO app_runtime;

RESET ROLE;
