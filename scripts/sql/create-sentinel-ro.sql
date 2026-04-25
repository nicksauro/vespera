-- ============================================================================
-- create-sentinel-ro.sql
-- ----------------------------------------------------------------------------
-- Story:     T002.0a (Custodial + Parquet Materialization)
-- Epic:      EPIC-T002.0
-- Owner:     Dara (@data-engineer) — co-signed by Riven (@risk-manager, R10)
-- Target:    sentinel-timescaledb @ localhost:5433, db=sentinel_db
-- ----------------------------------------------------------------------------
-- Purpose:
--   Create a read-only PostgreSQL role `sentinel_ro` with MINIMAL privileges
--   on the `public.trades` hypertable. This role is the ONLY credential
--   Vespera will use at runtime to materialize in-sample parquet. It is
--   physically incapable of INSERT / UPDATE / DELETE / TRUNCATE / DDL, so any
--   bug or adversarial path through Vespera cannot corrupt the canonical
--   Sentinel dataset (R10 custodial fail-closed).
--
-- Design notes:
--   - Idempotent: safe to re-run. CREATE ROLE guarded via DO-block; GRANTs
--     are no-ops if already present.
--   - Schema-level: REVOKE ALL on schema public, then GRANT USAGE only
--     (required to reference objects). No CREATE on schema.
--   - Table-level: GRANT SELECT on public.trades only. Other tables remain
--     inaccessible.
--   - Password: NOT set here. Assigned via a separate `ALTER ROLE sentinel_ro
--     WITH PASSWORD '<redacted>';` statement applied interactively by Dara
--     after this script runs, so the secret never enters git history.
--
-- Verification (Riven sign-off):
--   SELECT has_table_privilege('sentinel_ro', 'public.trades', 'SELECT');
--     -> expected: t
--   SELECT has_table_privilege('sentinel_ro', 'public.trades', 'INSERT');
--     -> expected: f
--   SELECT has_table_privilege('sentinel_ro', 'public.trades', 'UPDATE');
--     -> expected: f
--   SELECT has_table_privilege('sentinel_ro', 'public.trades', 'DELETE');
--     -> expected: f
--   SELECT has_table_privilege('sentinel_ro', 'public.trades', 'TRUNCATE');
--     -> expected: f
--
-- Rollback:
--   REVOKE ALL ON TABLE public.trades FROM sentinel_ro;
--   REVOKE ALL ON SCHEMA public FROM sentinel_ro;
--   DROP ROLE IF EXISTS sentinel_ro;
-- ============================================================================

BEGIN;

-- 1. Create role (idempotent)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sentinel_ro') THEN
        CREATE ROLE sentinel_ro WITH LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
        RAISE NOTICE 'Role sentinel_ro created';
    ELSE
        RAISE NOTICE 'Role sentinel_ro already exists, skipping CREATE';
    END IF;
END
$$;

-- 2. Schema-level privileges: strip everything, then allow USAGE only
REVOKE ALL ON SCHEMA public FROM sentinel_ro;
GRANT USAGE ON SCHEMA public TO sentinel_ro;

-- 3. Table-level privileges: SELECT only on trades
REVOKE ALL ON TABLE public.trades FROM sentinel_ro;
GRANT SELECT ON TABLE public.trades TO sentinel_ro;

-- 4. Ensure no future tables auto-grant to sentinel_ro (defensive)
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM sentinel_ro;

COMMIT;

-- ============================================================================
-- Post-migration handshake (Riven co-sign required):
--   \echo '-- Custodial verification --'
--   SELECT
--     has_table_privilege('sentinel_ro','public.trades','SELECT')   AS can_select,
--     has_table_privilege('sentinel_ro','public.trades','INSERT')   AS can_insert,
--     has_table_privilege('sentinel_ro','public.trades','UPDATE')   AS can_update,
--     has_table_privilege('sentinel_ro','public.trades','DELETE')   AS can_delete,
--     has_table_privilege('sentinel_ro','public.trades','TRUNCATE') AS can_truncate;
--   Expected: t | f | f | f | f
-- ============================================================================
