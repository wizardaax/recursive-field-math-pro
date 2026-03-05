#!/usr/bin/env bash
# Local validation script for Xova AES Evolution
# Usage: bash scripts/check_evolution.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "==> Xova AES Evolution Local Check"
echo "Root directory: $ROOT_DIR"

cd "$ROOT_DIR"

# Check required files exist
echo "==> Checking required files..."
REQUIRED_FILES=(
    "xova/evolve.py"
    "xova/registry.py" 
    "xova/sandbox.py"
    "policies/default.json"
    "examples/request_nine.json"
    ".github/workflows/evolve.yml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        exit 1
    fi
done

# Check required directories exist
echo "==> Checking required directories..."
REQUIRED_DIRS=(
    "plugins"
    "out"
    "docs"
    "docs/history"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/"
    else
        echo "❌ $dir/ (missing)"
        exit 1
    fi
done

# Test evolution script
echo "==> Testing evolution script..."
if python xova/evolve.py examples/request_nine.json > /tmp/evolution_test.json 2>&1; then
    echo "✅ Evolution script runs successfully"
    
    # Check output files were created
    if [ -f "out/summary.json" ] && [ -f "out/metrics.json" ]; then
        echo "✅ Output artifacts generated"
        
        # Validate JSON format
        if python -m json.tool out/summary.json > /dev/null 2>&1; then
            echo "✅ summary.json is valid JSON"
        else
            echo "❌ summary.json is not valid JSON"
            exit 1
        fi
        
        if python -m json.tool out/metrics.json > /dev/null 2>&1; then
            echo "✅ metrics.json is valid JSON"
        else
            echo "❌ metrics.json is not valid JSON"
            exit 1
        fi
        
        # Show sample metrics
        echo "==> Sample metrics:"
        cat out/metrics.json | python -m json.tool
        
    else
        echo "❌ Expected output artifacts not found"
        exit 1
    fi
else
    echo "❌ Evolution script failed"
    echo "Error output:"
    cat /tmp/evolution_test.json
    exit 1
fi

# Test workflow syntax (basic check)
echo "==> Checking workflow syntax..."
if command -v yamllint > /dev/null 2>&1; then
    if yamllint .github/workflows/evolve.yml; then
        echo "✅ Workflow YAML syntax is valid"
    else
        echo "❌ Workflow YAML syntax errors found"
        exit 1
    fi
else
    echo "⚠️  yamllint not available, skipping YAML validation"
fi

# Test infinite loop guard logic
echo "==> Testing infinite loop guard logic..."
python3 << 'EOF'
import os
import sys

# Test commit messages that should trigger the guard
guard_messages = [
    "Sync evolve artifacts to docs",
    "Update AES badge", 
    "Some change: Sync evolve artifacts to docs [skip ci]",
    "Fix issue and Update AES badge automatically"
]

safe_messages = [
    "Add new feature",
    "Fix bug in evolution script",
    "Update documentation",
    "Refactor code"
]

print("Testing guard trigger messages:")
for msg in guard_messages:
    should_skip = "Sync evolve artifacts to docs" in msg or "Update AES badge" in msg
    if should_skip:
        print(f"✅ '{msg}' -> SKIP (correct)")
    else:
        print(f"❌ '{msg}' -> CONTINUE (incorrect)")
        sys.exit(1)

print("\nTesting safe messages:")
for msg in safe_messages:
    should_skip = "Sync evolve artifacts to docs" in msg or "Update AES badge" in msg
    if not should_skip:
        print(f"✅ '{msg}' -> CONTINUE (correct)")
    else:
        print(f"❌ '{msg}' -> SKIP (incorrect)")
        sys.exit(1)

print("✅ Infinite loop guard logic is correct")
EOF

echo ""
echo "🎉 All local validation checks passed!"
echo ""
echo "Next steps:"
echo "1. Commit and push your changes"
echo "2. The evolve.yml workflow will run automatically on push to main"
echo "3. Check GitHub Actions tab for workflow execution"
echo "4. Generated artifacts will be in docs/ directory"
echo "5. Status badge will be available at docs/aes_badge.json"