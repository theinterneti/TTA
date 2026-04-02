#!/usr/bin/env bash
# run_training.sh — Safe LLaMA-Factory training launcher for GTX 1650 (4GB VRAM)
#
# Handles:
#   1. Force-unloads all Ollama GPU runners (can't share 4GB with training)
#   2. Blocks system sleep/suspend via systemd-inhibit
#   3. Runs training inside the current shell (use inside tmux for persistence)
#   4. Restores Ollama availability on exit
#
# Usage (inside tmux tta-train session):
#   bash scripts/finetune/run_training.sh
#   bash scripts/finetune/run_training.sh --resume  # resume from last checkpoint

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONFIG="$REPO_ROOT/scripts/finetune/configs/qwen3_5_0.8b_qlora.yaml"
LOG="/tmp/train_lf_qwen3.log"
LF_BIN="$HOME/venvs/llama-factory/bin/llamafactory-cli"

echo "=== TTA Fine-tune Launcher ==="
echo "Config: $CONFIG"
echo "Log:    $LOG"

# ── 1. Evict Ollama GPU runners ────────────────────────────────────────────────
echo ""
echo ">>> Evicting Ollama GPU runners..."
OLLAMA_MODELS=(qwen3.5:2b qwen3.5:0.8b qwen3:1.7b gemma3:4b tta_extractor:latest tta-extractor-qwen3:latest qwen3:0.6b)
for model in "${OLLAMA_MODELS[@]}"; do
    curl -sf http://localhost:11434/api/chat \
        -d "{\"model\": \"$model\", \"keep_alive\": 0}" \
        --max-time 5 >/dev/null 2>&1 && echo "  unloaded: $model" || true
done

# Also use ollama stop for any currently-loaded runners
curl -sf http://localhost:11434/api/ps 2>/dev/null | \
    python3 -c "import sys,json; [print(m['name']) for m in json.load(sys.stdin).get('models',[])]" 2>/dev/null | \
    while read -r m; do ollama stop "$m" 2>/dev/null && echo "  stopped: $m" || true; done

echo ">>> Waiting 12s for VRAM to free..."
sleep 12

VRAM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null || echo "?")
echo ">>> VRAM after eviction: ${VRAM_USED} MiB"
if [[ "$VRAM_USED" != "?" ]] && [[ "$VRAM_USED" -gt 800 ]]; then
    echo ">>> WARNING: VRAM still high (${VRAM_USED} MiB). Consider stopping other GPU workloads."
    echo ">>> Waiting 20 more seconds..."
    sleep 20
    VRAM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null || echo "?")
    echo ">>> VRAM now: ${VRAM_USED} MiB"
fi

# ── 2. Handle --resume flag ────────────────────────────────────────────────────
RESUME_ARG=""
if [[ "${1:-}" == "--resume" ]]; then
    CKPT_DIR="$REPO_ROOT/tta-extractor-lora-qwen3-5"
    LATEST_CKPT=$(ls -d "$CKPT_DIR"/checkpoint-* 2>/dev/null | sort -V | tail -1 || true)
    if [[ -n "$LATEST_CKPT" ]]; then
        echo ">>> Resuming from checkpoint: $LATEST_CKPT"
        # Inject resume_from_checkpoint into a temp config
        TEMP_CONFIG=$(mktemp /tmp/lf_config_XXXX.yaml)
        cp "$CONFIG" "$TEMP_CONFIG"
        echo "resume_from_checkpoint: $LATEST_CKPT" >> "$TEMP_CONFIG"
        CONFIG="$TEMP_CONFIG"
    else
        echo ">>> No checkpoint found, starting fresh"
    fi
fi

# ── 3. Launch training under sleep inhibitor ───────────────────────────────────
echo ""
echo ">>> Starting training (sleep/idle blocked)..."
echo ">>> Monitor: tail -f $LOG"
echo ">>> Progress: cat $REPO_ROOT/tta-extractor-lora-qwen3-5/trainer_log.jsonl"
echo ""

exec systemd-inhibit \
    --what=sleep:idle:handle-lid-switch \
    --who="TTA-train" \
    --why="Qwen3-0.6B QLoRA training" \
    --mode=block \
    bash -c "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
        $LF_BIN train $CONFIG \
        2>&1 | tee $LOG"
