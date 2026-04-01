#!/usr/bin/env python3
"""
TTA Interactive Terminal Game
─────────────────────────────
Run a full Therapeutic Text Adventure session in the terminal.

Usage:
    uv run python scripts/play.py
    uv run python scripts/play.py --skip-genesis
    uv run python scripts/play.py --model mistral --provider ollama
"""

from __future__ import annotations

import argparse
import asyncio
import dataclasses
import json
import logging
import os
import socket
import sys
import warnings
from datetime import datetime
from pathlib import Path
from uuid import uuid4

# ── Path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

# Auto-load .env so users don't need to `source .env` before running
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not installed; user must export env vars manually

# Suppress noisy upstream library warnings before any imports trigger them
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")
warnings.filterwarnings("ignore", message=".*Pydantic V1.*")
warnings.filterwarnings("ignore", message=".*pydantic.*")

# ── Logging (stderr only, not console) ───────────────────────────────────────
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stderr,
)
# Silence noisy library loggers
for _noisy in ("httpx", "httpcore", "openai", "src", "langchain", "langchain_core"):
    logging.getLogger(_noisy).setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Silence structlog (uses its own output pipeline, bypasses stdlib logging)
try:
    import structlog as _structlog

    _structlog.configure(
        wrapper_class=_structlog.make_filtering_bound_logger(logging.ERROR),
    )
except Exception:  # noqa: BLE001, S110
    pass

# ── Rich imports ──────────────────────────────────────────────────────────────
from rich.console import Console  # noqa: E402
from rich.markdown import Markdown  # noqa: E402
from rich.panel import Panel  # noqa: E402
from rich.prompt import Prompt  # noqa: E402
from rich.rule import Rule  # noqa: E402
from rich.text import Text  # noqa: E402

console = Console()

# ── Game imports (deferred until after path setup) ────────────────────────────
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage  # noqa: E402

from src.ai_components.llm_factory import get_llm  # noqa: E402
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
from src.components.genesis.agent import GenesisAgent  # noqa: E402
from src.components.genesis.first_scene_synthesis import (  # noqa: E402
    FirstSceneSynthesisService,
)
from src.components.genesis.session_state import Act, GenesisSessionState  # noqa: E402

# ── Constants ─────────────────────────────────────────────────────────────────
GENESIS_PANEL_STYLE = "magenta"
GENESIS_PANEL_TITLE = "✨ The Void"
GAMEPLAY_PANEL_STYLE = "blue"
QUIT_COMMANDS = {"quit", "exit", "q", ":q", "/quit"}
SAVES_DIR = Path.home() / ".tta" / "saves"
MAX_HISTORY_TURNS = 20  # H/A pairs to keep verbatim in context
SUMMARIZE_TRIGGER = 30  # summarize when raw history exceeds this many H/A pairs
AUTOSAVE_EVERY = 10  # auto-save every N turns
HELP_TEXT = """\
**Commands:**
- `help`            — show this message
- `look`            — re-describe the current scene
- `status`          — show turn, location, and inventory
- `journal`         — show the story-so-far summary
- `save`            — save your session to disk
- `quit` / `exit` / `q` — end the session
- *(anything else)* — your action in the world

Press **Ctrl-C** at any time to exit.\
"""


# ── Game State ────────────────────────────────────────────────────────────────


@dataclasses.dataclass
class GameState:
    """Persistent game state for one session."""

    session_id: str
    world_seed_data: dict  # WorldSeed.model_dump(mode="json")
    turn: int = 0
    location: str = "unknown"
    inventory: list[str] = dataclasses.field(default_factory=list)
    known_npcs: list[str] = dataclasses.field(default_factory=list)
    summary: str = ""  # rolling summary of summarized turns
    raw_history: list[dict] = dataclasses.field(
        default_factory=list
    )  # {"role": "human"|"ai", "content": str}


def save_game(state: GameState) -> Path:
    """Save game state to ~/.tta/saves/."""
    SAVES_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{state.session_id[:8]}_{datetime.now():%Y%m%d_%H%M%S}.json"
    path = SAVES_DIR / filename
    with path.open("w", encoding="utf-8") as f:
        json.dump(dataclasses.asdict(state), f, indent=2, ensure_ascii=False)
    return path


def load_game(path: Path) -> GameState:
    """Load game state from a JSON save file."""
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return GameState(**data)


