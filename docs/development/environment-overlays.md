# Host-Aware Environment Overlays

This guide explains the new workflow for generating `.env` files that adapt to
the local host (e.g., Ubuntu on bare metal vs. WSL). The generator merges the
project template, a profile-specific overlay, and a secret bundle that lives
*outside* the repository, then injects host metadata such as the WSL bridge IP.

## Platform Reorg Context

TTA has completed the platform split outlined in
`docs/development/reorg/tta-separation-roadmap.md`. Environment artifacts now
map to the following directories:

- `app_tta/config/env/…`: player-facing runtime overlays and samples.
- `platform_tta_dev/components/*/config/env/…`: tooling overlays for Serena, ACE,
  Hypertool, e2b, cline CLI, and other developer agents.
- `legacy/*/config/env/…`: quarantined overlays that will be retired after the
  migration completes.

As of 2025-11-17, all agentic components have been migrated to `platform_tta_dev/components/`
with backward-compatibility symlinks. See `MIGRATION_SUMMARY.md` for complete details.

## Components

| Artifact | Purpose |
| --- | --- |
| `scripts/env/generate_env.py` | CLI that merges layers, detects host details, and writes the final `.env`. |
| `config/env/overlays/<profile>.env` | Checked-in overlays with host-specific tweaks (e.g., `wsl-dev`). |
| `config/env/samples/*.secrets.sample.env` | Placeholder secrets that show the expected structure; copy outside the repo before use. |
| `scripts/env/bootstrap_secrets.py` | Copies a sample secrets file into `~/.config/tta/secrets/<profile>.env`. |

## Overlay Structure

Overlays are standard dotenv files. You can reference host metadata using
`${TTA_HOST_BRIDGE_IP}`, `${TTA_HOST_KIND}`, etc. Example (excerpt from
`config/env/overlays/wsl-dev.env`):

```env
REACT_APP_API_URL=http://${TTA_HOST_BRIDGE_IP}:8080
DATABASE_URL=postgresql://tta_user:${POSTGRES_PASSWORD}@${TTA_HOST_BRIDGE_IP}:5432/tta_db
NEO4J_URI=bolt://${TTA_HOST_BRIDGE_IP}:7687
```

The `${VAR}` placeholders are resolved after all layers are merged, so you can
also reference secrets or values defined earlier in the chain.

## Secrets Handling

1. Pick or create a profile name, e.g., `wsl-dev`.
1. Use the bootstrap helper to copy the sample secrets file outside the repo:

  ```bash
  python3 scripts/env/bootstrap_secrets.py --profile wsl-dev --verbose
  ```

  Overrides: `--sample` (custom sample path), `--dest` (custom target), and
  `--force` (overwrite existing file).

1. Replace every placeholder value in `~/.config/tta/secrets/wsl-dev.env` with the
  real credentials (never commit this file).

> **Note:** The generator never writes secrets back into the repo. If the secrets
> file is missing, it simply skips that layer and continues.

## Generating a `.env`

```bash
cd /path/to/TTA
python3 scripts/env/generate_env.py \
  --profile wsl-dev \
  --secrets ~/.config/tta/secrets/wsl-dev.env \
  --output .env \
  --force
```

Flags of interest:

- `--dry-run` prints the merged key/value pairs without writing a file.
- `--print-host-info` dumps the detected host metadata as JSON.
- `--overlay` allows pointing at any dotenv file if you don’t want profile-based lookup.

## Validation Checklist

After generating `.env`, run the usual smoke checks to ensure the endpoints are
reachable from your host:

```bash
# Validate DB / Redis / Neo4j connectivity (already provided in repo)
uv run python scripts/test_database_connections.py
uv run python scripts/verify_docker_runtime_setup.py
```

If a connection fails, adjust the overlay (for host-specific endpoints) or the
secrets file (for credentials) and regenerate.

## Troubleshooting Host Detection

Use the built-in inspector whenever you need to confirm what the generator sees
on the current machine:

```bash
python3 scripts/env/generate_env.py --print-host-info
```

Typical output includes:

- `TTA_HOST_KIND`: `wsl`, `linux`, `darwin`, etc.
- `TTA_HOST_BRIDGE_IP`: For WSL, this is the Windows bridge interface taken from
  `/etc/resolv.conf`. For other hosts it defaults to `127.0.0.1`.
- `TTA_DOCKER_SOCKET_PRESENT`: Indicates whether `/var/run/docker.sock` exists.

When running outside WSL but still needing a different IP (e.g., remote Docker
hosts), create another overlay (e.g., `config/env/overlays/remote-dev.env`) and
point the generator at it with `--profile remote-dev`.
