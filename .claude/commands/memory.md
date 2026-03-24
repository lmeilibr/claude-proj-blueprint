Long-term memory operations for the project.

Arguments: $ARGUMENTS (subcommand: index | search <query> | stats)

Workflow:
1. If "index": run `python memory/index.py --incremental` to re-index changes
2. If "search <query>": run `python memory/query.py "<query>" --agent-format` and use as context
3. If "stats": run `python memory/query.py --stats` to see chunk counts

After searching, use the results as context for responding to the user.
Always cite the source (file and excerpt) when using information from memory.

If the memory module is not installed, instruct:
  pip install -r memory/requirements.txt
  python memory/index.py
