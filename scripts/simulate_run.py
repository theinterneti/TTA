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

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

warnings.filterwarnings("ignore", category=UserWarning, module="langchain")
warnings.filterwarnings("ignore", message=".*[Pp]ydantic.*")

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage  # noqa: E402

from src.components.gameplay_loop.models.world_seed import (  # noqa: E402
    MagicPresence,
    Motivation,
    PlayerPosition,
    PowerSource,
    TechLevel,
    WorldScale,
    WorldSeed,
    WorldTone,
)
from src.components.model_management.mode_runner import ModeRunner  # noqa: E402

# ── Reuse GameState / helpers from play.py ─────────────────────────────────────
# We import the relevant pieces directly rather than exec-importing play.py
# to avoid the interactive startup side-effects.

MAX_HISTORY_TURNS = 20
SUMMARIZE_TRIGGER = 30
AUTOSAVE_EVERY = 10

_STATE_RE_SIM = re.compile(r"\[STATE\](.*?)(?:\[/STATE\]|$)", re.DOTALL)
_THINK_RE_SIM = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)

_OLLAMA_BASE = "http://localhost:11434"
_OLLAMA_TIMEOUT = 120.0

# ── ModeRunner — shared for extraction + narration ────────────────────────────
# Both narration and extraction now route through ModeRunner → ModelRouterPrimitive.
# Cascade order (narration): Groq → OR pinned → OR auto (FreeModelTracker)
# Cascade order (extraction): local Ollama → Groq → OR pinned → OR auto
# Multi-turn history is flattened into a single prompt string for ModeRunner;
# if ALL cloud tiers fail, _call_ollama_sim provides the local Ollama fallback.
_mode_runner = ModeRunner()

# Local-only mode names (bypass ModeRunner, call Ollama directly)
_LOCAL_ONLY_MODES = {"ollama", "blended", "local-fast", "qwen35-local"}


def _available_modes() -> list[str]:
    """Return available simulation mode names."""
    return sorted(
        [*_LOCAL_ONLY_MODES, "cascade", "openrouter", "hybrid", "groq", "tta-extractor-hybrid"]
    )


def _flatten_to_prompt(messages: list) -> str:
    """Flatten a LangChain message list (excluding SystemMessage) into a prose prompt.

    ModeRunner accepts a single prompt string; multi-turn history is represented
    as labelled turns so the model understands conversational context.
    """
    lines: list[str] = []
    for m in messages:
        if isinstance(m, SystemMessage):
            continue
        role = "Player" if isinstance(m, HumanMessage) else "Narrator"
        lines.append(f"{role}: {m.content}")
    return "\n\n".join(lines)


def _msgs_to_dicts(messages: list) -> list[dict]:
    """Convert LangChain message objects to plain role/content dicts for Ollama."""
    result = []
    for m in messages:
        if isinstance(m, SystemMessage):
            result.append({"role": "system", "content": m.content})
        elif isinstance(m, HumanMessage):
            result.append({"role": "user", "content": m.content})
        elif isinstance(m, AIMessage):
            result.append({"role": "assistant", "content": m.content})
    return result


async def _call_ollama_sim(
    messages: list[dict], model: str, think: bool = False
) -> str:
    """Call Ollama /api/chat and return the response content string.

    ``think=False`` (default) disables chain-of-thought for qwen3/qwen3.5
    thinking models, keeping extraction fast and the content field populated.
    """
    async with httpx.AsyncClient(timeout=_OLLAMA_TIMEOUT) as client:
        resp = await client.post(
            f"{_OLLAMA_BASE}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "think": think,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"]


