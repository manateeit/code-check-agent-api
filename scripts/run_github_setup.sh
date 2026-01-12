#!/bin/bash
set -e

echo "🚀 Starting GitHub Project Setup..."
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Step 1/3: Creating labels..."
bash "$SCRIPT_DIR/00_setup_labels.sh"
echo ""

echo "Step 2/3: Creating milestones..."
bash "$SCRIPT_DIR/01_setup_milestones.sh"
echo ""

echo "Step 3/3: Creating Phase 0 issues..."
bash "$SCRIPT_DIR/02_create_phase0_issues.sh"
echo ""

echo "✅ GitHub setup complete!"
echo ""
echo "📊 Summary:"
echo "  - 12 labels created"
echo "  - 8 milestones created"
echo "  - 7 Phase 0 issues created"
echo ""
echo "🔗 View your project:"
echo "  https://github.com/manateeit/code-check-agent-api/issues"
echo ""
echo "Next steps:"
echo "  1. Review issues in GitHub"
echo "  2. Start Phase 0 implementation"
echo "  3. Run: cd .. && pytest tests/test_setup.py -v"
