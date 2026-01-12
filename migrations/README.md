# Database Migrations

This directory contains SQL migration scripts for the Supabase database.

## How to Run Migrations

### Option 1: Supabase Dashboard (Recommended)

1. Go to your Supabase project dashboard
2. Navigate to: **SQL Editor**
3. Click **New Query**
4. Copy the contents of `001_create_tables.sql`
5. Paste into the SQL editor
6. Click **Run** (or press Cmd/Ctrl + Enter)
7. Verify success message

### Option 2: Supabase CLI

```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_REF

# Run migration
supabase db push
```

### Option 3: psql (Direct Connection)

```bash
# Get connection string from Supabase dashboard (Settings > Database)
psql "postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres" -f migrations/001_create_tables.sql
```

## Migration Files

| File | Description | Status |
|------|-------------|--------|
| `001_create_tables.sql` | Initial schema: jobs and research_results tables | ✅ Ready |

## Schema Overview

### Tables Created

**jobs**
- Stores async job metadata
- Tracks job status and progress
- Real-time enabled for WebSocket updates

**research_results**
- Stores section-level research data
- Links to jobs (CASCADE DELETE)
- Stores full JSON data for flexibility

### Indexes

- `idx_jobs_status` - Fast status filtering
- `idx_jobs_created_at` - Fast time-based queries
- `idx_jobs_status_created` - Combined status + time
- `idx_research_results_job_id` - Fast job result lookups
- `idx_research_results_section` - Fast section filtering

## Verification

After running migration, verify in Supabase:

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name IN ('jobs', 'research_results');

-- Check row counts
SELECT 'jobs' as table_name, COUNT(*) as rows FROM jobs
UNION ALL
SELECT 'research_results', COUNT(*) FROM research_results;

-- Check real-time is enabled
SELECT tablename FROM pg_publication_tables 
WHERE pubname = 'supabase_realtime' AND tablename = 'jobs';
```

## Rollback

If you need to undo the migration:

```sql
-- WARNING: This deletes all data!
DROP TABLE IF EXISTS research_results CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
```

## Next Migration

When Phase 5 adds job logs:
- Create `002_add_job_logs.sql`
- Add job_logs table
- Add additional indexes