async def _summarize_turns(llm, turns: list[dict]) -> str:
    """Ask the LLM to compress a list of {role, content} turns into a concise paragraph."""
    turns_text = "\n\n".join(
        f"{'PLAYER' if t['role'] == 'human' else 'NARRATOR'}: {t['content']}"
        for t in turns
    )
    msgs = [
        SystemMessage(
            content=(
                "You are a story archivist. Summarize the following story events into "
                "3-5 sentences, preserving all important facts: character names, items found, "
                "locations visited, decisions made, and any unresolved plot threads. "
                "Write in past tense. Be concrete — names and specifics matter."
            )
        ),
        HumanMessage(content=turns_text),
    ]
    try:
        result = await llm.ainvoke(msgs)
        return result.content if hasattr(result, "content") else str(result)
    except Exception:
        # Fallback: just grab narrator lines
        narrator_lines = [t["content"][:150] for t in turns if t["role"] == "ai"]
        return " … ".join(narrator_lines[:3])


# ── System prompt builder ─────────────────────────────────────────────────────


def _build_game_system_prompt(
    world_seed: WorldSeed, summary: str = "", game_state: GameState | None = None
) -> str:
    """Build a rich narrative GM system prompt grounded in the WorldSeed."""

    tone_map = {
        WorldTone.GETTING_BETTER: "hopeful and slowly brightening",
        WorldTone.GETTING_WORSE: "darkening and fraught with tension",
        WorldTone.HOLDING_ON: "static and weary, where small moments matter enormously",
        WorldTone.CYCLICAL: "rhythmic, where rise and fall are inevitable truths",
    }
    position_map = {
        PlayerPosition.INSIDER: "part of the system, knowing its rules and costs",
        PlayerPosition.OUTSIDER: "living at the margins, watching the centre from afar",
        PlayerPosition.ASCENDING: "climbing from outside toward a place in the structure",
        PlayerPosition.DESCENDING: "fallen from privilege, now navigating unfamiliar edges",
        PlayerPosition.OBSERVER: "deliberately apart, a witness rather than a participant",
    }
    power_map = {
        PowerSource.MAGIC: "magic",
        PowerSource.TECHNOLOGY: "technology",
        PowerSource.POLITICS: "political will and human organisation",
        PowerSource.BELIEF: "collective faith and narrative",
        PowerSource.NATURE: "primal natural forces and the land itself",
        PowerSource.LINEAGE: "blood, ancestry, and inherited power",
        PowerSource.COMBINATION: "a tension of multiple power sources",
    }
    scale_map = {
        WorldScale.VILLAGE: "a single community and its immediate surrounds",
        WorldScale.CITY: "one city and its districts",
        WorldScale.REGION: "a city plus its hinterland",
        WorldScale.CONTINENT: "multiple nations and landscapes",
        WorldScale.WORLD: "the full world",
        WorldScale.COSMIC: "multiple worlds and planes of existence",
    }
    magic_map = {
        MagicPresence.NONE: "there is no magic",
        MagicPresence.RUMOURED: "magic is only rumoured — few have seen it",
        MagicPresence.RARE: "magic exists but is extraordinary",
        MagicPresence.COMMON: "magic is part of everyday life",
        MagicPresence.PERVASIVE: "magic underpins everything",
    }
    motivation_map = {
        Motivation.CURIOSITY: "curiosity and the need to understand",
        Motivation.BELONGING: "the search for a place to belong",
        Motivation.JUSTICE: "justice and righting wrongs",
        Motivation.SURVIVAL: "simple survival",
        Motivation.DISCOVERY: "discovery of the unknown",
        Motivation.FREEDOM: "freedom from constraint",
        Motivation.REDEMPTION: "redemption for past failures",
        Motivation.POWER: "the acquisition of power",
        Motivation.LOVE: "love and connection",
        Motivation.DUTY: "duty and obligation",
        Motivation.REVENGE: "revenge",
        Motivation.CREATION: "the drive to create",
    }

    tone_desc = tone_map.get(world_seed.tone, str(world_seed.tone))
    position_desc = position_map.get(
        world_seed.player_position, str(world_seed.player_position)
    )
    power_desc = power_map.get(world_seed.power_source, str(world_seed.power_source))

    # Optional fields
    char_name = world_seed.character_name or "the player"
    char_bg = world_seed.character_background or "an uncertain past"
    char_secret = (
        world_seed.character_secret or "an unresolved question that drives them forward"
    )
    char_trait = world_seed.character_trait or "a quality that sets them apart"
    motivation_desc = (
        motivation_map.get(
            world_seed.character_motivation, str(world_seed.character_motivation)
        )
        if world_seed.character_motivation
        else "an unnamed yearning"
    )

    scale_desc = (
        scale_map.get(world_seed.scale, "an unknown scale")
        if world_seed.scale
        else "a world of unknown scale"
    )
    magic_desc = (
        magic_map.get(world_seed.magic_presence, "unknown magic presence")
        if world_seed.magic_presence
        else "an unknown relationship with the arcane"
    )

    culture = world_seed.culture_base or "an unnamed culture"
    culture_tone = world_seed.culture_tone or ""
    tension = world_seed.cultural_tension or "an unspoken tension beneath the surface"

    geo = world_seed.geography_archetype or "an unnamed landscape"
    detail = world_seed.one_specific_detail

    guide_fragment = ""
    if world_seed.guide_voice:
        guide_fragment = (
            f"\n\nThe Guide's voice: {world_seed.guide_voice.system_prompt_fragment}"
        )
    if world_seed.guide:
        guide_fragment += (
            f" The guide's name is {world_seed.guide.name}, "
            f"a {world_seed.guide.entity_type} who occupies a {world_seed.guide.social_position} position."
        )

    story_so_far = ""
    if summary:
        story_so_far = f"\n\nSTORY SO FAR:\n{summary}"

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
- The world's emotional tone is {tone_desc}.
- Power flows through {power_desc}.
- The world spans {scale_desc}, shaped by {geo}.
- Magically: {magic_desc}.
- The culture is "{culture}". {culture_tone}
- The world's fundamental tension: {tension}.
- One concrete detail that makes this world specific: {detail}.

