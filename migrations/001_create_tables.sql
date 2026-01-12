-- Migration 001: Create Jobs and Research Results Tables
-- Phase 1: Database Schema + Client
-- Run this in Supabase SQL Editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- Jobs Table
-- ============================================================
-- Stores async job metadata and status
CREATE TABLE IF NOT EXISTS code_research_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Job status and progress
    status VARCHAR(20) NOT NULL 
        CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    progress VARCHAR(50),  -- e.g., "5/13 sections complete"
    
    -- Job input parameters
    address TEXT NOT NULL,
    llm_provider VARCHAR(20) DEFAULT 'openai' 
        CHECK (llm_provider IN ('openai', 'gemini')),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Error tracking
    error_message TEXT,
    
    -- Optional metadata (JSON for flexibility)
    metadata JSONB DEFAULT '{}'::jsonb
);

-- ============================================================
-- Research Results Table
-- ============================================================
-- Stores individual section results for each job
CREATE TABLE IF NOT EXISTS code_research_research_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Foreign key to jobs (cascade delete)
    job_id UUID NOT NULL REFERENCES code_research_jobs(id) ON DELETE CASCADE,
    
    -- Section information
    section_name VARCHAR(100) NOT NULL,  -- e.g., "location_information", "wall_signs"
    section_data JSONB NOT NULL,         -- Full Pydantic model as JSON
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Indexes for Performance
-- ============================================================

-- Jobs table indexes
CREATE INDEX IF NOT EXISTS idx_code_research_jobs_status 
    ON code_research_jobs(status);

CREATE INDEX IF NOT EXISTS idx_code_research_jobs_created_at 
    ON code_research_jobs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_code_research_jobs_status_created 
    ON code_research_jobs(status, created_at DESC);

-- Research results table indexes
CREATE INDEX IF NOT EXISTS idx_code_research_research_results_job_id 
    ON code_research_research_results(job_id);

CREATE INDEX IF NOT EXISTS idx_code_research_research_results_section 
    ON code_research_research_results(section_name);

-- ============================================================
-- Enable Real-Time for Jobs Table (Supabase)
-- ============================================================
-- This allows clients to subscribe to job status updates via WebSocket

-- Add jobs table to real-time publication
ALTER PUBLICATION supabase_realtime ADD TABLE code_research_jobs;

-- ============================================================
-- Comments for Documentation
-- ============================================================

COMMENT ON TABLE code_research_jobs IS 'Stores async research job metadata and status';
COMMENT ON COLUMN code_research_jobs.id IS 'Unique job identifier (UUID)';
COMMENT ON COLUMN code_research_jobs.status IS 'Current job status: pending, processing, completed, failed, cancelled';
COMMENT ON COLUMN code_research_jobs.progress IS 'Human-readable progress indicator (e.g., "5/13 sections complete")';
COMMENT ON COLUMN code_research_jobs.address IS 'US address being researched';
COMMENT ON COLUMN code_research_jobs.llm_provider IS 'LLM provider for data extraction: openai or gemini';
COMMENT ON COLUMN code_research_jobs.metadata IS 'Optional additional data (JSON)';

COMMENT ON TABLE code_research_research_results IS 'Stores individual section research results for jobs';
COMMENT ON COLUMN code_research_research_results.job_id IS 'Reference to parent job (CASCADE DELETE)';
COMMENT ON COLUMN code_research_research_results.section_name IS 'Name of research section (e.g., wall_signs)';
COMMENT ON COLUMN code_research_research_results.section_data IS 'Full section data as JSON (Pydantic model)';

-- ============================================================
-- Verification Queries
-- ============================================================

-- Check tables were created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name IN ('code_research_jobs', 'code_research_research_results');

-- Check indexes
SELECT indexname FROM pg_indexes 
WHERE tablename IN ('code_research_jobs', 'code_research_research_results');

-- Verify real-time is enabled for jobs table
SELECT schemaname, tablename 
FROM pg_publication_tables 
WHERE pubname = 'supabase_realtime' AND tablename = 'code_research_jobs';

-- ============================================================
-- Sample Data (Optional - for testing)
-- ============================================================

-- Uncomment to insert test data:
/*
INSERT INTO code_research_jobs (address, llm_provider, status, progress) VALUES
    ('123 Main St, Miami, FL', 'openai', 'pending', '0/13 sections'),
    ('456 Oak Ave, Austin, TX', 'gemini', 'processing', '5/13 sections'),
    ('789 Elm St, Portland, OR', 'openai', 'completed', '13/13 sections');

INSERT INTO code_research_research_results (job_id, section_name, section_data) VALUES
    ((SELECT id FROM code_research_jobs LIMIT 1), 'location_information', '{"jurisdiction": {"value": "City of Miami"}}'::jsonb);
*/

-- ============================================================
-- Migration Complete
-- ============================================================

SELECT 'Migration 001 complete! Tables, indexes, and real-time configured.' AS status;
