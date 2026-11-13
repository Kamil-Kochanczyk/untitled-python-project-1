-- 0. Create the user (choose some secret password but later clean it to not commit it)
CREATE USER fastapiuser WITH PASSWORD '';

-- 1. Grant connection to the database
GRANT CONNECT ON DATABASE postgres TO fastapiuser;

-- 2. Grant usage (viewing) and create permissions on the public schema
GRANT USAGE, CREATE ON SCHEMA public TO fastapiuser;

-- 3. Grant CRUD privileges on existing tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO fastapiuser;

-- 4. Grant permissions on sequences (crucial for auto-incrementing IDs/Serial columns)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO fastapiuser;

-- 5. Ensure future tables created by migrations (like Alembic) automatically get these permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO fastapiuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO fastapiuser;

-- Use this script to grant all necessary privileges to the FastAPI app
-- FastAPI app isn't suppossed to have as many privileges as the default superuser