PLAYER CHARACTER:
- Name: {char_name}
- Background: {char_bg}
- Driven by: {motivation_desc}
- Known for: {char_trait}
- Their unresolved question: {char_secret}
- Their position in the world: {position_desc}.
{guide_fragment}

NARRATION RULES:
- Write in second-person present tense ("You step forward…").
- Match the world's tone at all times — do not break it.
- Keep responses evocative and grounded in the world's specific detail.
- Respond to player actions with meaningful consequences.
- Each response should be 2-4 paragraphs unless brevity is dramatically appropriate.
- Never break the fourth wall. Stay fully in the world.
- This is a therapeutic space — hold the player's choices with care and curiosity.
- End each response with a subtle opening for the next action (a question, a scene, a choice).
{story_so_far}{current_state_section}

CONSISTENCY RULES:
- The player's inventory and location must stay consistent across turns.
- NPCs the player has met should remember previous interactions.
- The world should feel like it continues between turns — consequences persist.
- When the player gains or loses an item, acknowledge it explicitly.
"""


# ── Mock WorldSeed for --skip-genesis ────────────────────────────────────────


def _make_mock_world_seed() -> WorldSeed:
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
        character_secret="you forged your own contract with one of the old powers and have never told anyone the terms",  # noqa: S106
    )


# ── Display helpers ───────────────────────────────────────────────────────────


def _print_narrator(
    text: str, title: str = GENESIS_PANEL_TITLE, style: str = GENESIS_PANEL_STYLE
) -> None:
    console.print()
    console.print(
        Panel(Markdown(text), title=title, border_style=style, padding=(1, 2))
    )


def _print_separator() -> None:
    console.print(Rule(style="dim"))


def _print_help() -> None:
    console.print(
        Panel(Markdown(HELP_TEXT), title="Help", border_style="yellow", padding=(1, 2))
    )


def _print_welcome() -> None:
    banner = Text()
    banner.append("Therapeutic Text Adventure\n", style="bold magenta")
    banner.append("An AI-powered narrative journey\n", style="dim")
    console.print(Panel(banner, border_style="magenta", padding=(1, 4)))
    console.print()


# ── Phase 1: Genesis ──────────────────────────────────────────────────────────


async def run_genesis(
    args: argparse.Namespace,
) -> tuple[WorldSeed, GenesisSessionState]:
    """Run the Genesis sequence and return the completed WorldSeed + state."""

    if args.skip_genesis:
        console.print("[dim]⏩ Skipping genesis sequence (--skip-genesis)[/dim]")
        world_seed = _make_mock_world_seed()
        state = GenesisSessionState(session_id=uuid4().hex)
        return world_seed, state

    state = GenesisSessionState(session_id=uuid4().hex)
    agent = GenesisAgent()

    console.print("[dim]Starting Genesis sequence… (this may take a moment)[/dim]")
    console.print()

    # First call with empty input to get the opening narration
    try:
        response = await agent.respond(state, "")
    except Exception as exc:
        logger.error("Genesis agent failed on opening call: %s", exc)
        console.print(f"[red]Failed to start genesis: {exc}[/red]")
        raise SystemExit(1) from exc

    _print_narrator(response.text)

    while state.act != Act.SESSION_BEGUN:
        _print_separator()
        try:
            player_input = Prompt.ask("[cyan]> [/cyan]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Session ended.[/dim]")
            raise SystemExit(0) from None

        if player_input.strip().lower() in QUIT_COMMANDS:
            console.print("[dim]Farewell.[/dim]")
            raise SystemExit(0)

        if player_input.strip().lower() == "help":
            _print_help()
            continue

        try:
            response = await agent.respond(state, player_input)
        except Exception as exc:
            logger.error("Genesis agent error: %s", exc)
            console.print(f"[red]Error: {exc}[/red]")
            continue

        _print_narrator(response.text)

        if response.is_complete and response.world_seed is not None:
            return response.world_seed, state

    # Fallback: try to assemble from state if loop exited without world_seed
    console.print("[dim]Genesis complete.[/dim]")
    raise SystemExit(1)


# ── Phase 2: First Scene ──────────────────────────────────────────────────────


async def run_first_scene(world_seed: WorldSeed, session_id: str) -> None:
    """Synthesise and display the opening scene."""

    console.print()
    console.print("[dim]✨ Weaving the first scene…[/dim]")

    service = FirstSceneSynthesisService(neo4j_driver=None)
    try:
        first_scene = await service.synthesize(world_seed, session_id=session_id)
    except Exception as exc:
        logger.error("First scene synthesis failed: %s", exc)
        console.print(f"[red]Scene synthesis failed: {exc}[/red]")
        raise SystemExit(1) from exc

    _print_separator()
    _print_narrator(
        first_scene.scene_text,
        title="🌅 First Light",
        style="green",
    )


# ── Phase 3: Gameplay Loop ────────────────────────────────────────────────────


async def run_gameplay(  # noqa: PLR0912, PLR0915
    world_seed: WorldSeed,
    args: argparse.Namespace,
    session_id: str,
    game_state: GameState | None = None,
) -> None:
    """Run the main gameplay loop with state management and context windowing."""

    if game_state is None:
        game_state = GameState(
            session_id=session_id,
            world_seed_data=world_seed.model_dump(mode="json"),
        )

    world_title = f"🌍 {world_seed.character_name or 'The World'}"

    try:
        llm = get_llm(
            provider=args.provider or None,
            model=args.model or None,
            temperature=0.8,
            max_tokens=800,
        )
    except Exception as exc:
        logger.error("Failed to initialise LLM: %s", exc)
        console.print(f"[red]LLM initialisation failed: {exc}[/red]")
        raise SystemExit(1) from exc

    def _build_history() -> list:
        """Rebuild langchain message list from raw_history + summary."""
        sys_msg = SystemMessage(
            content=_build_game_system_prompt(
                world_seed,
                summary=game_state.summary,
                game_state=game_state,
            )
        )
        messages = [sys_msg]
        # Use last MAX_HISTORY_TURNS H/A pairs
        recent = game_state.raw_history[-(MAX_HISTORY_TURNS * 2) :]
        for entry in recent:
            if entry["role"] == "human":
                messages.append(HumanMessage(content=entry["content"]))
            else:
                messages.append(AIMessage(content=entry["content"]))
        return messages

    async def _maybe_summarize() -> None:
        """If raw_history is too long, summarize the oldest turns."""
        if len(game_state.raw_history) > SUMMARIZE_TRIGGER * 2:
            oldest = game_state.raw_history[: -(MAX_HISTORY_TURNS * 2)]
            if oldest:
                console.print("[dim]📖 Archiving older chapters…[/dim]")
                new_chunk_summary = await _summarize_turns(llm, oldest)
                if game_state.summary:
                    game_state.summary += "\n\n" + new_chunk_summary
                else:
                    game_state.summary = new_chunk_summary
                # Trim history to last MAX_HISTORY_TURNS pairs
                game_state.raw_history = game_state.raw_history[
                    -(MAX_HISTORY_TURNS * 2) :
                ]

    def _do_save() -> None:
        path = save_game(game_state)
        console.print(f"[dim]💾 Saved to {path}[/dim]")

    console.print()
    console.print(
        "[dim]The world awaits. Type [bold]help[/bold] for commands. "
        "[bold]save[/bold] to preserve your progress.[/dim]"
    )
    console.print()

    # Brief pause to avoid rate-limiting first gameplay call immediately after first-scene synthesis
    await asyncio.sleep(3)

    # Track the last narrator response for `look` command
    last_narrator_text: str = ""

    while True:
        _print_separator()
        try:
            player_input = Prompt.ask(f"[cyan][T{game_state.turn}]>[/cyan]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Until next time.[/dim]")
            break

        stripped = player_input.strip()
        if not stripped:
            continue

        cmd = stripped.lower()

        # ── Built-in commands ──────────────────────────────────────────────
        if cmd in QUIT_COMMANDS:
            console.print("[dim]The story pauses here. Farewell.[/dim]")
            break

        if cmd == "help":
            _print_help()
            continue

        if cmd == "save":
            _do_save()
            continue

        if cmd in ("status", "stats"):
            loc = game_state.location or "unknown"
            inv = ", ".join(game_state.inventory) if game_state.inventory else "nothing"
            npcs = (
                ", ".join(game_state.known_npcs)
                if game_state.known_npcs
                else "none yet"
            )
            console.print(
                Panel(
                    f"[bold]Turn:[/bold] {game_state.turn}\n"
                    f"[bold]Location:[/bold] {loc}\n"
                    f"[bold]Inventory:[/bold] {inv}\n"
                    f"[bold]Known NPCs:[/bold] {npcs}",
                    title="📊 Status",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )
            continue

        if cmd in ("journal", "story so far", "recap"):
            if game_state.summary:
                _print_narrator(game_state.summary, title="📜 Journal", style="yellow")
            else:
                console.print("[dim]No journal entries yet.[/dim]")
            continue

        if cmd in ("look", "l", "examine surroundings"):
            if last_narrator_text:
                _print_narrator(
                    last_narrator_text, title=world_title, style=GAMEPLAY_PANEL_STYLE
                )
            else:
                console.print("[dim]Nothing to look at yet.[/dim]")
            continue

        # ── Normal player action ───────────────────────────────────────────
        game_state.raw_history.append({"role": "human", "content": stripped})

        history_msgs = _build_history()

        # Invoke LLM with retry/backoff for transient 429 rate-limits
        response_text = ""
        _retry_waits = [10, 30, 65]  # seconds — covers the 1-minute window
        for _attempt, _wait in enumerate([-1, *_retry_waits]):
            if _wait >= 0:
                console.print(
                    f"[dim]⏳ Rate limited — retrying in {_wait}s…[/dim]"
                )
                await asyncio.sleep(_wait)
            try:
                ai_response = await llm.ainvoke(history_msgs)
                response_text = (
                    ai_response.content
                    if hasattr(ai_response, "content")
                    else str(ai_response)
                )
                break
            except Exception as exc:
                exc_str = str(exc)
                is_rate_limit = "429" in exc_str
                if is_rate_limit and _attempt < len(_retry_waits):
                    continue  # retry with next wait
                logger.error("LLM invoke error: %s", exc)
                console.print(f"[red]The narrator pauses… ({exc})[/red]")
                response_text = ""
                break

        if not response_text:
            game_state.raw_history.pop()  # remove failed human message
            continue

        game_state.raw_history.append({"role": "ai", "content": response_text})
        game_state.turn += 1
        last_narrator_text = response_text

        _print_narrator(response_text, title=world_title, style=GAMEPLAY_PANEL_STYLE)

        # Auto-save
        if game_state.turn % AUTOSAVE_EVERY == 0:
            SAVES_DIR.mkdir(parents=True, exist_ok=True)
            autosave_path = SAVES_DIR / f"{game_state.session_id[:8]}_autosave.json"
            with autosave_path.open("w", encoding="utf-8") as _f:
                json.dump(
                    dataclasses.asdict(game_state), _f, indent=2, ensure_ascii=False
                )
            console.print(f"[dim]💾 Auto-saved (turn {game_state.turn})[/dim]")

        # Manage context window
        if len(game_state.raw_history) > SUMMARIZE_TRIGGER * 2:
            await _maybe_summarize()


# ── LLM availability check ────────────────────────────────────────────────────

_LLM_SETUP_HELP = """\
[bold yellow]No LLM provider configured.[/bold yellow]

