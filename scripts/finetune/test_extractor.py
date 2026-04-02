"""Quick quality test for the fine-tuned tta-extractor-qwen3 Ollama model.

Runs 10 sample prompts and scores exact-format compliance + field recall.
Usage: uv run python scripts/finetune/test_extractor.py [--model tta-extractor-qwen3]
       uv run python scripts/finetune/test_extractor.py --model qwen3.5:0.8b --with-system-prompt
"""

import argparse
import re

import httpx

SYSTEM_PROMPT = (
    "You are a game state extractor. Given a narrative paragraph, extract the "
    "current game state in the exact format: "
    "[STATE]location=...|inventory=...|npcs=...[/STATE]\n"
    "Use 'unknown' for any field not mentioned. List multiple NPCs as Name1,Name2. "
    "List inventory items as item1,item2. "
    "Do not add explanations — output only the [STATE]...[/STATE] block."
)

TEST_CASES = [
    {
        "narrative": "You step into the dimly lit tavern. The innkeeper, Marta, slides a mug across the bar. Your leather satchel clinks with the gold coins and skeleton key inside.",
        "expected": {
            "location": "tavern",
            "inventory": ["gold coins", "skeleton key"],
            "npcs": ["Marta"],
        },
    },
    {
        "narrative": "The forest path winds through ancient oaks. You draw your sword as a wolf circles nearby. Your pack contains dried meat and a healing potion.",
        "expected": {
            "location": "forest",
            "inventory": ["sword", "dried meat", "healing potion"],
            "npcs": [],
        },
    },
    {
        "narrative": "Captain Vance and her first mate Tobias stand at the helm of the merchant vessel. You carry only a dagger and a letter of marque.",
        "expected": {
            "location": "ship",
            "inventory": ["dagger", "letter of marque"],
            "npcs": ["Captain Vance", "Tobias"],
        },
    },
    {
        "narrative": "The throne room is empty. A crown rests on the cushioned dais. You have the royal seal and a blank proclamation in your coat.",
        "expected": {
            "location": "throne room",
            "inventory": ["royal seal", "blank proclamation"],
            "npcs": [],
        },
    },
    {
        "narrative": "Zara the witch examines the vials you carry: nightshade extract and phoenix ash. She stands in her cluttered workshop.",
        "expected": {
            "location": "workshop",
            "inventory": ["nightshade extract", "phoenix ash"],
            "npcs": ["Zara"],
        },
    },
    {
        "narrative": "The marketplace bustles with merchants. Aldric the merchant and his apprentice Finn haggle nearby. You have three silver coins in your pocket.",
        "expected": {
            "location": "marketplace",
            "inventory": ["silver coins"],
            "npcs": ["Aldric", "Finn"],
        },
    },
    {
        "narrative": "You wake in a stone cell. The guard, Rolf, paces outside the iron bars. Your pockets are empty.",
        "expected": {"location": "cell", "inventory": [], "npcs": ["Rolf"]},
    },
    {
        "narrative": "The dragon's cave smells of sulfur. You grip your enchanted shield and magic staff as the beast watches you from across a pile of gold.",
        "expected": {
            "location": "cave",
            "inventory": ["enchanted shield", "magic staff"],
            "npcs": [],
        },
    },
    {
        "narrative": "Elara meets you at the crossroads at midnight. You have a map and a compass rose tucked in your boot.",
        "expected": {
            "location": "crossroads",
            "inventory": ["map", "compass rose"],
            "npcs": ["Elara"],
        },
    },
    {
        "narrative": "The library is vast. Scholar Pembrook and his student Lena pore over ancient texts. You carry a magnifying glass and an ink quill.",
        "expected": {
            "location": "library",
            "inventory": ["magnifying glass", "ink quill"],
            "npcs": ["Pembrook", "Lena"],
        },
    },
]

STATE_RE = re.compile(r"\[STATE\](.*?)(?:\[/STATE\]|$)", re.DOTALL)


