# Changelog

## 3.0.0

- Added one Python renderer/installer for VS Code, Codex, and OpenCode.
- Added `single` and `multi` profiles with bounded host-specific agent output.
- Removed checked-in portable copies; host packages are generated from canonical
  `skills/` and `examples/` sources.
- Added environment discovery through ignored `.cells-agent/context.json`.
- Made OpenSpec the portable durable workflow backend and host memory optional.
- Regenerated the bundled Spherica and official-doc indexes without private
  source paths.
- Consolidated component research into `cells-components-catalog`, feature
  analysis into `cells-explore`, and composition into `cells-app-architecture`.
- Removed demo, manual-registry, and generic Git/issue skills from the Cells
  runtime.
- Added cross-platform rendering, merge/idempotency, catalog detection, plugin,
  and portability validation.

## 2.x

The previous line introduced host-specific examples, phase skills, indexed
catalogs, and experimental hooks. Version 3 replaces its duplicated portable
trees and mandatory external-memory assumptions.
