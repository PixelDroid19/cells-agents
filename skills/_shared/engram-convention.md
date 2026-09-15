# Legacy Engram Migration

Engram is no longer an active Cells workflow or memory backend. New work uses optional LocalMemory for user-approved reference material and `none` or `openspec` for workflow artifacts.

Do not require `mem_search`, `mem_get_observation`, `mem_save`, or any other `mem_*` integration to start, edit, test, or complete a Cells task.

If a user explicitly requests migration of an Engram export, use the supported `cells-agent memory import-engram` command family. Migration is opt-in, preserves the source export, and does not turn imported memories into verification evidence.

See the [memory documentation](../../docs/memory.md) for LocalMemory behavior, data handling, and migration limits.
