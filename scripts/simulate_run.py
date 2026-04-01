#!/usr/bin/env python3
"""
TTA Gameplay Simulation Harness
─────────────────────────────────
Runs scripted player inputs through the same LLM + GameState machinery as play.py,
capturing per-turn metrics for coherence, pacing, and context window analysis.

Usage:
    uv run python scripts/simulate_run.py --turns 10 --out runs/run_10.jsonl
    uv run python scripts/simulate_run.py --turns 30 --out runs/run_30.jsonl
    uv run python scripts/simulate_run.py --turns 30 --out runs/run_30.jsonl --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import dataclasses
import json
import re
import sys
import time
import warnings
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

warnings.filterwarnings("ignore", category=UserWarning, module="langchain")
warnings.filterwarnings("ignore", message=".*[Pp]ydantic.*")

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage  # noqa: E402

from src.ai_components.llm_factory import get_llm  # noqa: E402
from src.components.gameplay_loop.models.world_seed import (  # noqa: E402
    MagicPresence, Motivation, PlayerPosition, PowerSource,
    TechLevel, WorldScale, WorldSeed, WorldTone,
)

# ── Reuse GameState / helpers from play.py ─────────────────────────────────────
# We import the relevant pieces directly rather than exec-importing play.py
# to avoid the interactive startup side-effects.

MAX_HISTORY_TURNS = 20
SUMMARIZE_TRIGGER = 30
AUTOSAVE_EVERY = 10

@dataclasses.dataclass
class GameState:
    session_id: str
    world_seed_data: dict
    turn: int = 0
    location: str = "unknown"
    inventory: list[str] = dataclasses.field(default_factory=list)
    known_npcs: list[str] = dataclasses.field(default_factory=list)
    summary: str = ""
    raw_history: list[dict] = dataclasses.field(default_factory=list)


def _build_game_system_prompt(world_seed: WorldSeed, summary: str = "", game_state: GameState | None = None) -> str:
    """Minimal reproduction of play.py's system prompt builder."""
    tone_map = {
        WorldTone.GETTING_BETTER: "hopeful and slowly brightening",
        WorldTone.GETTING_WORSE: "darkening and fraught with tension",
        WorldTone.HOLDING_ON: "static and weary, where small moments matter enormously",
        WorldTone.CYCLICAL: "rhythmic, where rise and fall are inevitable truths",
    }
    char_name = world_seed.character_name or "the player"
    char_bg = world_seed.character_background or "an uncertain past"
    char_secret = world_seed.character_secret or "an unresolved question"
    char_trait = world_seed.character_trait or "a quality that sets them apart"
    tone_desc = tone_map.get(world_seed.tone, str(world_seed.tone))
    story_so_far = f"\n\nSTORY SO FAR:\n{summary}" if summary else ""
    current_state_section = ""
    if game_state:
        loc = game_state.location
        inv = ", ".join(game_state.inventory) if game_state.inventory else "nothing"
        npcs = ", ".join(game_state.known_npcs) if game_state.known_npcs else "none yet"
        current_state_section = f"""

CURRENT STATE (keep consistent across turns):
- Current location: {loc}
- Inventory: {inv}
- NPCs the player has met: {npcs}
- Turn: {game_state.turn}"""

    return f"""\
You are the narrator and game master of a therapeutic text adventure.

WORLD:
- Tone: {tone_desc}
- Power flows through: {world_seed.power_source}
- Scale: {world_seed.scale}; geography: {world_seed.geography_archetype}
- Magic: {world_seed.magic_presence} — {world_seed.magic_source or ''}
- Culture: "{world_seed.culture_base}". {world_seed.culture_tone or ''}
- Tension: {world_seed.cultural_tension or 'unspoken'}
- Detail: {world_seed.one_specific_detail}

PLAYER CHARACTER:
- Name: {char_name}
- Background: {char_bg}
- Driven by: freedom from constraint
- Known for: {char_trait}
- Their unresolved question: {char_secret}

NARRATION RULES:
- Write in second-person present tense.
- Match the world's tone. Keep responses 2-4 paragraphs.
- Each response should end with a subtle opening for the next action.
- Never break the fourth wall.
- Therapeutic space — hold the player's choices with care.
{story_so_far}{current_state_section}

CONSISTENCY RULES:
- Location, inventory, NPCs must stay consistent across turns.
- When the player gains or loses an item, acknowledge it explicitly.
- NPCs the player has met should remember previous interactions.
"""


