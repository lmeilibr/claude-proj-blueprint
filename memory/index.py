"""
Index project files into the vector database for long-term memory.

Usage:
    python memory/index.py                  # Full index
    python memory/index.py --incremental    # Only changed files since last index
    python memory/index.py --source docs/   # Index specific directory
    python memory/index.py --clear          # Clear and re-index everything
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from memory.backends import create_backend

console = Console()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        console.print("[red]config.yaml not found in memory/[/red]")
        sys.exit(1)
    with open(config_path) as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Chunking strategies
# ---------------------------------------------------------------------------

def chunk_by_heading(text: str, filepath: str) -> list[dict]:
    """Split markdown by ## headings. Each section becomes a chunk."""
    chunks = []
    sections = re.split(r'^(#{1,3}\s+.+)$', text, flags=re.MULTILINE)

    current_heading = filepath
    current_body = ""

    for part in sections:
        if re.match(r'^#{1,3}\s+', part):
            if current_body.strip():
                chunks.append({
                    "text": f"# {current_heading}\n\n{current_body.strip()}",
                    "heading": current_heading,
                })
            current_heading = part.strip().lstrip('#').strip()
            current_body = ""
        else:
            current_body += part

    if current_body.strip():
        chunks.append({
            "text": f"# {current_heading}\n\n{current_body.strip()}",
            "heading": current_heading,
        })

    return chunks


def chunk_by_file(text: str, filepath: str) -> list[dict]:
    """Entire file as one chunk."""
    return [{"text": text, "heading": filepath}]


CHUNKERS = {
    "heading": chunk_by_heading,
    "file": chunk_by_file,
}


# ---------------------------------------------------------------------------
# Git log indexing
# ---------------------------------------------------------------------------

