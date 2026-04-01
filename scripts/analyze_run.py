#!/usr/bin/env python3
"""
TTA Run Analyzer
─────────────────
Reads simulate_run.py JSONL output and generates a readable analysis report.

Usage:
    uv run python scripts/analyze_run.py runs/run_10.jsonl
    uv run python scripts/analyze_run.py runs/run_30.jsonl --verbose
    uv run python scripts/analyze_run.py runs/run_10.jsonl runs/run_20.jsonl runs/run_30.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_run(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_summary(path: Path) -> dict:
    summary_path = path.with_suffix(".summary.json")
    if summary_path.exists():
        return json.loads(summary_path.read_text())
    return {}


def analyze_run(records: list[dict], summary: dict, label: str, verbose: bool = False) -> None:
    if not records:
        print(f"[{label}] No records found.")
        return

    n = len(records)
    print(f"\n{'═'*64}")
    print(f"  {label}  —  {n} turns")
    print(f"{'═'*64}")

    # ── Response quality ──────────────────────────────────────────────────────
    words = [r["response_words"] for r in records]
    latencies = [r["latency_ms"] for r in records]
    print(f"\n📏 RESPONSE LENGTH (words)")
    print(f"   Mean: {sum(words)/n:.0f}  Min: {min(words)}  Max: {max(words)}")

    # Distribution by quintile
    sorted_words = sorted(words)
    q20 = sorted_words[n//5]
    q80 = sorted_words[4*n//5]
    short = sum(1 for w in words if w < 80)
    long_ = sum(1 for w in words if w > 250)
    print(f"   20th pct: {q20} words  |  80th pct: {q80} words")
    print(f"   Short (<80w): {short}/{n}  |  Long (>250w): {long_}/{n}")

    # Per-turn word count sparkline
    print(f"\n   Turn-by-turn word count:")
    bar_max = max(words) if words else 1
    for i, (turn_rec, w) in enumerate(zip(records, words)):
        bar_len = int(w / bar_max * 30)
        bar = "█" * bar_len
        flag = " ⚠️ short" if w < 80 else (" ⚡ long" if w > 250 else "")
        print(f"   T{turn_rec['turn']:02d} [{bar:<30}] {w:3d}{flag}")

    # ── Latency ───────────────────────────────────────────────────────────────
    if any(l > 0 for l in latencies):
        print(f"\n⏱️  LATENCY")
        print(f"   Mean: {sum(latencies)/n/1000:.1f}s  Min: {min(latencies)/1000:.1f}s  Max: {max(latencies)/1000:.1f}s")
        slow = sum(1 for l in latencies if l > 15000)
        if slow:
            print(f"   ⚠️  {slow} turns took >15s (possible rate limiting)")

    # ── Context window growth ─────────────────────────────────────────────────
    ctx_chars = [r["context_chars"] for r in records]
    ctx_msgs = [r["context_messages"] for r in records]
    print(f"\n📦 CONTEXT WINDOW")
    print(f"   Messages:  T01={ctx_msgs[0]}  →  T{n:02d}={ctx_msgs[-1]}  (max observed: {max(ctx_msgs)})")
    print(f"   Chars:     T01={ctx_chars[0]:,}  →  T{n:02d}={ctx_chars[-1]:,}")
    print(f"   Est tokens: T01≈{ctx_chars[0]//4:,}  →  T{n:02d}≈{ctx_chars[-1]//4:,}  (200K limit: {ctx_chars[-1]//4/200000*100:.1f}%)")
    if summary.get("summarization_triggered"):
        print(f"   ✅ Summarization triggered this run")
        if summary.get("final_summary"):
            print(f"   Summary snippet: {summary['final_summary'][:200]}...")
    else:
        trigger_turn = 30  # SUMMARIZE_TRIGGER
        print(f"   ℹ️  Summarization would trigger at turn ~{trigger_turn} (not reached in {n}-turn run)")

    # ── Entity coherence ──────────────────────────────────────────────────────
    print(f"\n🧩 ENTITY COHERENCE")
    entity_first = summary.get("entity_first_appearance", {})
    entity_recur = summary.get("entity_recurrence", {})

    if entity_first:
        print(f"   Entities first mentioned:")
        for entity, first_turn in sorted(entity_first.items(), key=lambda x: x[1]):
            recur = entity_recur.get(entity, [])
            recur_str = f" → recurs at turns {recur[1:]}" if len(recur) > 1 else " (mentioned once)"
            print(f"     T{first_turn:02d}: {entity}{recur_str}")
    else:
        print(f"   No tracked entities detected.")

    coherence_rate = summary.get("coherence_callback_rate", 0)
    coherence_turns = summary.get("coherence_callback_turns", 0)
    print(f"\n   Callback coherence (response references entity >5 turns old):")
    print(f"   {coherence_turns}/{n} turns = {coherence_rate*100:.0f}%")
    if coherence_rate < 0.3:
        print(f"   ⚠️  LOW — narration rarely references earlier events")
    elif coherence_rate < 0.6:
        print(f"   ⚡ MODERATE — some continuity present")
    else:
        print(f"   ✅ GOOD — narration regularly references earlier events")

    # ── Structured state gap ──────────────────────────────────────────────────
    state_gap = summary.get("structured_state_gap", {})
    print(f"\n🗂️  STRUCTURED STATE TRACKING")
    for field, tracked in state_gap.items():
        icon = "✅" if tracked else "❌"
        print(f"   {icon} {field}: {'tracked' if tracked else 'NEVER UPDATED (critical gap)'}")
    print(f"   ℹ️  All 3 fields rely only on LLM conversation history — not extracted structured data.")

    # ── Pacing ────────────────────────────────────────────────────────────────
    print(f"\n🎭 PACING")
    proper_nouns_per_turn = [len(r.get("proper_nouns", [])) for r in records]
    avg_nouns = sum(proper_nouns_per_turn) / n
    # New NPCs/locations introduced (rough: proper nouns first seen this turn)
    seen = set()
    new_per_turn = []
    for r in records:
        nouns = set(r.get("proper_nouns", []))
        new = nouns - seen
        new_per_turn.append(len(new))
        seen |= nouns
    print(f"   Avg proper nouns/turn: {avg_nouns:.1f}")
    new_entity_summary = [f"T{r['turn']:02d}:{cnt}" for r, cnt in zip(records, new_per_turn) if cnt > 0]
    print(f"   New named entities/turn: {new_entity_summary}")

    # Detect turns where the response is very short (pacing issues)
    thin_turns = [r for r in records if r["response_words"] < 80]
    if thin_turns:
        print(f"   ⚠️  {len(thin_turns)} turns with very short responses (possible pacing break):")
        for t in thin_turns:
            print(f"     T{t['turn']:02d}: {t['response_words']} words — \"{t['response_text'][:80]}...\"")

    # ── Verbose: full response text ────────────────────────────────────────────
    if verbose:
        print(f"\n📖 FULL TURN LOG")
        for r in records:
            print(f"\n  ─── T{r['turn']:02d} ───")
            print(f"  > {r['player_input']}")
            print(f"  {r['response_text']}")

    # ── Key findings summary ───────────────────────────────────────────────────
    print(f"\n🔍 KEY FINDINGS")
    findings = []
    if coherence_rate < 0.3:
        findings.append("LOW coherence callback rate — earlier events are quickly 'forgotten' narratively")
    if not state_gap.get("location_tracked"):
        findings.append("Location tracking is broken — system prompt always says 'unknown'")
    if not state_gap.get("inventory_tracked"):
        findings.append("Inventory tracking is broken — system prompt always says 'nothing'")
    if max(words) > 300:
        findings.append(f"Response length variance is high ({min(words)}–{max(words)} words) — pacing is inconsistent")
    if len(entity_recur) < 2 and n >= 10:
        findings.append("Very few entities recur across turns — world doesn't feel continuous")
    if not findings:
        findings.append("No critical issues detected in this run length.")
    for f in findings:
        print(f"   ⚑  {f}")


def compare_runs(runs: list[tuple[str, list[dict], dict]]) -> None:
    """Print a comparison table across multiple runs."""
    if len(runs) < 2:
        return
    print(f"\n\n{'═'*64}")
    print(f"  CROSS-RUN COMPARISON")
    print(f"{'═'*64}")
    headers = ["Run", "Turns", "Avg words", "Avg lat(s)", "Coherence%", "Entity recur", "Summarized"]
    print(f"  {'  '.join(f'{h:<12}' for h in headers)}")
    print(f"  {'-'*90}")
    for label, records, summary in runs:
        n = len(records)
        if not n:
            continue
        avg_w = sum(r["response_words"] for r in records) / n
        avg_l = sum(r["latency_ms"] for r in records) / n / 1000
        coh = summary.get("coherence_callback_rate", 0) * 100
        recur = len(summary.get("entity_recurrence", {}))
        summ = "yes" if summary.get("summarization_triggered") else "no"
        row = [label[:12], str(n), f"{avg_w:.0f}", f"{avg_l:.1f}", f"{coh:.0f}%", str(recur), summ]
        print(f"  {'  '.join(f'{v:<12}' for v in row)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="TTA Run Analyzer")
    parser.add_argument("files", nargs="+", type=Path, help="JSONL run files to analyze")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print full response text per turn")
    args = parser.parse_args()

    all_runs = []
    for path in args.files:
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            continue
        records = load_run(path)
        summary = load_summary(path)
        label = path.stem
        analyze_run(records, summary, label, verbose=args.verbose)
        all_runs.append((label, records, summary))

    if len(all_runs) > 1:
        compare_runs(all_runs)


if __name__ == "__main__":
    main()
