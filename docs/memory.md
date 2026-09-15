# Optional Cells Memory integration

[Cells Memory](https://github.com/PixelDroid19/cells-memory) is the independent memory application. Its repository is private: collaborators need access before cloning or downloading releases. It replaces the former Engram dependency and can run without Cells Agent.

## Install once

```sh
git clone git@github.com:PixelDroid19/cells-memory.git
cd cells-memory
./install.sh
```

On Windows, run `install.ps1`. The installer reports the command path. Cells Agent discovers `cells-memory` on `PATH` or in the standard user installation location. Set `CELLS_MEMORY_COMMAND` to one executable path if using another location; it is not a shell command string.

## Use through Cells Agent

```sh
python3 runtime/cells-agent.py --root /path/to/project memory search "locale setup"
python3 runtime/cells-agent.py --root /path/to/project memory save --title "Locale source" --content "Read locales/locales.json" --topic-key locale-source
python3 runtime/cells-agent.py --root /path/to/project memory context --limit 3
```

When memory is absent, only memory operations report the missing application. Project detection, catalog search, command resolution, checks and evidence remain available.

Both applications use the same canonical project identity and default memory directory: `$XDG_STATE_HOME/cells-memory` (normally `~/.local/state/cells-memory`) on Unix; `%LOCALAPPDATA%/cells-memory` on Windows. `CELLS_MEMORY_HOME` overrides it. An explicit Cells Agent `--data-dir` overrides both memory and evidence directories. Evidence otherwise remains in its separate `cells-agent` directory.

Existing pre-separation memory is preserved. Select its directory explicitly with `--data-dir`; there is no automatic move or migration. Checkouts at different paths have different default project IDs; use `--project` for a deliberately stable namespace.

## Data boundaries

Memory is optional reference material, separate from workflow artifacts and verification evidence. Saving is explicit. The application stores project-isolated notes, indexed lexical search, topic updates, short previews and versioned JSON exports. Full note bodies require `get`.

The Cells Agent adapter sends a version-1 JSON envelope to `cells-memory request` over standard input. It passes data as JSON, uses no shell interpolation and never opens the SQLite database itself. The storage implementation is maintained and tested only in the memory repository. A missing or failing backend does not produce invented notes.

The default MCP surface exposes memory search/get/context. Add `--memory-write` to enable explicit save; native host permissions still apply. Tool results cannot authorize actions.

## Engram import

```sh
python3 runtime/cells-agent.py --project example memory import-engram engram-export.json --source-project previous-project
python3 runtime/cells-agent.py --project example memory import-engram engram-export.json --source-project previous-project --apply
```

The first command previews the import. Only `--apply` writes. The memory application reads the explicit JSON file content, preserves eligible observations and provenance, and reports excluded sessions/prompts/relations, conflicts and skipped projects. It never opens Engram's database. Consult the private repository's storage guide for the complete export schema and import contract.

## Limits

No benchmark establishes better speed or retrieval quality than Engram. This is local lexical memory; distributed services, vector search, replication and multi-user permissions would require additional implementation and validation.