def _make_sable_world_seed() -> WorldSeed:
    return WorldSeed(
        tone=WorldTone.GETTING_BETTER,
        power_source=PowerSource.MAGIC,
        player_position=PlayerPosition.OUTSIDER,
        one_specific_detail="a library that rearranges its own shelves at midnight",
        scale=WorldScale.CITY,
        geography_archetype="fog-wrapped coastal city built on ancient ruins",
        era_tech_level=TechLevel.RENAISSANCE,
        magic_presence=MagicPresence.COMMON,
        magic_source="bargains with the old powers written into contract law",
        culture_base="mercantile republic",
        culture_tone="pragmatic but superstitious; deals are sacred, omens are heeded",
        cultural_tension="the old powers are renegotiating their contracts, and no one knows the new terms",
        character_name="Sable",
        character_background="grew up in the outer docks, apprenticed to a forger of documents",
        character_motivation=Motivation.FREEDOM,
        character_trait="a gift for reading what people need to hear",
        character_secret="you forged your own contract with one of the old powers and have never told anyone the terms",
    )


# ── Scripted inputs — designed to stress-test coherence ───────────────────────

SCRIPTED_INPUTS = [
    # turns 1-5: establish location + first NPC
    "I walk toward the large Archive building I can see through the fog.",
    "I examine the brass door handles — are there any contract markings on them?",
    "I push the door open and step inside the Archive.",
    "I speak to the first person I see inside — an elderly archivist.",
    "I ask the archivist about the renegotiating contracts with the old powers.",
    # turns 6-10: first item, deeper NPC interaction
    "I show her my own contract, carefully — keeping the forged signature covered.",
    "I ask her name and what she knows about the old powers.",
    "I pick up the quill on the nearby desk.",
    "I write my name in the visitor's register.",
    "I ask if there are restricted sections of the Archive.",
    # turns 11-15: escalation + second item
    "I attempt to sneak into the restricted section she pointed at.",
    "I read the first document I can find in the restricted section.",
    "I pocket the document quietly.",
    "I ask about the name signed at the bottom of the document.",
    "I return to the archivist and ask her full name — I want to remember it.",
    # turns 16-20: location change, third NPC
    "I leave the Archive and walk toward the outer docks.",
    "I look for any sign of my old mentor among the dock workers.",
    "I ask a dockworker about any unusual ships that arrived in the last week.",
    "I walk to pier 7 and examine the strange vessel anchored there.",
    "I board the ship, moving quietly along the gangplank.",
    # turns 21-25: third item, callback to earlier events
    "I find the captain's quarters below deck.",
    "I read the ship's log left open on the table.",
    "I hear footsteps above deck — someone is coming.",
    "I hide behind the captain's desk and wait.",
    "I look at the contract pinned to the wall of the captain's quarters.",
    # turns 26-30: callbacks, resolution setup
    "I compare the contract on the wall to the document I pocketed from the Archive.",
    "I take a careful rubbing of the contract on the wall using the quill I took.",
    "I slip off the ship before dawn, back to the fog.",
    "I return to my room at the inn and examine everything I found today.",
    "I write in my own journal: what I found, what I suspect, what I'm afraid of.",
]

# ── Entity tracking helpers ────────────────────────────────────────────────────

# Key entities introduced in the scripted run — we track whether they appear in responses
TRACKED_ENTITIES = {
    "archive": ["archive", "building"],
    "brass_handles": ["brass", "handle", "handles"],
    "archivist": ["archivist"],
    "contracts": ["contract", "contracts", "bargain"],
    "quill": ["quill"],
    "document": ["document", "parchment", "paper"],
    "restricted": ["restricted", "forbidden"],
    "mentor": ["mentor"],
    "dockworker": ["dockworker", "docker", "dock worker"],
    "pier_7": ["pier", "vessel", "ship"],
    "captains_quarters": ["captain", "quarters"],
    "ships_log": ["log", "ship's log"],
    "rubbing": ["rubbing"],
    "inn": ["inn", "room", "room at"],
}

def _detect_entities(text: str) -> list[str]:
    """Return which tracked entity keys are mentioned in the text."""
    lower = text.lower()
    return [key for key, terms in TRACKED_ENTITIES.items() if any(t in lower for t in terms)]


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return len(text) // 4


def _count_words(text: str) -> int:
    return len(text.split())


def _extract_proper_nouns(text: str) -> list[str]:
    """Very rough proper noun detection (capitalized words not at sentence start)."""
    words = re.findall(r'(?<=[.!?…]\s)([A-Z][a-z]+)|(?<=\s)([A-Z][a-z]{2,})', text)
    found = [w for pair in words for w in pair if w]
    # Filter common false positives
    stopwords = {"The", "A", "An", "In", "You", "Your", "She", "He", "They", "It",
                 "Her", "His", "Their", "As", "At", "To", "Of", "And", "But", "Or",
                 "With", "From", "Is", "Are", "Was", "Were", "Be", "Have", "Has"}
    return sorted(set(w for w in found if w not in stopwords))


# ── Simulation core ────────────────────────────────────────────────────────────

