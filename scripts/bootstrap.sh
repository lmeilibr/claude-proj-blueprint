#!/bin/bash
# Bootstrap script for Claude Code Project Template
# Usage: ./scripts/bootstrap.sh --level [1|2|3|4]

set -e

LEVEL=2  # default

while [[ $# -gt 0 ]]; do
  case $1 in
    --level) LEVEL="$2"; shift 2 ;;
    *) echo "Usage: ./scripts/bootstrap.sh --level [1|2|3|4]"; exit 1 ;;
  esac
done

echo "🚀 Bootstrapping project at Level $LEVEL"
echo ""

# ============================================================
# L1: CLAUDE.md + settings + docs structure
# ============================================================
echo "📋 L1: Setting up CLAUDE.md and basic structure..."

if [ ! -f "CLAUDE.md" ]; then
  echo "   ⚠️  CLAUDE.md not found — make sure you're in the project root"
  exit 1
fi

# Ensure basic dirs exist
mkdir -p src docs/{product,architecture,specs,runbooks/post-mortems}

echo "   ✅ Basic structure ready"
echo "   📝 TODO: Fill in [SPEC] markers in CLAUDE.md"
echo "   📝 TODO: Fill in docs/product/vision.md"
echo ""

if [ "$LEVEL" -lt 2 ]; then
  echo "✅ Level 1 setup complete!"
  echo ""
  echo "Daily workflow:"
  echo "  cd $(basename $PWD) && claude"
  echo "  → Describe what you need"
  echo "  → Claude reads CLAUDE.md automatically"
  exit 0
fi

# ============================================================
# L2: Skills + Commands
# ============================================================
echo "🧠 L2: Setting up skills and commands..."

mkdir -p .claude/{skills,commands}

# Count skills
SKILL_COUNT=$(find .claude/skills -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
echo "   📦 $SKILL_COUNT skills found"

# Count commands
CMD_COUNT=$(find .claude/commands -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "   ⚡ $CMD_COUNT commands found"

echo "   📝 TODO: Create project-specific skills in .claude/skills/"
echo "   📝 TODO: Use .claude/skills/_template-skill/SKILL.md as template"
echo ""

if [ "$LEVEL" -lt 3 ]; then
  echo "✅ Level 2 setup complete!"
  echo ""
  echo "Daily workflow:"
  echo "  cd $(basename $PWD) && claude"
  echo "  → Shift+Tab+Tab: Plan Mode"
  echo "  → Describe feature intent"
  echo "  → Shift+Tab: Auto Accept"
  echo "  → /compact to compress context"
  echo "  → Commit frequently, new session per feature"
  exit 0
fi

# ============================================================
# L3: Hooks
# ============================================================
echo "🔒 L3: Setting up hooks..."

if [ -f ".claude/hooks.json" ]; then
  echo "   ✅ hooks.json found"
else
  echo "   ⚠️  hooks.json not found — create it in .claude/"
fi

# Make scripts executable
chmod +x scripts/*.sh 2>/dev/null || true
echo "   ✅ Scripts made executable"

echo "   📝 TODO: Test hooks with a sample file write"
echo "   📝 TODO: Customize lint-check.sh for your stack"
echo ""

if [ "$LEVEL" -lt 4 ]; then
  echo "✅ Level 3 setup complete!"
  echo ""
  echo "Daily workflow:"
  echo "  cd $(basename $PWD) && claude"
  echo "  → Same as L2, plus:"
  echo "  → Hooks run automatically on file write and bash"
  echo "  → /spec-review src/ to run agent review"
  exit 0
fi

# ============================================================
# L4: Agents + Agent Teams + Long-term Memory
# ============================================================
echo "🤖 L4: Setting up agents, memory, and autonomous capabilities..."

mkdir -p .claude/agents

AGENT_COUNT=$(find .claude/agents -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "   🕵️ $AGENT_COUNT agents found"

# Memory layer
echo ""
echo "🧠 L4: Setting up long-term memory..."
if [ -f "memory/index.py" ]; then
  echo "   ✅ Memory module found"

  # Check if dependencies are installed
  if python3 -c "import chromadb" 2>/dev/null; then
    echo "   ✅ Dependencies installed"

    # Auto-index if not already done
    if [ ! -d "memory/.chroma" ]; then
      echo "   📦 Running initial index..."
      python3 memory/index.py 2>/dev/null && echo "   ✅ Initial index complete" || echo "   ⚠️  Index failed — run manually: python memory/index.py"
    else
      echo "   ✅ Vector DB exists (memory/.chroma/)"
    fi
  else
    echo "   ⚠️  Dependencies not installed"
    echo "   📝 TODO: pip install -r memory/requirements.txt"
  fi

  # Install post-commit hook
  if [ -d ".git" ] && [ -f "scripts/post-commit-index.sh" ]; then
    cp scripts/post-commit-index.sh .git/hooks/post-commit
    chmod +x .git/hooks/post-commit
    echo "   ✅ Post-commit hook installed (auto-index)"
  fi
else
  echo "   ⚠️  memory/ module not found"
fi
echo ""
echo "   📝 TODO: Enable agent teams:"
echo "      export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1"
echo "   📝 TODO: Customize agents in .claude/agents/"
echo "   📝 TODO: Set up self-healing CI pipeline"
echo ""

echo "✅ Level 4 setup complete!"
echo ""
echo "Daily workflow:"
echo "  cd $(basename $PWD) && claude"
echo "  → Same as L3, plus:"
echo "  → python memory/query.py 'how did we handle X' — semantic search"
echo "  → python memory/index.py --incremental — re-index after changes"
echo "  → 'Create an agent team for [task]'"
echo "  → Author-Critic loop runs automatically"

echo ""
echo "================================================"
echo "📊 Summary"
echo "================================================"
echo "Level:    $LEVEL"
echo "Skills:   $SKILL_COUNT"
echo "Commands: $CMD_COUNT"
echo "Agents:   $AGENT_COUNT"
echo "Hooks:    $([ -f '.claude/hooks.json' ] && echo 'Active' || echo 'Not configured')"
echo "Memory:   $([ -d 'memory/.chroma' ] && echo 'Indexed' || echo 'Not indexed')"
echo ""
echo "Next: Search for [SPEC] markers and fill them in:"
echo "  grep -r '\[SPEC\]' CLAUDE.md docs/ .claude/ | head -20"
