# GitHub Project Setup Scripts

This directory contains scripts to set up the complete GitHub project structure for the TDD implementation plan.

## 📋 Scripts Overview

| Script | Purpose | Creates |
|--------|---------|---------|
| `00_setup_labels.sh` | Create phase and utility labels | 12 labels |
| `01_setup_milestones.sh` | Create phase milestones | 8 milestones |
| `02_create_phase0_issues.sh` | Create Phase 0 issues | 7 issues |
| `run_github_setup.sh` | **Master script - run this** | Everything |

## 🚀 Quick Start

### One-Command Setup

```bash
cd scripts
./run_github_setup.sh
```

This will:
1. ✅ Create all labels (color-coded by phase)
2. ✅ Create 8 milestones (one per phase)
3. ✅ Create 7 Phase 0 issues (auto-assigned to you)

### Individual Scripts

If you want to run steps individually:

```bash
# Step 1: Labels
./00_setup_labels.sh

# Step 2: Milestones
./01_setup_milestones.sh

# Step 3: Phase 0 Issues
./02_create_phase0_issues.sh
```

## 📊 What Gets Created

### Labels (12 total)
- **Phase labels** (8): phase-0-setup through phase-7-perf
- **Utility labels** (4): tdd, gate, test, implementation

### Milestones (8 total)
- Phase 0: Setup & Dependencies (due in 1 week)
- Phase 1: Database Schema + Client (due in 2 weeks)
- Phase 2-7: (incremental weekly deadlines)

### Issues (Phase 0 - 7 total)
- 1 implementation issue
- 5 test issues
- 1 gate issue (exit criteria)

## ⚙️ Prerequisites

1. **GitHub CLI installed**: `brew install gh` (macOS) or see https://cli.github.com
2. **Authenticated**: `gh auth login`
3. **Correct repository**: `manateeit/code-check-agent-api`

## 🔍 Verification

After running the setup:

```bash
# List all labels
gh label list --repo manateeit/code-check-agent-api

# List all milestones
gh api repos/manateeit/code-check-agent-api/milestones

# List Phase 0 issues
gh issue list --repo manateeit/code-check-agent-api --label "phase-0-setup"
```

## 🚨 Troubleshooting

### "gh: command not found"
Install GitHub CLI: https://cli.github.com

### "HTTP 401: Bad credentials"
Authenticate: `gh auth login`

### "Label already exists"
This is OK - script will skip existing labels

### "Milestone already exists"
This is OK - existing milestones are preserved

## 🔗 Next Steps

After GitHub setup completes:

1. **Review issues**: https://github.com/manateeit/code-check-agent-api/issues
2. **Start Phase 0**: Begin with the "[Phase 0] Setup Test Infrastructure" issue
3. **Run tests**: `pytest tests/test_setup.py -v`

## 📚 Additional Resources

- TDD Plan: See `AGENTS.md` for full plan
- Phase Details: Check each issue for detailed instructions
- GitHub Project: Will be created in later scripts