def parse_state(text: str) -> dict:
    m = STATE_RE.search(text)
    if not m:
        return {}
    body = m.group(1).strip()
    if not body or "=" not in body:
        return {}
    fields = {}
    for part in body.split("|"):
        if "=" in part:
            k, v = part.split("=", 1)
            fields[k.strip()] = v.strip()
    return fields


def score_case(raw: str, expected: dict) -> dict:
    parsed = parse_state(raw)
    has_format = bool(parsed)

    loc_match = (
        expected["location"].lower() in parsed.get("location", "").lower()
        if expected["location"]
        else True
    )

    npcs_raw = parsed.get("npcs", "")
    found_npcs = [
        n.strip().lower()
        for n in npcs_raw.split(",")
        if n.strip() and n.strip().lower() != "none"
    ]
    expected_npcs = [n.lower() for n in expected["npcs"]]
    npc_recall = (
        sum(1 for n in expected_npcs if any(n in f for f in found_npcs))
        / max(len(expected_npcs), 1)
        if expected_npcs
        else 1.0
    )

    inv_raw = parsed.get("inventory", "")
    found_inv = [
        i.strip().lower()
        for i in inv_raw.split(",")
        if i.strip() and i.strip().lower() not in ("none", "unknown")
    ]
    expected_inv = [i.lower() for i in expected["inventory"]]
    inv_recall = (
        sum(1 for i in expected_inv if any(i in f for f in found_inv))
        / max(len(expected_inv), 1)
        if expected_inv
        else 1.0
    )

    return {
        "format_ok": has_format,
        "location_ok": loc_match,
        "npc_recall": npc_recall,
        "inv_recall": inv_recall,
    }


def call_ollama(
    model: str, prompt: str, timeout: int = 120, system_prompt: str | None = None
) -> str:
    # Use /api/chat with think=false to suppress extended-thinking tokens
    # (required for qwen3.5 models; harmless for others)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    resp = httpx.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "messages": messages,
            "think": False,
            "stream": False,
            "keep_alive": "10m",
            "options": {"temperature": 0, "num_predict": 200},
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("message", {}).get("content", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="tta-extractor-qwen3")
    ap.add_argument(
        "--timeout", type=int, default=120, help="Per-request timeout in seconds"
    )
    ap.add_argument(
        "--with-system-prompt",
        action="store_true",
        help="Inject the extractor system prompt (for baseline/untuned models)",
    )
    args = ap.parse_args()

    sys_prompt = SYSTEM_PROMPT if args.with_system_prompt else None

    print(f"Testing model: {args.model}")
    if sys_prompt:
        print("(with system prompt)")
    print("=" * 60)

    results = []
    for i, tc in enumerate(TEST_CASES, 1):
        try:
            raw = call_ollama(
                args.model,
                tc["narrative"],
                timeout=args.timeout,
                system_prompt=sys_prompt,
            )
            score = score_case(raw, tc["expected"])
        except Exception as e:
            print(f"  [{i:02d}] ERROR: {e}")
            results.append(
                {
                    "format_ok": False,
                    "location_ok": False,
                    "npc_recall": 0,
                    "inv_recall": 0,
                }
            )
            continue

        fmt = "✓" if score["format_ok"] else "✗"
        loc = "✓" if score["location_ok"] else "✗"
        print(
            f"  [{i:02d}] fmt={fmt} loc={loc} npcs={score['npc_recall']:.0%} inv={score['inv_recall']:.0%}"
        )
        print(f"        → {raw[:120].strip()}")
        results.append(score)

    print("\n" + "=" * 60)
    n = len(results)
    print(
        f"Format OK:       {sum(r['format_ok'] for r in results)}/{n} ({sum(r['format_ok'] for r in results) / n:.0%})"
    )
    print(f"Location recall: {sum(r['location_ok'] for r in results) / n:.0%}")
    print(f"NPC recall:      {sum(r['npc_recall'] for r in results) / n:.0%}")
    print(f"Inventory recall:{sum(r['inv_recall'] for r in results) / n:.0%}")
    overall = sum(r["format_ok"] and r["location_ok"] for r in results) / n
    print(f"\nOverall pass:    {overall:.0%}")


if __name__ == "__main__":
    main()