async def run_simulation(
    n_turns: int,
    out_path: Path,
    dry_run: bool = False,
    provider: str | None = None,
    model: str | None = None,
) -> None:
    world_seed = _make_sable_world_seed()
    session_id = uuid4().hex
    game_state = GameState(session_id=session_id, world_seed_data=world_seed.model_dump(mode="json"))

    scripted = SCRIPTED_INPUTS[:n_turns]
    if len(scripted) < n_turns:
        # Pad with generic exploration inputs
        extras = [
            "I look around carefully.",
            "I think about what I've discovered so far.",
            "I move toward the nearest source of light.",
            "I speak to someone nearby.",
            "I examine my surroundings more closely.",
        ]
        while len(scripted) < n_turns:
            scripted.extend(extras)
        scripted = scripted[:n_turns]

    llm = None
    if not dry_run:
        llm = get_llm(provider=provider, model=model, temperature=0.8, max_tokens=800)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_records: list[dict] = []
    all_entity_appearances: dict[str, list[int]] = {k: [] for k in TRACKED_ENTITIES}

    print(f"\n{'='*60}")
    print(f"TTA Simulation Run — {n_turns} turns")
    print(f"Session: {session_id[:8]}")
    print(f"Mode: {'DRY RUN (no LLM calls)' if dry_run else 'LIVE'}")
    print(f"Output: {out_path}")
    print(f"{'='*60}\n")

    for i, player_input in enumerate(scripted):
        turn_num = i + 1
        print(f"[T{turn_num:02d}] > {player_input[:70]}{'...' if len(player_input)>70 else ''}")

        if dry_run:
            response_text = f"[DRY RUN] Turn {turn_num} — would respond to: {player_input}"
            latency_ms = 0.0
        else:
            # Build context
            sys_msg = SystemMessage(
                content=_build_game_system_prompt(world_seed, summary=game_state.summary, game_state=game_state)
            )
            messages = [sys_msg]
            recent = game_state.raw_history[-(MAX_HISTORY_TURNS * 2):]
            for entry in recent:
                if entry["role"] == "human":
                    messages.append(HumanMessage(content=entry["content"]))
                else:
                    messages.append(AIMessage(content=entry["content"]))
            messages.append(HumanMessage(content=player_input))

            context_chars = sum(len(m.content) for m in messages)

            t0 = time.time()
            try:
                ai_response = await llm.ainvoke(messages)
                response_text = ai_response.content if hasattr(ai_response, "content") else str(ai_response)
            except Exception as exc:
                print(f"  ⚠️  LLM error: {exc}")
                response_text = ""
            latency_ms = (time.time() - t0) * 1000

            if not response_text:
                continue

        # Update game state
        game_state.raw_history.append({"role": "human", "content": player_input})
        game_state.raw_history.append({"role": "ai", "content": response_text})
        game_state.turn = turn_num

        # Compute metrics
        sys_msg_temp = SystemMessage(content=_build_game_system_prompt(world_seed, summary=game_state.summary, game_state=game_state))
        all_msgs = [sys_msg_temp] + game_state.raw_history[-(MAX_HISTORY_TURNS * 2):]
        context_chars = sum(len(m if isinstance(m, str) else (m.content if hasattr(m, 'content') else m.get('content', ''))) for m in all_msgs)

        entities_in_response = _detect_entities(response_text)
        for ent in entities_in_response:
            all_entity_appearances[ent].append(turn_num)

        proper_nouns = _extract_proper_nouns(response_text)
        words = _count_words(response_text)
        chars = len(response_text)
        context_msgs = len(all_msgs)
        tokens_est = _estimate_tokens(response_text)
        context_tokens_est = _estimate_tokens(str(context_chars))

        # Coherence: does response reference any entity introduced >5 turns ago?
        old_entities = [e for e, turns in all_entity_appearances.items()
                        if turns and turns[0] <= turn_num - 5 and e in entities_in_response]

        record = {
            "session_id": session_id[:8],
            "turn": turn_num,
            "player_input": player_input,
            "response_text": response_text,
            "response_words": words,
            "response_chars": chars,
            "response_tokens_est": tokens_est,
            "latency_ms": round(latency_ms, 1),
            "context_messages": context_msgs,
            "context_chars": context_chars,
            "context_tokens_est": _estimate_tokens(str(context_chars)) + tokens_est,
            "entities_detected": entities_in_response,
            "proper_nouns": proper_nouns,
            "old_entities_referenced": old_entities,
            "coherence_callback": len(old_entities) > 0,
            "location_structured": game_state.location,
            "inventory_structured": game_state.inventory,
            "history_len": len(game_state.raw_history),
            "summary_len": len(game_state.summary),
        }
        metrics_records.append(record)

        print(f"       words={words:3d} | latency={latency_ms/1000:.1f}s | ctx_msgs={context_msgs:2d} | entities={entities_in_response}")
        print(f"       response: {response_text[:120]}...")
        print()

        # Summarization check (mirrors play.py logic)
        if len(game_state.raw_history) > SUMMARIZE_TRIGGER * 2 and not dry_run:
            oldest = game_state.raw_history[:-(MAX_HISTORY_TURNS * 2)]
            if oldest:
                print("[dim] 📖 Triggering summarization…")
                from langchain_core.messages import SystemMessage as SM
                summarize_msgs = [
                    SM(content="You are a story archivist. Summarize the following story events into 3-5 sentences, preserving all important facts: character names, items found, locations visited, decisions made, and any unresolved plot threads. Write in past tense. Be concrete."),
                    HumanMessage(content="\n\n".join(
                        f"{'PLAYER' if t['role']=='human' else 'NARRATOR'}: {t['content']}"
                        for t in oldest
                    )),
                ]
                try:
                    summary_result = await llm.ainvoke(summarize_msgs)
                    new_summary = summary_result.content if hasattr(summary_result, "content") else str(summary_result)
                    game_state.summary = (game_state.summary + "\n\n" + new_summary).strip() if game_state.summary else new_summary
                    game_state.raw_history = game_state.raw_history[-(MAX_HISTORY_TURNS * 2):]
                    print(f"  📖 Summary: {new_summary[:200]}...")
                except Exception as exc:
                    print(f"  ⚠️  Summarization failed: {exc}")

    # Write JSONL output
    with out_path.open("w", encoding="utf-8") as f:
        for rec in metrics_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Write summary JSON alongside
    summary_path = out_path.with_suffix(".summary.json")
    entity_summary = {k: v for k, v in all_entity_appearances.items() if v}
    avg_words = sum(r["response_words"] for r in metrics_records) / len(metrics_records) if metrics_records else 0
    avg_latency = sum(r["latency_ms"] for r in metrics_records) / len(metrics_records) if metrics_records else 0
    coherence_turns = sum(1 for r in metrics_records if r["coherence_callback"])

    with summary_path.open("w", encoding="utf-8") as f:
        json.dump({
            "session_id": session_id[:8],
            "n_turns": n_turns,
            "turns_completed": len(metrics_records),
            "avg_response_words": round(avg_words, 1),
            "avg_latency_ms": round(avg_latency, 1),
            "coherence_callback_turns": coherence_turns,
            "coherence_callback_rate": round(coherence_turns / len(metrics_records), 3) if metrics_records else 0,
            "entity_first_appearance": {k: v[0] for k, v in entity_summary.items()},
            "entity_recurrence": {k: v for k, v in entity_summary.items() if len(v) > 1},
            "final_context_messages": metrics_records[-1]["context_messages"] if metrics_records else 0,
            "final_context_chars": metrics_records[-1]["context_chars"] if metrics_records else 0,
            "summarization_triggered": game_state.summary != "",
            "final_summary": game_state.summary,
            "structured_state_gap": {
                "location_tracked": game_state.location != "unknown",
                "inventory_tracked": len(game_state.inventory) > 0,
                "npcs_tracked": len(game_state.known_npcs) > 0,
            },
        }, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Run complete: {len(metrics_records)} turns")
    print(f"Avg response: {avg_words:.0f} words | Avg latency: {avg_latency/1000:.1f}s")
    print(f"Coherence callbacks: {coherence_turns}/{len(metrics_records)} turns ({coherence_turns/len(metrics_records)*100:.0f}%)")
    print(f"Entity recurrence: {sum(1 for v in entity_summary.values() if len(v)>1)} entities mentioned >1 turn")
    print(f"Structured state gaps: location={game_state.location}, inventory={game_state.inventory}, npcs={game_state.known_npcs}")
    print(f"\nMetrics → {out_path}")
    print(f"Summary → {summary_path}")
    print(f"{'='*60}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="TTA Simulation Harness")
    parser.add_argument("--turns", type=int, default=10, help="Number of turns to simulate (default: 10)")
    parser.add_argument("--out", type=Path, default=None, help="Output JSONL path (default: runs/run_N.jsonl)")
    parser.add_argument("--dry-run", action="store_true", help="Skip LLM calls — just test the harness")
    parser.add_argument("--provider", default=None, help="LLM provider (openrouter/ollama)")
    parser.add_argument("--model", default=None, help="LLM model override")
    args = parser.parse_args()

    if args.out is None:
        args.out = Path("runs") / f"run_{args.turns}.jsonl"

    asyncio.run(run_simulation(
        n_turns=args.turns,
        out_path=args.out,
        dry_run=args.dry_run,
        provider=args.provider,
        model=args.model,
    ))


if __name__ == "__main__":
    main()
