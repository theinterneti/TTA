"""
Causal graph utilities extracted to a dedicated module.
ScaleManager remains the orchestrator that uses these operations.
"""
from __future__ import annotations

from typing import Dict, List, Set


def add_edge(graph: Dict[str, Set[str]], src: str, dst: str) -> None:
    graph.setdefault(src, set()).add(dst)


def detect_simple_cycles(graph: Dict[str, Set[str]]) -> List[str]:
    issues: List[str] = []
    for src, dsts in graph.items():
        for dst in dsts:
            if dst in graph and src in graph[dst]:
                issues.append(f"Cycle between {src} and {dst}")
    return issues


def remove_weak_link(graph: Dict[str, Set[str]]) -> None:
    for src, dsts in list(graph.items()):
        if not dsts:
            continue
        dst = next(iter(dsts))
        dsts.remove(dst)


__all__ = ["add_edge", "detect_simple_cycles", "remove_weak_link"]

