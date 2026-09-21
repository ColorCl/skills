---
name: trailmark-structural
description: Runs full Trailmark structural analysis for codebase hotspots, taint and blast radius, privilege boundaries, attack surface, proxy nodes, subgraphs, and type references. Use for detailed structural data or Vivisect prioritization.
allowed-tools: Bash Read Grep Glob
---

# Trailmark Structural Analysis

Run the bundled script; never reproduce its Python logic in a shell heredoc.

```bash
uv run {baseDir}/scripts/structural.py "{args}" --out "{args}/.trailmark/structural.json" --compact
```

The command prints a small summary and writes the full evidence to
`{args}/.trailmark/structural.json`. Use `jq` to read only the fields needed for the request.

## Required handling

- If `languages` is empty, report that Trailmark found no supported languages and stop.
- Empty pass output is normal. Return the summary and do not treat an empty subgraph as a failure.
- The script uses compatibility probes for newer Trailmark fields. Preserve all reported
  `attack_surface` attributes unchanged because downstream ranking consumes them.
- Do not install Trailmark or replace this analysis with manual code review. If the command cannot run,
  report the installation gap.

Use `--limit N` to bound evidence samples; the full payload remains on disk. Use the main `trailmark`
skill for ad-hoc graph queries and `trailmark-summary` for a quick overview only.
