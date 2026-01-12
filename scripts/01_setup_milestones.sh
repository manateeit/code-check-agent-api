#!/bin/bash
set -e

echo "🎯 Creating GitHub Milestones for TDD Phases..."

REPO="manateeit/code-check-agent-api"

# Calculate due dates (each phase = 1 week)
# Handle both macOS (BSD date) and Linux (GNU date)
if date -v+7d > /dev/null 2>&1; then
  # macOS
  WEEK1=$(date -v+7d +%Y-%m-%d)
  WEEK2=$(date -v+14d +%Y-%m-%d)
  WEEK3=$(date -v+21d +%Y-%m-%d)
  WEEK4=$(date -v+28d +%Y-%m-%d)
  WEEK5=$(date -v+35d +%Y-%m-%d)
  WEEK6=$(date -v+42d +%Y-%m-%d)
  WEEK7=$(date -v+49d +%Y-%m-%d)
else
  # Linux
  WEEK1=$(date -d "+7 days" +%Y-%m-%d)
  WEEK2=$(date -d "+14 days" +%Y-%m-%d)
  WEEK3=$(date -d "+21 days" +%Y-%m-%d)
  WEEK4=$(date -d "+28 days" +%Y-%m-%d)
  WEEK5=$(date -d "+35 days" +%Y-%m-%d)
  WEEK6=$(date -d "+42 days" +%Y-%m-%d)
  WEEK7=$(date -d "+49 days" +%Y-%m-%d)
fi

echo "Creating Phase 0 milestone..."
gh api repos/$REPO/milestones -X POST \
  -f title="Phase 0: Setup & Dependencies" \
  -f description="Setup test infrastructure, install dependencies, verify all connections work. Exit: 5 tests pass." \
  -f due_on="${WEEK1}T23:59:59Z" \
  -f state="open" 2>/dev/null || echo "  ⚠️  Milestone may already exist"

echo "Creating Phase 1 milestone..."
gh api repos/$REPO/milestones -X POST \
  -f title="Phase 1: Database Schema + Client" \
  -f description="Create Supabase tables, implement CRUD operations, test database layer. Exit: 9 tests pass." \
  -f due_on="${WEEK2}T23:59:59Z" \
  -f state="open" 2>/dev/null || echo "  ⚠️  Milestone may already exist"

echo "Creating Phase 2 milestone..."
gh api repos/$REPO/milestones -X POST \
  -f title="Phase 2: Async Job API Endpoints" \
  -f description="Create FastAPI endpoints for async job submission and status retrieval. Exit: 8 tests pass." \
  -f due_on="${WEEK3}T23:59:59Z" \
  -f state="open" 2>/dev/null || echo "  ⚠️  Milestone may already exist"

echo "Creating Phase 3 milestone..."
gh api repos/$REPO/milestones -X POST \
  -f title="Phase 3: Background Worker (Modal)" \
  -f description="Create Modal worker, integrate with API, deploy to Modal. Exit: 4 tests pass + worker deployed." \
  -f due_on="${WEEK4}T23:59:59Z" \
  -f state="open" 2>/dev/null || echo "  ⚠️  Milestone may already exist"

echo "Creating Phase 4 milestone..."
gh api repos/$REPO/milestones -X POST \
  -f title="Phase 4: Real-Time Progress Updates" \
  -f description="Enable Supabase real-time, create WebSocket endpoint, test streaming updates. Exit: 2 tests pass." \
  -f due_on="${WEEK5}T23:59:59Z" \
  -f state="open" 2>/dev/null || echo "  ⚠️  Milestone may already exist"

echo "Creating Phase 5 milestone..."
gh api repos/$REPO/milestones -X POST \
  -f title="Phase 5: Error Handling + Retries" \
  -f description="Robust error handling, automatic retries, failure recovery, monitoring. Exit: 8 tests pass." \
  -f due_on="${WEEK6}T23:59:59Z" \
  -f state="open" 2>/dev/null || echo "  ⚠️  Milestone may already exist"

echo "Creating Phase 6 milestone..."
gh api repos/$REPO/milestones -X POST \
  -f title="Phase 6: Backward Compatibility" \
  -f description="Keep old endpoints working, write migration guide, deprecation notices. Exit: 6 tests pass." \
  -f due_on="${WEEK7}T23:59:59Z" \
  -f state="open" 2>/dev/null || echo "  ⚠️  Milestone may already exist"

echo "Creating Phase 7 milestone..."
gh api repos/$REPO/milestones -X POST \
  -f title="Phase 7: Load Testing + Optimization" \
  -f description="Performance testing, optimization, production readiness. Exit: 7 tests pass + load test." \
  -f due_on="${WEEK7}T23:59:59Z" \
  -f state="open" 2>/dev/null || echo "  ⚠️  Milestone may already exist"

echo "✅ All 8 milestones created successfully!"
