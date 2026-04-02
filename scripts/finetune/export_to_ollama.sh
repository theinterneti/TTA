#!/usr/bin/env bash
# Export fine-tuned Qwen3-0.6B LoRA → GGUF → Ollama
# Usage: ./export_to_ollama.sh [lora_dir] [output_name]
set -e

LORA_DIR="${1:-/home/theinterneti/Repos/TTA/tta-extractor-lora-qwen3-5}"
MODEL_NAME="${2:-tta-extractor-qwen3}"
BASE_MODEL="Qwen/Qwen3-0.6B"
MERGED_DIR="/tmp/tta-extractor-merged"
GGUF_PATH="/home/theinterneti/Repos/TTA/models/tta-extractor-qwen3.gguf"
MODELFILE="/home/theinterneti/Repos/TTA/models/Modelfile.tta-extractor-qwen3"

PYTHON=~/venvs/llama-factory/bin/python
LF_CLI=~/venvs/llama-factory/bin/llamafactory-cli

echo "=== Step 1: Merge LoRA adapter into base model ==="
rm -rf "$MERGED_DIR"  # clean prior attempt if any
$LF_CLI export \
  --model_name_or_path "$BASE_MODEL" \
  --adapter_name_or_path "$LORA_DIR" \
  --template qwen3_nothink \
  --finetuning_type lora \
  --export_dir "$MERGED_DIR" \
  --export_size 2

echo "=== Step 2: Convert merged model to GGUF (Q4_K_M) ==="
# Use llama.cpp's convert script if available, else use transformers
LLAMA_CPP_DIR="$HOME/.unsloth/llama.cpp"
LLAMA_QUANTIZE="$LLAMA_CPP_DIR/tools/quantize"
CONVERT_SCRIPT="$LLAMA_CPP_DIR/convert_hf_to_gguf.py"

if [[ ! -f "$CONVERT_SCRIPT" ]]; then
  echo "ERROR: llama.cpp not found at $LLAMA_CPP_DIR. Cannot convert to GGUF."
  exit 1
fi

mkdir -p "$(dirname "$GGUF_PATH")"
GGUF_F32_PATH="${GGUF_PATH%.gguf}-f16.gguf"

# Convert HF model → GGUF (f16) — use LF venv python which has transformers
"$PYTHON" "$CONVERT_SCRIPT" "$MERGED_DIR" --outfile "$GGUF_F32_PATH" --outtype f16

# Quantize to Q4_K_M (smaller, Ollama-friendly)
if [[ -f "$LLAMA_QUANTIZE" ]]; then
  "$LLAMA_QUANTIZE" "$GGUF_F32_PATH" "$GGUF_PATH" Q4_K_M
  rm -f "$GGUF_F32_PATH"
else
  echo "WARNING: quantize binary not found — using f16 GGUF (larger but correct)"
  mv "$GGUF_F32_PATH" "$GGUF_PATH"
fi

echo "=== Step 3: Write Ollama Modelfile ==="
cat > "$MODELFILE" << MODELFILE_EOF
FROM $GGUF_PATH

TEMPLATE """<|im_start|>system
{{ .System }}<|im_end|>
<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
"""

SYSTEM """You are a game state extractor. Given a narrative paragraph, extract the current game state in the exact format: [STATE]location=...|inventory=...|npcs=...[/STATE]
Use 'unknown' for any field not mentioned. List multiple NPCs as Name1,Name2. List inventory items as item1,item2. Do not add explanations — output only the [STATE]...[/STATE] block."""

PARAMETER temperature 0.0
PARAMETER top_k 1
PARAMETER stop "[/STATE]"
MODELFILE_EOF

echo "=== Step 4: Register with Ollama ==="
ollama create "$MODEL_NAME" -f "$MODELFILE"

echo ""
echo "Done! Test with:"
echo "  ollama run $MODEL_NAME 'You stand in the forest. Elara hands you a sword.'"
