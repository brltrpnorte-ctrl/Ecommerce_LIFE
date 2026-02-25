-- Quick verification helpers for roles and privileges

SELECT current_user, session_user;

SELECT rolname
FROM pg_roles
WHERE rolname IN ('app_owner', 'app_runtime')
ORDER BY rolname;

-- Default privileges configured in current database
SELECT *
FROM pg_default_acl;
