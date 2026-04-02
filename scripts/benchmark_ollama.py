#!/usr/bin/env python3
"""Ollama Model Benchmark for TTA Narrative Generation.

Runs each model through 5 standardized prompts measuring:
- Words per response (target: 120-350)
- Tokens/sec throughput
- [STATE] block compliance rate
- Coherence score (entity recurrence across 5-prompt sequence)
- First-token latency

Usage:
    uv run python scripts/benchmark_ollama.py --model gemma3:4b
    uv run python scripts/benchmark_ollama.py --all
    uv run python scripts/benchmark_ollama.py --compare gemma3:4b llama3.2:3b
    uv run python scripts/benchmark_ollama.py --role state  # test extraction only
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import httpx

# ── Config ────────────────────────────────────────────────────────────────────

OLLAMA_BASE = "http://localhost:11434"
RESULTS_DIR = Path("runs/ollama_benchmarks")

# Entities introduced turn-by-turn — T5 references T1 entity to test coherence
BENCHMARK_PROMPTS = [
    "I walk toward the large Archive building through the fog.",  # T1: scene entry
    "I examine the brass door handles closely, looking for markings.",  # T2: object detail
    "I speak to the elderly archivist standing near the shelves.",  # T3: NPC voice
    "I pick up the quill from the desk and pocket it carefully.",  # T4: item + STATE
    "I ask the archivist if the fog ever lifts near the Archive.",  # T5: coherence callback
]

NARRATION_SYSTEM = """\
You are the narrator of a therapeutic text adventure set in a fog-wrapped coastal city.
Write in second-person present tense. Each response must be 120-350 words.
Be evocative and specific — describe what the player sees, hears, smells.
After EVERY response, append on its own line:
[STATE]location=<current location>|inventory=<item1,item2 or empty>|npcs=<npc1,npc2 or empty>[/STATE]
Keep location brief (e.g. "Archive entrance"). List only items held. List NPCs met.
This block is stripped before display — write it for the engine, not the player."""

STATE_EXTRACTION_SYSTEM = """\
You are a structured data extractor for a text adventure game engine.
Given a narrative passage, extract the current game state in this exact format:
[STATE]location=<location>|inventory=<item1,item2 or empty>|npcs=<npc1,npc2 or none>[/STATE]
Rules:
- location: brief phrase, e.g. "Archive entrance", "restricted section"
- inventory: comma-separated items the player now holds, or "empty"
- npcs: comma-separated named NPCs encountered, or "none"
Output ONLY the [STATE] line. No explanation, no other text."""

# ── Regex ─────────────────────────────────────────────────────────────────────

_STATE_RE = re.compile(r"\[STATE\](.*?)\[/STATE\]", re.DOTALL)
_PROPER_NOUN_RE = re.compile(r"\b[A-Z][a-z]{2,}\b")

ARCHIVE_ENTITIES = {
    "archive",
    "brass",
    "handles",
    "archivist",
    "quill",
    "fog",
    "document",
}


def _parse_state(text: str) -> dict[str, str | list[str]]:
    m = _STATE_RE.search(text)
    if not m:
        return {"location": "", "inventory": [], "npcs": []}
    parts = dict(kv.split("=", 1) for kv in m.group(1).split("|") if "=" in kv)
    inv_raw = parts.get("inventory", "")
    npcs_raw = parts.get("npcs", "")
    return {
        "location": parts.get("location", "").strip(),
        "inventory": [
            i.strip() for i in inv_raw.split(",") if i.strip() not in ("", "empty")
        ],
        "npcs": [
            n.strip() for n in npcs_raw.split(",") if n.strip() not in ("", "none")
        ],
    }


def _word_count(text: str) -> int:
    return len(re.sub(_STATE_RE, "", text).split())


def _entities_in(text: str) -> set[str]:
    lower = text.lower()
    return {e for e in ARCHIVE_ENTITIES if e in lower}


# ── Ollama API ─────────────────────────────────────────────────────────────────


def list_models() -> list[str]:
    r = httpx.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
    r.raise_for_status()
    return [m["name"] for m in r.json().get("models", [])]


def generate(
    model: str, system: str, messages: list[dict], timeout: float = 90.0
) -> dict:
    """Call ollama /api/chat and return timing + text."""
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}] + messages,
        "stream": False,
        "options": {"temperature": 0.8, "num_predict": 600},
    }
    t0 = time.perf_counter()
    r = httpx.post(f"{OLLAMA_BASE}/api/chat", json=payload, timeout=timeout)
    elapsed = time.perf_counter() - t0
    r.raise_for_status()
    data = r.json()
    text = data.get("message", {}).get("content", "")
    eval_count = data.get("eval_count", 0)
    eval_duration_ns = data.get("eval_duration", 1)
    tps = eval_count / (eval_duration_ns / 1e9) if eval_duration_ns else 0
    return {"text": text, "latency_s": elapsed, "tokens": eval_count, "tps": tps}


# ── Benchmark ─────────────────────────────────────────────────────────────────


def benchmark_narration(model: str) -> dict:
    """Run 5-prompt narration benchmark."""
    print(f"\n{'=' * 60}")
    print(f"  NARRATION BENCHMARK: {model}")
    print(f"{'=' * 60}")

    history: list[dict] = []
    turn_results = []
    seen_entities: dict[str, int] = {}  # entity -> first turn seen

    for i, prompt in enumerate(BENCHMARK_PROMPTS, 1):
        history.append({"role": "user", "content": prompt})
        print(f"\n[T{i:02d}] > {prompt[:70]}")
        try:
            result = generate(model, NARRATION_SYSTEM, history)
        except Exception as e:
            print(f"       ❌ ERROR: {e}")
            history.append({"role": "assistant", "content": "[ERROR]"})
            turn_results.append({"turn": i, "error": str(e)})
            continue

        text = result["text"]
        state = _parse_state(text)
        clean = _STATE_RE.sub("", text).strip()
        words = _word_count(text)
        entities = _entities_in(clean)
        has_state = bool(_STATE_RE.search(text))

        # Coherence: entity from ≥3 turns ago re-mentioned
        old_refs = [e for e in entities if seen_entities.get(e, i) < i - 2]
        for e in entities:
            seen_entities.setdefault(e, i)

        state_flag = "✅" if has_state else "❌"
        word_flag = "⚠️ " if words < 120 else ("⚠️ " if words > 350 else "✅")
        print(
            f"       {word_flag} {words}w | {result['latency_s']:.1f}s | {result['tps']:.0f}t/s | STATE:{state_flag}"
        )
        if state["location"]:
            print(
                f"       loc={state['location']!r} inv={state['inventory']} npcs={state['npcs']}"
            )
        if old_refs:
            print(f"       🔗 coherence callback: {old_refs}")
        print(f"       {clean[:100]}...")

        history.append({"role": "assistant", "content": clean})
        turn_results.append(
            {
                "turn": i,
                "words": words,
                "latency_s": round(result["latency_s"], 2),
                "tps": round(result["tps"], 1),
                "has_state": has_state,
                "location": state["location"],
                "inventory": state["inventory"],
                "npcs": state["npcs"],
                "coherence_callback": bool(old_refs),
            }
        )

    # Summary
    completed = [t for t in turn_results if "error" not in t]
    avg_words = sum(t["words"] for t in completed) / len(completed) if completed else 0
    avg_lat = (
        sum(t["latency_s"] for t in completed) / len(completed) if completed else 0
    )
    avg_tps = sum(t["tps"] for t in completed) / len(completed) if completed else 0
    state_pct = (
        sum(1 for t in completed if t["has_state"]) / len(completed) * 100
        if completed
        else 0
    )
    coherence_pct = (
        sum(1 for t in completed if t["coherence_callback"]) / len(completed) * 100
        if completed
        else 0
    )
    in_range = sum(1 for t in completed if 120 <= t["words"] <= 350)

    summary = {
        "model": model,
        "mode": "narration",
        "turns_completed": len(completed),
        "avg_words": round(avg_words, 1),
        "avg_latency_s": round(avg_lat, 2),
        "avg_tps": round(avg_tps, 1),
        "state_block_pct": round(state_pct, 1),
        "coherence_pct": round(coherence_pct, 1),
        "in_word_range_pct": round(in_range / len(completed) * 100, 1)
        if completed
        else 0,
        "turns": turn_results,
    }

    print(f"\n{'─' * 60}")
    print(f"  RESULT: {model}")
    print(
        f"  Avg words: {avg_words:.0f}  |  Avg latency: {avg_lat:.1f}s  |  Avg t/s: {avg_tps:.0f}"
    )
    print(
        f"  [STATE] compliance: {state_pct:.0f}%  |  Word range: {in_range}/{len(completed)}  |  Coherence: {coherence_pct:.0f}%"
    )
    print(f"{'─' * 60}")

    return summary


def benchmark_state_extraction(model: str) -> dict:
    """Test model as a dedicated state extractor (blended mode role)."""
    print(f"\n{'=' * 60}")
    print(f"  STATE EXTRACTION BENCHMARK: {model}")
    print(f"{'=' * 60}")

    # 5 narrative passages with known ground truth
    test_cases = [
        {
            "narrative": "The fog parts as you reach the Archive entrance. The brass handles are cold beneath your fingers. A custodian watches from within.",
            "expected": {
                "location": "Archive entrance",
                "inventory": [],
                "npcs": ["custodian"],
            },
        },
        {
            "narrative": "You step inside. The Archive interior smells of old ink and sea salt. The archivist Mira looks up from her ledger.",
            "expected": {
                "location": "Archive interior",
                "inventory": [],
                "npcs": ["archivist Mira"],
            },
        },
        {
            "narrative": "You pick up the driftwood quill from the desk. It's heavier than it looks. Mira raises an eyebrow.",
            "expected": {
                "location": "Archive interior",
                "inventory": ["quill"],
                "npcs": ["archivist Mira"],
            },
        },
        {
            "narrative": "The restricted section door is locked. You finger the forged document in your coat pocket. Mira has not followed you.",
            "expected": {
                "location": "restricted section entrance",
                "inventory": ["quill", "forged document"],
                "npcs": [],
            },
        },
        {
            "narrative": "You slip through a side exit onto Pier 7. The dockworker Renu gives you a nod. The quill and document are still on you.",
            "expected": {
                "location": "Pier 7",
                "inventory": ["quill", "forged document"],
                "npcs": ["dockworker Renu"],
            },
        },
    ]

    results = []
    for i, case in enumerate(test_cases, 1):
        messages = [{"role": "user", "content": f"Narrative:\n{case['narrative']}"}]
        print(f"\n[E{i:02d}] Extracting state from narrative snippet...")
        try:
            result = generate(model, STATE_EXTRACTION_SYSTEM, messages, timeout=30)
        except Exception as e:
            print(f"       ❌ ERROR: {e}")
            results.append({"case": i, "error": str(e)})
            continue

        text = result["text"].strip()
        parsed = _parse_state(text)
        exp = case["expected"]

        loc_ok = bool(parsed["location"])
        inv_ok = (
            any(
                item.lower() in " ".join(parsed["inventory"]).lower()
                for item in exp["inventory"]
            )
            if exp["inventory"]
            else parsed["inventory"] == []
        )
        npcs_ok = (
            any(
                npc.split()[0].lower() in " ".join(parsed["npcs"]).lower()
                for npc in exp["npcs"]
            )
            if exp["npcs"]
            else True
        )

        score = sum([loc_ok, inv_ok, npcs_ok])
        print(f"       Output: {text[:80]}")
        print(
            f"       Score: {score}/3 | loc:{'✅' if loc_ok else '❌'} inv:{'✅' if inv_ok else '❌'} npcs:{'✅' if npcs_ok else '❌'} | {result['latency_s']:.1f}s"
        )
        results.append(
            {
                "case": i,
                "score": score,
                "latency_s": round(result["latency_s"], 2),
                "output": text,
            }
        )

    completed = [r for r in results if "error" not in r]
    avg_score = (
        sum(r["score"] for r in completed) / (3 * len(completed)) * 100
        if completed
        else 0
    )
    avg_lat = (
        sum(r["latency_s"] for r in completed) / len(completed) if completed else 0
    )

    summary = {
        "model": model,
        "mode": "state-extraction",
        "cases_completed": len(completed),
        "accuracy_pct": round(avg_score, 1),
        "avg_latency_s": round(avg_lat, 2),
        "cases": results,
    }

    print(f"\n{'─' * 60}")
    print(f"  Extraction accuracy: {avg_score:.0f}% | Avg latency: {avg_lat:.1f}s")
    print(f"{'─' * 60}")
    return summary


# ── Compare ────────────────────────────────────────────────────────────────────


def print_comparison(summaries: list[dict]) -> None:
    narr = [s for s in summaries if s["mode"] == "narration"]
    extr = [s for s in summaries if s["mode"] == "state-extraction"]

    if narr:
        print(f"\n{'═' * 80}")
        print("  NARRATION COMPARISON")
        print(f"{'═' * 80}")
        hdr = f"{'Model':<22} {'Avg W':>6} {'Lat':>6} {'t/s':>5} {'STATE%':>7} {'Range%':>7} {'Coh%':>6}"
        print(hdr)
        print("─" * 80)
        for s in sorted(narr, key=lambda x: -x["state_block_pct"]):
            print(
                f"{s['model']:<22} {s['avg_words']:>6.0f} {s['avg_latency_s']:>6.1f} {s['avg_tps']:>5.0f} {s['state_block_pct']:>7.0f} {s['in_word_range_pct']:>7.0f} {s['coherence_pct']:>6.0f}"
            )

    if extr:
        print(f"\n{'═' * 80}")
        print("  STATE EXTRACTION COMPARISON")
        print(f"{'═' * 80}")
        hdr = f"{'Model':<22} {'Accuracy%':>10} {'Avg Lat':>8}"
        print(hdr)
        print("─" * 80)
        for s in sorted(extr, key=lambda x: -x["accuracy_pct"]):
            print(
                f"{s['model']:<22} {s['accuracy_pct']:>10.0f} {s['avg_latency_s']:>8.1f}"
            )


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Ollama models for TTA")
    parser.add_argument("--model", help="Single model to benchmark")
    parser.add_argument(
        "--all", action="store_true", help="Benchmark all pulled models"
    )
    parser.add_argument(
        "--compare", nargs="+", metavar="MODEL", help="Compare specific models"
    )
    parser.add_argument(
        "--role",
        choices=["narration", "state", "both"],
        default="both",
        help="Which benchmark to run (default: both)",
    )
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    available = list_models()
    print(f"Available models: {available or '(none pulled yet)'}")

    models_to_test: list[str] = []
    if args.all:
        models_to_test = available
    elif args.compare:
        models_to_test = args.compare
    elif args.model:
        models_to_test = [args.model]
    else:
        parser.print_help()
        return

    missing = [m for m in models_to_test if m not in available]
    if missing:
        print(f"\n⚠️  Not pulled: {missing}")
        print(f"   Run: ollama pull {missing[0]}")
        models_to_test = [m for m in models_to_test if m in available]
        if not models_to_test:
            return

    all_summaries: list[dict] = []
    for model in models_to_test:
        if args.role in ("narration", "both"):
            s = benchmark_narration(model)
            all_summaries.append(s)
            out = RESULTS_DIR / f"{model.replace(':', '_')}_narration.json"
            out.write_text(json.dumps(s, indent=2))
            print(f"\nSaved → {out}")

        if args.role in ("state", "both"):
            s = benchmark_state_extraction(model)
            all_summaries.append(s)
            out = RESULTS_DIR / f"{model.replace(':', '_')}_state.json"
            out.write_text(json.dumps(s, indent=2))
            print(f"Saved → {out}")

    if len(models_to_test) > 1:
        print_comparison(all_summaries)


if __name__ == "__main__":
    main()
