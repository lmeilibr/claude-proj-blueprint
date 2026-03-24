#!/bin/bash
# Post-commit hook: incrementally index changes into vector DB
# Install: cp scripts/post-commit-index.sh .git/hooks/post-commit && chmod +x .git/hooks/post-commit

if command -v python &> /dev/null && [ -f "memory/index.py" ]; then
    python memory/index.py --incremental &> /dev/null &
    echo "🧠 Memory: indexing in background..."
fi