def _strip_state_block(text: str) -> tuple[str, dict]:
    match = _STATE_RE_SIM.search(text)
    if not match:
        return text.strip(), {}
    clean = (text[: match.start()] + text[match.end() :]).strip()
    raw = match.group(1).strip()
    state: dict = {}
    for part in raw.split("|"):
        if "=" not in part:
            continue
        key, _, val = part.partition("=")
        key = key.strip().lower()
        val = val.strip()
        if key == "location" and val.lower() not in ("unknown", "none", ""):
            state["location"] = val
        elif key == "inventory":
            items = []
            for i in val.split(","):
                clean_i = i.strip().strip("[]")
                if clean_i and clean_i.lower() not in ("empty", "none", ""):
                    items.append(clean_i)
            state["inventory"] = items
        elif key == "npcs":
            npcs = []
            for n in val.split(","):
                clean_n = n.strip().strip("[]")
                if clean_n and clean_n.lower() not in ("none", "empty", ""):
                    npcs.append(clean_n)
            state["npcs"] = npcs
    return clean, state


def _normalize_state(state: dict) -> dict:
    """Normalize extracted state: deduplicate, clean underscores, fix case."""
    normalized: dict = {}

    # Location: replace underscores with spaces, strip excess whitespace
    if state.get("location"):
        normalized["location"] = state["location"].replace("_", " ").strip()

    # Inventory: normalize, deduplicate case-insensitively, filter garbage, cap at 5
    if state.get("inventory") is not None:
        seen: set[str] = set()
        clean_items: list[str] = []
        for item in state["inventory"]:
            item = item.replace("_", " ").strip()
            # Filter: skip if >35 chars (phrases), empty, or looks like atmosphere/material
            if not item or len(item) > 35:
                continue
            # Filter common false positives: scene objects / liquids / materials
            _low = item.lower()
            if _low in {
                "blood",
                "mist",
                "fog",
                "light",
                "shadow",
                "dust",
                "air",
                "water",
                "fire",
                "smoke",
                "nothing",
                "empty",
                "none",
                "bottle",
                "crate",
                "crates",
                "signature",
                "ink",
                "ledger",
                "paper",
                "vellum",
                "parchment",
                "scroll",
                "tome",
                "candle",
                "coin",
                "coins",
                "bargain",
                "key",
                "map",
                "note",
                "notes",
                "letter",
            }:
                continue
            if _low not in seen:
                seen.add(_low)
                clean_items.append(item.title())
        normalized["inventory"] = clean_items[:5]  # hard cap

    # NPCs: normalize, deduplicate case-insensitively, filter garbage, cap at 5
    if state.get("npcs") is not None:
        seen_npcs: set[str] = set()
        clean_npcs: list[str] = []
        for npc in state["npcs"]:
            npc = npc.replace("_", " ").strip()
            # Filter: >30 chars, contains digits, generic role words without proper name
            if not npc or len(npc) > 30 or any(c.isdigit() for c in npc):
                continue
            _low_npc = npc.lower()
            if _low_npc in {
                "the man",
                "dockhand",
                "dockworker",
                "clerk",
                "worker",
                "guard",
                "merchant",
                "stranger",
                "figure",
                "person",
                "crew",
                "mysterious crew",
                "unknown figure",
                "passerby",
            }:
                continue
            # Canonical key: strip leading articles so "The Archivist" == "Archivist"
            _canon = (
                _low_npc.removeprefix("the ")
                .removeprefix("a ")
                .removeprefix("an ")
                .strip()
            )
            if _canon not in seen_npcs:
                seen_npcs.add(_canon)
                clean_npcs.append(npc.title())
        normalized["npcs"] = clean_npcs[:5]

    return normalized


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


def _build_game_system_prompt(
    world_seed: WorldSeed, summary: str = "", game_state: GameState | None = None
) -> str:
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
- Magic: {world_seed.magic_presence} — {world_seed.magic_source or ""}
- Culture: "{world_seed.culture_base}". {world_seed.culture_tone or ""}
- Tension: {world_seed.cultural_tension or "unspoken"}
- Detail: {world_seed.one_specific_detail}

PLAYER CHARACTER:
- Name: {char_name}
- Background: {char_bg}
- Driven by: freedom from constraint
- Known for: {char_trait}
- Their unresolved question: {char_secret}

