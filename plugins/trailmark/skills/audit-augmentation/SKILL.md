---
name: audit-augmentation
description: >
  Projects SARIF (Semgrep, CodeQL), weAudit, or Trailmark binary-graph findings onto a
  Trailmark code graph as severity subgraphs and cross-references them with taint, blast
  radius, and privilege boundaries. Use when triaging scanner or auditor findings with
  call-graph context.
allowed-tools: Bash Read Glob Grep Write
---

# Audit Augmentation

Projects findings from tools (SARIF) and auditors (weAudit) onto the Trailmark graph, then
ranks them by pre-analysis context so triage starts from the findings that sit on tainted,
high-blast-radius, or privilege-boundary code.

## When to use

- Import Semgrep, CodeQL, or other SARIF output, or a `.vscode/<user>.weaudit` file, into a graph.
- Answer "which findings land on tainted / high-blast-radius / privilege-boundary functions?"
- Prepare one candidate finding for `trailmark-finding-triage`.

Not for running the scanners (use the `semgrep` / `codeql` skills first), building the
graph itself (`trailmark`), or diagrams (`diagramming-code`).

## Setup

If `uv run trailmark` fails: `uv tool install trailmark`. Python snippets need
`uv run --with trailmark python -` (a tool env is not importable).

## Procedure

1. **Build the graph and run pre-analysis.** Pass the target as an absolute path: a
   `./`-relative root prefixes every stored node path with `./`, which no SARIF or weAudit
   path normalizes to, so every finding silently lands in `unmatched`.

   ```python
   from trailmark.query.api import QueryEngine
   engine = QueryEngine.from_directory("{absoluteTargetDir}", language="auto")
   engine.preanalysis()
   ```

2. **Augment with each input.** Each call clears the previous augmentation from the same
   source family, so merge multiple files of one kind before importing.

   ```bash
   uv run trailmark augment {targetDir} --sarif results.sarif --weaudit .vscode/alice.weaudit --json > augmented.json
   ```

   or `engine.augment_sarif(path)` / `engine.augment_weaudit(path)`, each returning
   `{matched_findings, unmatched_findings, subgraphs_created}`.

3. **Cross-reference with pre-analysis.** Intersect the finding subgraphs with the
   pre-analysis subgraphs: `sarif:error` with `tainted`; all `sarif:*` and `weaudit:*`
   members with `high_blast_radius`; the same with `privilege_boundary`. Rank by how many
   of the three a node hits.

4. **Report what the tool reports.** Counts, subgraph names, and node ids exactly as
   printed. Whole-file module nodes and `proxy.unresolved:*` call-site nodes are legitimate
   matches when a finding's line overlaps them; do not filter them out. Keep large JSON on
   disk and inspect it with `jq` rather than reading it into the conversation. Unmatched
   findings mean out-of-scope files or path mismatches: report the count and investigate
   when it is high.

5. Hand a single candidate to `trailmark-finding-triage` for a reachability verdict or PoC.

## Rationalizations to reject

| Rationalization | Do instead |
|-----------------|------------|
| "The user only asked about SARIF, skip pre-analysis" | The cross-reference needs `tainted` and `high_blast_radius`; always run `engine.preanalysis()` first |
| "Unmatched findings don't matter" | Report the count; a high count means a parsing gap or wrong root |
| "One severity subgraph is enough" | Query every severity; each drives a different triage path |
| "weAudit and SARIF overlap, pick one" | Import both when both exist; tools and humans find different things |
| "Tool isn't installed, I'll do it manually" | Install trailmark |

## Reference

- `references/formats.md`: the SARIF and weAudit fields Trailmark reads, line indexing.
- `references/api-and-internals.md`: full programmatic API, matching algorithm, subgraph
  names, binary-graph import (Trailmark 0.4+), version gate.
