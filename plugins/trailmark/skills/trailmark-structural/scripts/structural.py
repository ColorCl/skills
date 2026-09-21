#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["trailmark"]
# ///
"""Run Trailmark preanalysis and keep the large payload out of chat context."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from trailmark.parse import detect_languages
except ModuleNotFoundError:  # Trailmark 0.2 compatibility
    from trailmark.query.api import detect_languages
from trailmark.query.api import QueryEngine


def summarized_subgraph(engine: QueryEngine, name: str, limit: int) -> dict[str, object]:
    nodes = engine.subgraph(name)
    result: dict[str, object] = {
        "count": len(nodes),
        "sample_ids": [node["id"] for node in nodes[:limit]],
    }
    if hasattr(engine, "subgraph_edges"):
        result["edge_count"] = len(engine.subgraph_edges(name))
    return result


def build_payload(target: str, limit: int) -> dict[str, object]:
    languages = detect_languages(target)
    if not languages:
        return {"languages": [], "error": "Trailmark found no supported languages under target"}

    engine = QueryEngine.from_directory(target, language="auto")
    preanalysis = engine.preanalysis()
    graph = json.loads(engine.to_json())
    nodes = graph.get("nodes", {})
    payload: dict[str, object] = {
        "languages": languages,
        "summary": engine.summary(),
        "preanalysis": preanalysis,
        "attack_surface": engine.attack_surface()[:limit],
        "hotspots": engine.complexity_hotspots(10)[:limit],
        "proxy_nodes": [
            node_id
            for node_id, node in nodes.items()
            if node.get("kind") == "proxy" or node.get("origin") == "proxy"
        ][:limit],
        "subgraphs": {
            name: summarized_subgraph(engine, name, limit) for name in engine.subgraph_names()
        },
    }
    if hasattr(engine, "type_references"):
        payload["type_reference_samples"] = {
            node_id: engine.type_references(node_id)[:10] for node_id in list(nodes)[:limit]
        }
    return payload


def compact_summary(payload: dict[str, object], output: Path) -> dict[str, object]:
    subgraphs = payload.get("subgraphs", {})
    return {
        "languages": payload.get("languages", []),
        "summary": payload.get("summary", {}),
        "hotspot_count": len(payload.get("hotspots", [])),
        "attack_surface_count": len(payload.get("attack_surface", [])),
        "proxy_node_count": len(payload.get("proxy_nodes", [])),
        "subgraph_counts": {name: data["count"] for name, data in subgraphs.items()},
        "full_payload": str(output),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--compact", action="store_true", help="print one-line JSON summary")
    parser.add_argument("--out", default=".trailmark/structural.json")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")

    payload = build_payload(args.target, args.limit)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n")
    summary = compact_summary(payload, output)
    print(json.dumps(summary, separators=(",", ":") if args.compact else None))


if __name__ == "__main__":
    main()
