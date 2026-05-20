-- PostgreSQL initialization: immutable audit log trigger
-- Called once on DB creation via Docker entrypoint

CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Audit log records are immutable (ISO 17025 §7.5.2)';
END;
$$ LANGUAGE plpgsql;

-- Trigger is created after Alembic creates the table (applied via migration)
-- This file seeds initial immutable data protections
