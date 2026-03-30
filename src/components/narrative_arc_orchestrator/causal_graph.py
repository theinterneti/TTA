"""

# Logseq: [[TTA/Components/Narrative_arc_orchestrator/Causal_graph]]
Causal graph utilities extracted to a dedicated module.
ScaleManager remains the orchestrator that uses these operations.
"""

from __future__ import annotations


def add_edge(graph: dict[str, set[str]], src: str, dst: str) -> None:
    graph.setdefault(src, set()).add(dst)


def detect_simple_cycles(graph: dict[str, set[str]]) -> list[str]:
    issues: list[str] = []
    for src, dsts in graph.items():
        issues.extend(
            f"Cycle between {src} and {dst}"
            for dst in dsts
            if dst in graph and src in graph[dst]
        )
    return issues


def remove_weak_link(graph: dict[str, set[str]]) -> None:
    for _, dsts in list(graph.items()):
        if not dsts:
            continue
        dst = next(iter(dsts))
        dsts.remove(dst)


__all__ = ["add_edge", "detect_simple_cycles", "remove_weak_link"]
