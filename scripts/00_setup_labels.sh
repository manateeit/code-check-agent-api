#!/bin/bash
set -e

echo "🏷️  Creating GitHub Labels for TDD Phases..."

REPO="manateeit/code-check-agent-api"

# Color scheme (Material Design inspired)
COLOR_PHASE0="d4c5f9"  # Light purple - Setup
COLOR_PHASE1="c2e0c6"  # Light green - Database
COLOR_PHASE2="bfdadc"  # Light blue - API
COLOR_PHASE3="fef2c0"  # Light yellow - Worker
COLOR_PHASE4="fed7d7"  # Light red - Real-time
COLOR_PHASE5="fbb360"  # Orange - Errors
COLOR_PHASE6="d4a5a5"  # Mauve - Compatibility
COLOR_PHASE7="c5f2ff"  # Cyan - Performance

# Phase labels
echo "Creating phase labels..."
gh label create "phase-0-setup" \
  --color "$COLOR_PHASE0" \
  --description "Phase 0: Setup & Dependencies" \
  --repo "$REPO" --force

gh label create "phase-1-database" \
  --color "$COLOR_PHASE1" \
  --description "Phase 1: Database Schema + Client" \
  --repo "$REPO" --force

gh label create "phase-2-api" \
  --color "$COLOR_PHASE2" \
  --description "Phase 2: Async Job API Endpoints" \
  --repo "$REPO" --force

gh label create "phase-3-worker" \
  --color "$COLOR_PHASE3" \
  --description "Phase 3: Background Worker (Modal)" \
  --repo "$REPO" --force

gh label create "phase-4-realtime" \
  --color "$COLOR_PHASE4" \
  --description "Phase 4: Real-Time Progress Updates" \
  --repo "$REPO" --force

gh label create "phase-5-errors" \
  --color "$COLOR_PHASE5" \
  --description "Phase 5: Error Handling + Retries" \
  --repo "$REPO" --force

gh label create "phase-6-compat" \
  --color "$COLOR_PHASE6" \
  --description "Phase 6: Backward Compatibility" \
  --repo "$REPO" --force

gh label create "phase-7-perf" \
  --color "$COLOR_PHASE7" \
  --description "Phase 7: Load Testing + Optimization" \
  --repo "$REPO" --force

# Utility labels
echo "Creating utility labels..."
gh label create "tdd" \
  --color "0e8a16" \
  --description "Test-Driven Development" \
  --repo "$REPO" --force

gh label create "gate" \
  --color "b60205" \
  --description "🚦 Exit Criteria Gate - Must Pass" \
  --repo "$REPO" --force

gh label create "test" \
  --color "fbca04" \
  --description "Unit Test (RED → GREEN)" \
  --repo "$REPO" --force

gh label create "implementation" \
  --color "0075ca" \
  --description "Implementation Code" \
  --repo "$REPO" --force

echo "✅ All 12 labels created successfully!"