To play, you need one of:

  [bold]Option 1 — OpenRouter (free tier, cloud):[/bold]
    1. Sign up at [link=https://openrouter.ai]openrouter.ai[/link] (free)
    2. Create a file named [cyan].env[/cyan] in the repo root:
         [dim]OPENROUTER_API_KEY=sk-or-...[/dim]
    3. Run: [cyan]source .env && make play[/cyan]

  [bold]Option 2 — Ollama (fully local, no API key):[/bold]
    1. Install from [link=https://ollama.ai]ollama.ai[/link]
    2. [cyan]ollama pull llama3.2[/cyan]
    3. [cyan]ollama serve[/cyan]  (in another terminal)
    4. [cyan]make play[/cyan]
"""


def _check_llm_available(args: argparse.Namespace) -> None:
    """Verify an LLM provider is reachable; print helpful error and exit if not."""
    provider = args.provider
    has_openrouter_key = bool(os.environ.get("OPENROUTER_API_KEY"))

    # Determine effective provider (mirrors llm_factory logic)
    if provider is None:
        provider = "openrouter" if has_openrouter_key else "ollama"

    if provider == "openrouter" and not has_openrouter_key:
        console.print(Panel(_LLM_SETUP_HELP, border_style="yellow", padding=(1, 2)))
        raise SystemExit(1)

    if provider == "ollama":
        # Quick TCP check — Ollama listens on 11434
        try:
            with socket.create_connection(("localhost", 11434), timeout=1):
                pass  # reachable
        except OSError:
            console.print(Panel(_LLM_SETUP_HELP, border_style="yellow", padding=(1, 2)))
            raise SystemExit(1) from None


# ── Entry point ───────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="TTA — Therapeutic Text Adventure interactive terminal session",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--skip-genesis",
        action="store_true",
        help="Skip the Genesis sequence and use a built-in demo WorldSeed",
    )
    parser.add_argument(
        "--model",
        metavar="MODEL",
        default=None,
        help="LLM model name (e.g. 'llama3.2', 'mistral', 'meta-llama/llama-3.1-8b-instruct:free')",
    )
    parser.add_argument(
        "--provider",
        metavar="PROVIDER",
        default=None,
        choices=["ollama", "openrouter"],
        help="LLM provider: 'ollama' (local) or 'openrouter' (cloud, needs OPENROUTER_API_KEY)",
    )
    parser.add_argument(
        "--load",
        metavar="FILE",
        default=None,
        help="Resume a saved session from a JSON save file (e.g. ~/.tta/saves/abc12345_20260401_1230.json)",
    )
    return parser


async def main(args: argparse.Namespace) -> None:
    _print_welcome()

    loaded_state: GameState | None = None

    # Handle --load: skip genesis and first scene, go straight to gameplay
    if args.load:
        load_path = Path(args.load).expanduser()
        if not load_path.exists():
            # Try relative to SAVES_DIR
            load_path = SAVES_DIR / args.load
        if not load_path.exists():
            console.print(f"[red]Save file not found: {args.load}[/red]")
            raise SystemExit(1)
        try:
            loaded_state = load_game(load_path)
            world_seed = WorldSeed(**loaded_state.world_seed_data)
            console.print(
                f"[dim]📂 Loaded save — resuming at turn {loaded_state.turn}[/dim]"
            )
        except Exception as exc:
            console.print(f"[red]Failed to load save: {exc}[/red]")
            raise SystemExit(1) from exc

        await run_gameplay(
            world_seed,
            args,
            session_id=loaded_state.session_id,
            game_state=loaded_state,
        )
    else:
        # Phase 1: Genesis
        world_seed, genesis_state = await run_genesis(args)
        session_id = genesis_state.session_id

        # Phase 2: First Scene
        await run_first_scene(world_seed, session_id)

        # Phase 3: Gameplay
        await run_gameplay(world_seed, args, session_id=session_id)

    console.print()
    console.print("[dim]Thank you for playing.[/dim]")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    _parser = _build_parser()
    _args = _parser.parse_args()
    _check_llm_available(_args)  # exits with code 1 if no LLM available
    try:
        asyncio.run(main(_args))
    except SystemExit:
        raise
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted. Goodbye.[/dim]")
        sys.exit(0)