NARRATION RULES:
- Write in second-person present tense.
- Match the world's tone. Each response must be 120–350 words.
- Each response should end with a subtle opening for the next action.
- Never break the fourth wall.
- Therapeutic space — hold the player's choices with care.
- After EVERY response, append a state update block on its own line:
  [STATE]location=<current location>|inventory=<item1,item2 or empty>|npcs=<npc1,npc2 or empty>[/STATE]
  Keep location brief (e.g. "Archive entrance", "restricted section", "pier 7").
  List only items the player currently holds. List only NPCs met this scene or recalled.
  This block will be stripped before display — write it for the game engine, not the player.
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


def _detect_entities(text: str, entity_map: dict | None = None) -> list[str]:
    """Return which tracked entity keys are mentioned in the text."""
    lower = text.lower()
    emap = entity_map if entity_map is not None else TRACKED_ENTITIES
    return [key for key, terms in emap.items() if any(t in lower for t in terms)]


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return len(text) // 4


def _count_words(text: str) -> int:
    return len(text.split())


def _extract_proper_nouns(text: str) -> list[str]:
    """Very rough proper noun detection (capitalized words not at sentence start)."""
    words = re.findall(r"(?<=[.!?…]\s)([A-Z][a-z]+)|(?<=\s)([A-Z][a-z]{2,})", text)
    found = [w for pair in words for w in pair if w]
    # Filter common false positives
    stopwords = {
        "The",
        "A",
        "An",
        "In",
        "You",
        "Your",
        "She",
        "He",
        "They",
        "It",
        "Her",
        "His",
        "Their",
        "As",
        "At",
        "To",
        "Of",
        "And",
        "But",
        "Or",
        "With",
        "From",
        "Is",
        "Are",
        "Was",
        "Were",
        "Be",
        "Have",
        "Has",
    }
    return sorted(set(w for w in found if w not in stopwords))


# ── Simulation core ────────────────────────────────────────────────────────────


