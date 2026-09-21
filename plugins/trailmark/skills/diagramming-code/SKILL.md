---
name: diagramming-code
description: >
  Renders Mermaid diagrams from a Trailmark code graph: call graphs, class hierarchies,
  module dependencies, class containment, complexity heatmaps, and entrypoint-to-target
  data flow. Use when visualizing code architecture or attack surface paths.
---

# Diagramming Code

One command renders the diagram; your job is choosing `--type` and `--focus`. **Never
hand-write Mermaid from reading source.** The graph is parsed, so the diagram is accurate;
prose-derived diagrams miss calls and invent edges.

## When to use

Any request to *see* code structure: who calls what, inheritance, module imports, class
members, complexity hotspots, or paths from entrypoints to a sensitive function. Not for
querying the graph without a picture (use `trailmark`) or for diagrams not derived from code.

## Procedure

1. **Pick the type** from the request:

   | Question | `--type` |
   |---|---|
   | Who calls what? | `call-graph` |
   | Class inheritance? | `class-hierarchy` |
   | Module dependencies? | `module-deps` |
   | Class members and structure? | `containment` |
   | Where is complexity highest? | `complexity` |
   | Path from input to a function? | `data-flow` |

2. **Run it** — one command, no setup step:

   ```bash
   trailmark diagram --target {targetDir} --language auto --type <type> [--focus <node>] [--depth 2] [--direction TB|LR]
   ```

   If `trailmark` is not found, or says `diagram` is an unknown command: `uv tool install --force
   trailmark`, then rerun. The command parses the target itself; do not build a graph or run
   pre-analysis first — it cannot use them.

3. **Focus.** `call-graph` and `data-flow` need `--focus <function>` on any non-trivial repo.
   If the command reports `node '<x>' not found`, choose from the list it prints instead of
   guessing again. `data-flow` without `--focus` targets the top complexity hotspots. Use
   `--direction LR` for dependency chains; raise `--depth` only if the result is too sparse
   (the command warns above 100 nodes).

4. **Deliver.** Output is raw Mermaid starting with `flowchart` or `classDiagram`. Wrap it in
   a ```` ```mermaid ```` fence, or write it to the file the user asked for. If it is empty or
   malformed, see `references/mermaid-syntax.md`.

## Rationalizations to reject

| Rationalization | Reality |
|---|---|
| "I'll sketch the Mermaid from the source, it's faster." | Hand-drawn diagrams miss calls and invent edges. Run the command. |
| "I should build the graph or run pre-analysis first." | The command parses on its own and cannot see an engine built in another process. Skip it. |
| "Let me check which Trailmark version is installed." | `trailmark diagram` is native in current Trailmark releases. Just run it. |
| "The diagram is huge; I'll trim nodes by hand." | Use `--focus` and `--depth`. |

## Reference

- `references/diagram-types.md` — what each type shows, with examples
- `references/mermaid-syntax.md` — ID sanitization, escaping, styling, pitfalls