def get_git_log(limit: int = 200) -> list[dict]:
    """Get recent git commits as chunks."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{limit}", "--format=%H|||%s|||%an|||%aI"],
            capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    chunks = []
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        parts = line.split('|||')
        if len(parts) != 4:
            continue
        sha, message, author, date = parts
        chunks.append({
            "id": f"git-{sha[:12]}",
            "text": f"Commit: {message}\nAuthor: {author}\nDate: {date}",
            "metadata": {
                "source": f"git:{sha[:12]}",
                "type": "git_commit",
                "title": message[:100],
                "last_modified": date[:10],
            }
        })
    return chunks


# ---------------------------------------------------------------------------
# File discovery and hashing
# ---------------------------------------------------------------------------

def discover_files(sources: list[dict], project_root: Path) -> list[dict]:
    """Find all files matching source patterns."""
    import fnmatch

    files = []
    for source in sources:
        source_path = project_root / source["path"]
        if not source_path.exists():
            continue
        glob_pattern = source.get("glob", "**/*")
        for filepath in source_path.rglob("*"):
            if not filepath.is_file():
                continue
            relative = filepath.relative_to(project_root)
            if fnmatch.fnmatch(str(relative), f"{source['path']}{glob_pattern}"):
                files.append({
                    "path": filepath,
                    "relative": str(relative),
                    "chunk_by": source.get("chunk_by", "file"),
                    "metadata_type": source.get("metadata_type", "unknown"),
                })
    return files


def file_hash(filepath: Path) -> str:
    """SHA-256 hash of file contents."""
    return hashlib.sha256(filepath.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# State management (for incremental indexing)
# ---------------------------------------------------------------------------

STATE_FILE = Path(__file__).parent / ".index_state.json"


def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state: dict):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


# ---------------------------------------------------------------------------
# Main indexing logic
# ---------------------------------------------------------------------------

def index_project(
    incremental: bool = False,
    source_filter: str | None = None,
    clear: bool = False,
):
    config = load_config()
    project_root = Path(__file__).parent.parent.resolve()
    backend_type = config.get("backend", "chroma")

    console.print(f"\n[bold]Indexing project into vector DB[/bold]")
    console.print(f"  Backend: {backend_type}")
    if backend_type == "chroma":
        console.print(f"  Persist: {project_root / config.get('persist_dir', 'memory/.chroma')}")
    elif backend_type == "pgvector":
        pg = config.get("pgvector", {})
        console.print(f"  Host: {pg.get('host', 'localhost')}:{pg.get('port', 5432)}/{pg.get('database', '?')}")
    console.print(f"  Model: {config['embedding_model']}")
    console.print()

    # Initialize backend
    if clear:
        console.print("[yellow]Clearing existing data...[/yellow]")
    store = create_backend(config)

    # Load embedding model
    console.print(f"Loading embedding model: {config['embedding_model']}...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(config["embedding_model"])

    # Load state for incremental
    state = load_state() if incremental else {}
    new_state = {}

    # Discover files
    sources = config.get("sources", [])
    if source_filter:
        sources = [s for s in sources if source_filter in s["path"]]

    files = discover_files(sources, project_root)
    console.print(f"Found [bold]{len(files)}[/bold] files to index\n")

    indexed = 0
    skipped = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Indexing...", total=len(files))

        for file_info in files:
            filepath = file_info["path"]
            relative = file_info["relative"]
            progress.update(task, description=f"Indexing {relative}")

            # Skip if unchanged (incremental mode)
            current_hash = file_hash(filepath)
            if incremental and state.get(relative) == current_hash:
                new_state[relative] = current_hash
                skipped += 1
                progress.advance(task)
                continue

            # Read and chunk
            try:
                text = filepath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                progress.advance(task)
                continue

            if not text.strip():
                progress.advance(task)
                continue

            chunker = CHUNKERS.get(file_info["chunk_by"], chunk_by_file)
            chunks = chunker(text, relative)

            # Delete old chunks for this file
            try:
                existing = store.get(where={"source": relative})
                if existing["ids"]:
                    store.delete(ids=existing["ids"])
            except Exception:
                pass

            # Embed and store
            for i, chunk in enumerate(chunks):
                chunk_id = f"{relative}::chunk-{i}"
                chunk_text = chunk["text"][:8000]  # Chroma limit safety

                try:
                    embedding = model.encode(chunk_text).tolist()
                except Exception:
                    continue

                last_modified = datetime.fromtimestamp(
                    filepath.stat().st_mtime
                ).strftime("%Y-%m-%d")

                store.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk_text],
                    metadatas=[{
                        "source": relative,
                        "type": file_info["metadata_type"],
                        "title": chunk.get("heading", relative),
                        "last_modified": last_modified,
                        "chunk_index": i,
                    }],
                )

            new_state[relative] = current_hash
            indexed += 1
            progress.advance(task)

        # Index git log
        if config.get("index_git_log", False) and not source_filter:
            progress.update(task, description="Indexing git history...")
            git_chunks = get_git_log(config.get("git_log_limit", 200))

            # Clear old git chunks
            try:
                existing = store.get(where={"type": "git_commit"})
                if existing["ids"]:
                    store.delete(ids=existing["ids"])
            except Exception:
                pass

            for chunk in git_chunks:
                try:
                    embedding = model.encode(chunk["text"]).tolist()
                    store.add(
                        ids=[chunk["id"]],
                        embeddings=[embedding],
                        documents=[chunk["text"]],
                        metadatas=[chunk["metadata"]],
                    )
                except Exception:
                    continue

            console.print(f"  Git commits indexed: {len(git_chunks)}")

    # Save state
    save_state(new_state)

    total = store.count()
    console.print(f"\n[bold green]Done![/bold green]")
    console.print(f"  Indexed: {indexed} files")
    console.print(f"  Skipped: {skipped} files (unchanged)")
    console.print(f"  Total chunks in DB: {total}")
    console.print(f"  State saved to: {STATE_FILE.name}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index project into vector DB")
    parser.add_argument("--incremental", action="store_true",
                        help="Only index changed files")
    parser.add_argument("--source", type=str, default=None,
                        help="Filter to specific source path (e.g. docs/)")
    parser.add_argument("--clear", action="store_true",
                        help="Clear existing index before re-indexing")
    args = parser.parse_args()

    index_project(
        incremental=args.incremental,
        source_filter=args.source,
        clear=args.clear,
    )
