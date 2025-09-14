#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# Add core/database to path for imports
ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "core", ROOT / "database"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from world_state_manager import WorldStateManager


def main():
    parser = argparse.ArgumentParser(description="TTA Living Worlds Admin CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_summary = sub.add_parser("summary", help="Print world summary (dict)")
    p_summary.add_argument("world_id")

    sub.add_parser("metrics", help="Print debug metrics summary")

    p_export = sub.add_parser("export", help="Export world to file (JSON)")
    p_export.add_argument("world_id")
    p_export.add_argument("file")

    p_import = sub.add_parser("import", help="Import world from file (JSON)")
    p_import.add_argument("file")

    # Entity ops
    p_addc = sub.add_parser("add-character", help="Add a character")
    p_addc.add_argument("world_id")
    p_addc.add_argument("character_id")
    p_addc.add_argument("--name", default="")

    p_addl = sub.add_parser("add-location", help="Add a location")
    p_addl.add_argument("world_id")
    p_addl.add_argument("location_id")
    p_addl.add_argument("--name", default="")

    p_addo = sub.add_parser("add-object", help="Add an object")
    p_addo.add_argument("world_id")
    p_addo.add_argument("object_id")
    p_addo.add_argument("--name", default="")

    p_rm = sub.add_parser("remove-entity", help="Remove an entity by id/type")
    p_rm.add_argument("world_id")
    p_rm.add_argument("entity_type", choices=["character", "location", "object"])
    p_rm.add_argument("entity_id")

    # Flags
    p_flags = sub.add_parser("set-flag", help="Set a world flag key=value")
    p_flags.add_argument("world_id")
    p_flags.add_argument("key")
    p_flags.add_argument("value")

    sub.add_parser("pause", help="Pause evolution").add_argument("world_id")
    sub.add_parser("resume", help="Resume evolution").add_argument("world_id")

    args = parser.parse_args()

    wsm = WorldStateManager()

    if args.cmd == "summary":
        print(wsm.get_world_summary_dict(args.world_id))
    elif args.cmd == "metrics":
        print(wsm.get_debug_metrics_summary())
    elif args.cmd == "export":
        ok = wsm.export_world_state_to_file(args.world_id, args.file)
        print("OK" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    elif args.cmd == "import":
        ws = wsm.import_world_state_from_file(args.file)
        print("OK" if ws else "FAIL")
        sys.exit(0 if ws else 1)
    elif args.cmd == "add-character":
        ok = wsm.add_character(args.world_id, args.character_id, {"name": args.name})
        print("OK" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    elif args.cmd == "add-location":
        ok = wsm.add_location(args.world_id, args.location_id, {"name": args.name})
        print("OK" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    elif args.cmd == "add-object":
        ok = wsm.add_object(args.world_id, args.object_id, {"name": args.name})
        print("OK" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    elif args.cmd == "remove-entity":
        if args.entity_type == "character":
            ok = wsm.remove_character(args.world_id, args.entity_id)
        elif args.entity_type == "location":
            ok = wsm.remove_location(args.world_id, args.entity_id)
        else:
            ok = wsm.remove_object(args.world_id, args.entity_id)
        print("OK" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    elif args.cmd == "set-flag":
        ok = wsm.admin.set_world_flags(args.world_id, {args.key: args.value})
        print("OK" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    elif args.cmd == "pause":
        ok = wsm.admin.pause_evolution(args.world_id)
        print("OK" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    elif args.cmd == "resume":
        ok = wsm.admin.resume_evolution(args.world_id)
        print("OK" if ok else "FAIL")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
