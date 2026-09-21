# Programmatic API, Matching Rules, and Binary Import

## Contents

- Programmatic API
- Version gate (binary graphs, repository links)
- Annotation format
- Subgraphs created
- How matching works
- Binary graph JSON shape

## Programmatic API

```python
from trailmark.query.api import QueryEngine

engine = QueryEngine.from_directory("{absoluteTargetDir}", language="auto")
engine.preanalysis()                                     # required before cross-referencing

result = engine.augment_sarif("results.sarif")
# {"matched_findings": 12, "unmatched_findings": 3, "subgraphs_created": [...]}
result = engine.augment_weaudit(".vscode/alice.weaudit")

engine.findings()                    # all nodes carrying finding annotations
engine.subgraph("sarif:error")       # high-severity SARIF nodes
engine.subgraph("weaudit:high")
engine.subgraph("sarif:semgrep")     # by tool name
engine.subgraph_names()               # every named subgraph on the graph
engine.annotations_of("module:function_name")
```

Pass the target directory as an absolute path. A `./`-relative root makes every stored node
path start with `./`, which no SARIF or weAudit path normalizes to, and every finding lands
in `unmatched`.

Each `augment_*` call clears the previous augmentation from the same source family
(`sarif:` or `weaudit:`) before importing, so multiple files of one kind must be merged
first. If auto-detection picks the wrong parser, pass an explicit language or a
comma-separated list such as `python,rust`.

## Version gate

SARIF and weAudit augmentation are available from Trailmark 0.2. Binary graph augmentation
needs 0.4.0+:

```python
if not hasattr(engine, "augment_binary"):
    raise RuntimeError("Binary augmentation requires Trailmark >= 0.4.0")
result = engine.augment_binary("binary_graph.json")
```

Binary graph augmentation is programmatic only; do not invent a CLI flag if
`trailmark augment --help` does not show one. On 0.5.0+, known links between source
functions and imported binary or external endpoints can be declared once in
`.trailmark/links.toml` (see the `trailmark` skill's Repository Links section) instead of
being re-derived per session; declared external endpoints materialize as
`proxy.external:<symbol>` nodes on every parse.

## Annotation format

- Kind: `finding` (tool-generated) or `audit_note` (weAudit `entryType` 1).
- Source: `sarif:<tool_name>` or `weaudit:<author>`.
- Description: `[SEVERITY] rule-id: message (tool)` for SARIF;
  `[SEVERITY] label (type) - description [author]` for weAudit.

## Subgraphs created

| Subgraph | Contents |
|----------|----------|
| `sarif:error` / `sarif:warning` / `sarif:note` | Nodes with SARIF findings at that level (a missing `level` defaults to `warning`) |
| `sarif:<tool>` | Nodes flagged by a specific tool (`tool.driver.name`) |
| `weaudit:high` / `weaudit:medium` / `weaudit:low` / `weaudit:informational` | Nodes with weAudit findings at that severity |
| `weaudit:findings` | All weAudit findings (`entryType` 0) |
| `weaudit:notes` | All weAudit notes (`entryType` 1) |
| `binary:<artifact>` | Binary function nodes imported from a 0.4+ binary graph |

A subgraph is only created when at least one finding of that class matched a node.

Pre-analysis separately creates `tainted`, `high_blast_radius` (>= 10 downstream
descendants), `privilege_boundary`, `entrypoints`, `entrypoints:<trust_level>`, and
`entrypoint_reachable`.

## How matching works

1. The finding's path is normalized relative to the graph's `root_path`. Relative paths,
   absolute paths, and `file://` URIs are accepted; any other URI scheme (for example
   `https://`) never matches.
2. Every node whose `location.file_path` equals the normalized path and whose line range
   overlaps the finding's range is selected. Whole-file module nodes and
   `proxy.unresolved:*` call-site nodes have locations too, so a single-line finding
   routinely matches a function, its module, and any proxy node on that line. All are
   annotated.
3. Matches are ordered tightest span first.
4. A finding whose location overlaps no node counts as unmatched. `resolvedEntries` in a
   weAudit file are imported alongside `treeEntries`.

weAudit lines are 0-indexed; Trailmark adds 1 to `startLine` and `endLine` on import.

## Binary graph JSON shape (0.4+)

```json
{
  "artifact": {"name": "libexample", "architecture": "x86_64", "sha256": "..."},
  "functions": [
    {"symbol": "parse_packet", "address": "0x401000",
     "source": {"file": "src/parser.c", "line": 42}}
  ],
  "calls": [
    {"source": "parse_packet", "target": "malloc", "confidence": "inferred"}
  ]
}
```

Imports create `origin=binary` function nodes, `origin=proxy` external proxy nodes for
unresolved binary calls, and inferred `corresponds_to` edges when a binary function maps
back to a source node.