async def run_simulation(
    n_turns: int,
    out_path: Path,
    dry_run: bool = False,
    provider: str | None = None,
    model: str | None = None,
    mode: str = "openrouter",
    scenario_path: Path | None = None,
    summarize_trigger_override: int | None = None,
    turn_delay: float = 0.0,
) -> None:
    # Load scenario (file overrides built-in SCRIPTED_INPUTS)
    scenario_inputs = SCRIPTED_INPUTS
    scenario_entities = TRACKED_ENTITIES
    scenario_name = "default"
    scenario_chains: dict[str, str] = {}
    if scenario_path is not None:
        raw = json.loads(scenario_path.read_text())
        scenario_inputs = raw["inputs"]
        scenario_entities = raw.get("tracked_entities", TRACKED_ENTITIES)
        scenario_name = raw.get("name", scenario_path.stem)
        scenario_chains = raw.get("chains", {})

    # Apply summarize trigger override
    summarize_trigger = (
        summarize_trigger_override
        if summarize_trigger_override is not None
        else SUMMARIZE_TRIGGER
    )

    # Narrator routing: local-only modes use Ollama directly; all others cascade
    # through ModeRunner (Groq → OR pinned → OR auto → local fallback).
    local_only = mode in _LOCAL_ONLY_MODES
    local_narrator_model = "gemma3:4b"  # Ollama fallback / local-only model

    world_seed = _make_sable_world_seed()
    session_id = uuid4().hex
    game_state = GameState(
        session_id=session_id, world_seed_data=world_seed.model_dump(mode="json")
    )

    scripted = scenario_inputs[:n_turns]
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

    out_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_records: list[dict] = []
    all_entity_appearances: dict[str, list[int]] = {k: [] for k in scenario_entities}

    print(f"\n{'=' * 60}")
    print(f"TTA Simulation Run — {n_turns} turns")
    print(f"Session: {session_id[:8]}")
    print(f"Scenario: {scenario_name}")
    if scenario_chains:
        for chain_id, desc in scenario_chains.items():
            print(f"  Chain {chain_id}: {desc}")
    print(f"Mode: {'DRY RUN (no LLM calls)' if dry_run else ('LOCAL:' + local_narrator_model) if local_only else 'CASCADE (Groq→OR→auto)'}")
    print(
        f"Summarize trigger: {summarize_trigger} H/A pairs (~turn {summarize_trigger})"
    )
    print(f"Output: {out_path}")
    print(f"{'=' * 60}\n")

    for i, player_input in enumerate(scripted):
        turn_num = i + 1
        print(
            f"[T{turn_num:02d}] > {player_input[:70]}{'...' if len(player_input) > 70 else ''}"
        )

        if dry_run:
            response_text = (
                f"[DRY RUN] Turn {turn_num} — would respond to: {player_input}"
            )
            latency_ms = 0.0
        else:
            # Build context
            sys_msg = SystemMessage(
                content=_build_game_system_prompt(
                    world_seed, summary=game_state.summary, game_state=game_state
                )
            )
            messages: list = [sys_msg]
            recent = game_state.raw_history[-(MAX_HISTORY_TURNS * 2) :]
            for entry in recent:
                if entry["role"] == "human":
                    messages.append(HumanMessage(content=entry["content"]))
                else:
                    messages.append(AIMessage(content=entry["content"]))
            messages.append(HumanMessage(content=player_input))

            context_chars = sum(len(str(m.content)) for m in messages if hasattr(m, "content"))

            t0 = time.time()
            response_text = ""
            for _sim_attempt in range(3):
                try:
                    if local_only:
                        response_text = await _call_ollama_sim(
                            _msgs_to_dicts(messages),
                            local_narrator_model,
                        )
                        response_text = _THINK_RE_SIM.sub("", response_text).strip()
                    else:
                        # Cascade: Groq → OR pinned → OR auto via ModeRunner
                        sys_content = str(messages[0].content) if isinstance(messages[0], SystemMessage) else None
                        response_text = await _mode_runner.call(
                            "narration",
                            prompt=_flatten_to_prompt(messages),
                            system=sys_content,
                        )
                    break
                except Exception as exc:
                    exc_str = str(exc)
                    is_retryable = any(
                        code in exc_str for code in ("429", "404", "502", "503")
                    )
                    if is_retryable and _sim_attempt < 2:
                        print(f"  ⟳ Provider error ({exc_str[:60]}) — retrying in 10s…")
                        await asyncio.sleep(10)
                    elif not local_only and _sim_attempt == 2:
                        # All cascade tiers exhausted — final local Ollama fallback
                        print("  🔀 All cascade tiers failed — falling back to local Ollama…")
                        try:
                            response_text = await _call_ollama_sim(
                                _msgs_to_dicts(messages), local_narrator_model
                            )
                            if response_text:
                                print(f"  ✓ Local fallback succeeded: {local_narrator_model}")
                        except Exception as fb_exc:
                            print(f"  ⚠️  Local fallback failed: {fb_exc}")
                        break
                    else:
                        print(
                            f"  ⚠️  Narrator error after {_sim_attempt + 1} attempts: {exc}"
                        )
                        break
            latency_ms = (time.time() - t0) * 1000

            # Empty response guard: retry once with local Ollama
            if not response_text and not dry_run:
                print(f"  ⟳ Empty response — retrying with {local_narrator_model}…")
                try:
                    response_text = await _call_ollama_sim(
                        _msgs_to_dicts(messages), local_narrator_model
                    )
                    latency_ms = (time.time() - t0) * 1000
                except Exception:
                    pass
            if not response_text:
                continue

            # Short-response guard: retry once if narration is suspiciously short
            if _count_words(response_text) < 25 and not dry_run:
                print(
                    f"  ⟳ Response too short ({_count_words(response_text)}w) — retrying…"
                )
                try:
                    if local_only:
                        retry_text = await _call_ollama_sim(
                            _msgs_to_dicts(messages), local_narrator_model
                        )
                    else:
                        sys_content = str(messages[0].content) if isinstance(messages[0], SystemMessage) else None
                        retry_text = await _mode_runner.call(
                            "narration",
                            prompt=_flatten_to_prompt(messages),
                            system=sys_content,
                        )
                    if _count_words(retry_text) > _count_words(response_text):
                        response_text = retry_text
                        latency_ms = (time.time() - t0) * 1000
                except Exception:
                    pass  # keep original short response

        # Update game state — strip [STATE] block first, then update structured fields
        response_text, extracted_state = _strip_state_block(response_text)
        extracted_state = _normalize_state(extracted_state)

        # Extraction: use ModeRunner to run the dedicated extraction pipeline.
        # Tier order: local Ollama extractor → Groq → OpenRouter → auto.
        use_extraction = not dry_run and bool(response_text)
        if use_extraction:
            prior_inv = (
                ", ".join(game_state.inventory) if game_state.inventory else "empty"
            )
            extraction_prompt = (
                f"Player inventory BEFORE this turn: [{prior_inv}]\n\n"
                "Based on the narrative below, output the player's state AFTER this turn.\n"
                "Rules:\n"
                "  location: 2-4 word place name (snake_case)\n"
                "  inventory: items the player is ACTIVELY CARRYING right now.\n"
                "    - Keep prior inventory items unless explicitly dropped/used/lost\n"
                "    - Add items the player EXPLICITLY picked up or was given this turn\n"
                "    - EXCLUDE: items on tables/desks/shelves not touched; scene objects;\n"
                "      liquids; materials; abstract concepts; atmospheric words\n"
                "    - Max 5 items, title case, comma-separated\n"
                "  npcs: named characters/creatures present in this scene (max 3, title case)\n"
                "    - Only proper names without articles (e.g. 'Maren', not 'The Archivist')\n"
                "    - If only title known, use just the title (e.g. 'Archivist', 'Captain')\n"
                "Use 'empty' if none. Reply with ONLY:\n"
                "[STATE]location=<place>|inventory=<items or empty>|npcs=<names or empty>[/STATE]\n\n"
                f"Narrative:\n{response_text}"
            )
            try:
                raw_extraction = await _mode_runner.call(
                    "extraction", prompt=extraction_prompt
                )
                _, qwen_state = _strip_state_block(raw_extraction)
                qwen_state = _normalize_state(qwen_state)
                # ModeRunner extractor is authoritative — replace state, don't accumulate
                if qwen_state:
                    extracted_state = qwen_state
            except Exception:
                pass
        if extracted_state.get("location"):
            game_state.location = extracted_state["location"]
        if extracted_state.get("inventory") is not None:
            # Dedicated extractor output = authoritative current state → replace inventory
            game_state.inventory = extracted_state["inventory"]
        if extracted_state.get("npcs") is not None:
            # NPCs accumulate (known_npcs = everyone met so far)
            for npc in extracted_state.get("npcs", []):
                if npc.lower() not in [n.lower() for n in game_state.known_npcs]:
                    game_state.known_npcs.append(npc)

        game_state.raw_history.append({"role": "human", "content": player_input})
        game_state.raw_history.append({"role": "ai", "content": response_text})
        game_state.turn = turn_num

        # Compute metrics
        sys_msg_temp = SystemMessage(
            content=_build_game_system_prompt(
                world_seed, summary=game_state.summary, game_state=game_state
            )
        )
        all_msgs = [sys_msg_temp] + game_state.raw_history[-(MAX_HISTORY_TURNS * 2) :]
        context_chars = sum(
            len(str(m.get("content", "")) if isinstance(m, dict) else str(getattr(m, "content", "")))
            for m in all_msgs
        )

        entities_in_response = _detect_entities(response_text, scenario_entities)
        for ent in entities_in_response:
            if ent in all_entity_appearances:
                all_entity_appearances[ent].append(turn_num)

        proper_nouns = _extract_proper_nouns(response_text)
        words = _count_words(response_text)
        chars = len(response_text)
        context_msgs = len(all_msgs)
        tokens_est = _estimate_tokens(response_text)
        # Coherence: does response reference any entity introduced >5 turns ago?
        old_entities = [
            e
            for e, turns in all_entity_appearances.items()
            if turns and turns[0] <= turn_num - 5 and e in entities_in_response
        ]

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
            "inventory_structured": list(game_state.inventory),
            "npcs_structured": list(game_state.known_npcs),
            "location_after": extracted_state.get("location", ""),
            "inventory_after": extracted_state.get("inventory", []),
            "npcs_after": extracted_state.get("npcs", []),
            "history_len": len(game_state.raw_history),
            "summary_len": len(game_state.summary),
        }
        metrics_records.append(record)

        print(
            f"       words={words:3d} | latency={latency_ms / 1000:.1f}s | ctx_msgs={context_msgs:2d} | entities={entities_in_response}"
        )
        print(f"       response: {response_text[:120]}...")
        print()

        # Summarization check (mirrors play.py logic)
        if len(game_state.raw_history) > summarize_trigger * 2 and not dry_run:
            oldest = game_state.raw_history[: -(MAX_HISTORY_TURNS * 2)]
            if oldest:
                print("[dim] 📖 Triggering summarization…")
                turns_text = "\n\n".join(
                    f"{'PLAYER' if t['role'] == 'human' else 'NARRATOR'}: {t['content']}"
                    for t in oldest
                )
                summarize_system = (
                    "You are a story archivist. Summarize the following story events into 3-5 sentences, "
                    "preserving all important facts: character names, items found, locations visited, "
                    "decisions made, and any unresolved plot threads. Write in past tense. Be concrete."
                )
                try:
                    if local_only:
                        new_summary = await _call_ollama_sim(
                            [
                                {"role": "system", "content": summarize_system},
                                {"role": "user", "content": turns_text},
                            ],
                            local_narrator_model,
                        )
                    else:
                        new_summary = await _mode_runner.call(
                            "narration",
                            prompt=turns_text,
                            system=summarize_system,
                        )
                    game_state.summary = (
                        (game_state.summary + "\n\n" + new_summary).strip()
                        if game_state.summary
                        else new_summary
                    )
                    game_state.raw_history = game_state.raw_history[
                        -(MAX_HISTORY_TURNS * 2) :
                    ]
                    print(f"  📖 Summary: {new_summary[:200]}...")
                except Exception as exc:
                    print(f"  ⚠️  Summarization failed: {exc}")

        if turn_delay > 0 and turn_num < n_turns:
            await asyncio.sleep(turn_delay)

    # Write JSONL output
    with out_path.open("w", encoding="utf-8") as f:
        for rec in metrics_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Write summary JSON alongside
    summary_path = out_path.with_suffix(".summary.json")
    entity_summary = {k: v for k, v in all_entity_appearances.items() if v}
    avg_words = (
        sum(r["response_words"] for r in metrics_records) / len(metrics_records)
        if metrics_records
        else 0
    )
    avg_latency = (
        sum(r["latency_ms"] for r in metrics_records) / len(metrics_records)
        if metrics_records
        else 0
    )
    coherence_turns = sum(1 for r in metrics_records if r["coherence_callback"])

    # Cross-chain callback: entities that appear in turns outside their "home" chain range
    # Entity first appearance → chain it belongs to → did it get referenced later?
    entity_longevity = {
        k: {"first": v[0], "last": v[-1], "count": len(v), "span": v[-1] - v[0]}
        for k, v in entity_summary.items()
        if len(v) > 1
    }
    long_lived = [k for k, s in entity_longevity.items() if s["span"] >= 10]
    item_usage_turns = [
        r["turn"]
        for r in metrics_records
        if any(
            w in r["player_input"].lower()
            for w in [
                "use",
                "show",
                "compare",
                "rubbing",
                "pocket",
                "sign",
                "write",
                "read",
            ]
        )
    ]

    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "session_id": session_id[:8],
                "n_turns": n_turns,
                "turns_completed": len(metrics_records),
                "avg_response_words": round(avg_words, 1),
                "avg_latency_ms": round(avg_latency, 1),
                "coherence_callback_turns": coherence_turns,
                "coherence_callback_rate": round(
                    coherence_turns / len(metrics_records), 3
                )
                if metrics_records
                else 0,
                "entity_first_appearance": {k: v[0] for k, v in entity_summary.items()},
                "entity_recurrence": {
                    k: v for k, v in entity_summary.items() if len(v) > 1
                },
                "final_context_messages": metrics_records[-1]["context_messages"]
                if metrics_records
                else 0,
                "final_context_chars": metrics_records[-1]["context_chars"]
                if metrics_records
                else 0,
                "summarization_triggered": game_state.summary != "",
                "summarization_trigger_used": summarize_trigger,
                "final_summary": game_state.summary,
                "scenario_name": scenario_name,
                "scenario_chains": scenario_chains,
                "entity_longevity": entity_longevity,
                "long_lived_entities": long_lived,
                "item_usage_turns": item_usage_turns,
                "structured_state_gap": {
                    "location_tracked": game_state.location != "unknown",
                    "inventory_tracked": len(game_state.inventory) > 0,
                    "npcs_tracked": len(game_state.known_npcs) > 0,
                },
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\n{'=' * 60}")
    print(f"Run complete: {len(metrics_records)} turns")
    print(
        f"Avg response: {avg_words:.0f} words | Avg latency: {avg_latency / 1000:.1f}s"
    )
    print(
        f"Coherence callbacks: {coherence_turns}/{len(metrics_records)} turns ({coherence_turns / len(metrics_records) * 100:.0f}%)"
        if metrics_records
        else "Coherence: 0 turns"
    )
    print(
        f"Entity recurrence: {sum(1 for v in entity_summary.values() if len(v) > 1)} entities mentioned >1 turn"
    )
    if long_lived:
        print(f"Long-lived entities (span ≥10 turns): {long_lived}")
    if item_usage_turns:
        print(f"Item usage turns: {item_usage_turns}")
    if game_state.summary:
        print(f"Summarization: TRIGGERED ✅ ({len(game_state.summary)} chars)")
        print(f"  Summary: {game_state.summary[:200]}…")
    else:
        print(f"Summarization: not triggered (trigger={summarize_trigger})")
    print(
        f"Final state: location={game_state.location}, inventory={game_state.inventory}, npcs={game_state.known_npcs}"
    )
    print(f"\nMetrics → {out_path}")
    print(f"Summary → {summary_path}")
    print(f"{'=' * 60}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="TTA Simulation Harness")
    parser.add_argument(
        "--turns",
        type=int,
        default=10,
        help="Number of turns to simulate (default: 10)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSONL path (default: runs/run_N.jsonl)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Skip LLM calls — just test the harness"
    )
    parser.add_argument(
        "--provider", default=None, help="LLM provider (openrouter/ollama)"
    )
    parser.add_argument("--model", default=None, help="LLM model override")
    parser.add_argument(
        "--mode",
        default="openrouter",
        choices=_available_modes(),
        help=(
            f"LLM mode — loaded from config/model_modes.yaml. "
            f"Available: {', '.join(_available_modes())}. "
            "Add new modes by editing config/model_modes.yaml."
        ),
    )
    parser.add_argument(
        "--scenario",
        type=Path,
        default=None,
        help="Path to a scenario JSON file (inputs + tracked_entities). "
        "Overrides built-in SCRIPTED_INPUTS.",
    )
    parser.add_argument(
        "--summarize-trigger",
        type=int,
        default=None,
        help="Override SUMMARIZE_TRIGGER (H/A pairs before rolling summary fires). "
        "Default: 30. Use 15 to test mid-run summarization.",
    )
    parser.add_argument(
        "--turn-delay",
        type=float,
        default=0.0,
        help="Seconds to sleep between turns (default: 0). "
        "Use 10-20 with --mode groq to respect free-tier TPM limits.",
    )
    args = parser.parse_args()

    if args.out is None:
        args.out = Path("runs") / f"run_{args.turns}_{args.mode}.jsonl"

    asyncio.run(
        run_simulation(
            n_turns=args.turns,
            out_path=args.out,
            dry_run=args.dry_run,
            provider=args.provider,
            model=args.model,
            mode=args.mode,
            scenario_path=args.scenario,
            summarize_trigger_override=args.summarize_trigger,
            turn_delay=args.turn_delay,
        )
    )


if __name__ == "__main__":
    main()
