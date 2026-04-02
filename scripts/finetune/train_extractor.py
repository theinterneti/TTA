#!/usr/bin/env python3
"""
Fine-tune Qwen2.5-Instruct on TTA [STATE] extraction pairs using Unsloth + LoRA.

Usage (from within tta-finetune venv):
    source ~/venvs/tta-finetune/bin/activate
    python scripts/finetune/train_extractor.py
    python scripts/finetune/train_extractor.py --epochs 5 --data data/training_pairs.jsonl
    python scripts/finetune/train_extractor.py --base-model unsloth/Qwen2.5-0.5B-Instruct

Hardware:
    GTX 1650 (4GB VRAM) — use fp16=True, bf16=False, batch_size=1
    Qwen2.5-1.5B-Instruct + 4-bit: ~1.3GB VRAM, fits comfortably

IMPORTANT: import unsloth FIRST before transformers/trl/peft (monkey-patches them).
"""

import argparse
import json
import sys
from pathlib import Path

# ── Save Accelerator.prepare BEFORE unsloth replaces it ───────────────────────
# unsloth/models/_utils.py exec()s Accelerator.prepare source into its own globals,
# which lacks FP8BackendType → NameError at training time. We save the original
# (proper Python method with correct scope) and restore it after unsloth patches.
import accelerate.accelerator as _acc_mod
_original_accelerator_prepare = _acc_mod.Accelerator.prepare


# ── Unsloth must be imported before any transformers/trl/peft ──────────────
try:
    import unsloth  # noqa: F401 — side-effect import patches trl/transformers
    from unsloth import FastLanguageModel
except ImportError:
    print("ERROR: unsloth not installed. Activate the fine-tune venv first:")
    print("  source ~/venvs/tta-finetune/bin/activate")
    print("  pip install 'unsloth[cu124-torch250] @ git+https://github.com/unslothai/unsloth.git'")
    sys.exit(1)

# Restore the original prepare (unsloth's exec'd version breaks on FP8BackendType)
_acc_mod.Accelerator.prepare = _original_accelerator_prepare

from datasets import load_dataset
from trl import SFTConfig, SFTTrainer


DEFAULT_BASE_MODEL = "unsloth/Qwen2.5-1.5B-Instruct"  # Instruct: has ChatML template; supported by unsloth 2025.3.x + transformers 4.51.x
DEFAULT_DATA = "data/training_pairs.jsonl"
DEFAULT_OUTPUT = "./tta-extractor-lora"
DEFAULT_GGUF_OUTPUT = "./tta-extractor-gguf"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fine-tune Qwen3.5-0.8B for TTA [STATE] extraction")
    p.add_argument("--base-model", default=DEFAULT_BASE_MODEL, help="HuggingFace model ID or path")
    p.add_argument("--data", default=DEFAULT_DATA, help="Path to training_pairs.jsonl (ChatML format)")
    p.add_argument("--output", default=DEFAULT_OUTPUT, help="Where to save LoRA adapters")
    p.add_argument("--gguf-output", default=DEFAULT_GGUF_OUTPUT, help="Where to save GGUF export")
    p.add_argument("--epochs", type=int, default=3, help="Training epochs (default: 3)")
    p.add_argument("--lora-r", type=int, default=16, help="LoRA rank (default: 16)")
    p.add_argument("--max-seq-len", type=int, default=512, help="Max sequence length (default: 512)")
    p.add_argument("--load-in-4bit", action="store_true", help="Load base model in 4-bit (needed for 2B on 4GB VRAM)")
    p.add_argument("--skip-gguf", action="store_true", help="Skip GGUF export step")
    p.add_argument("--dry-run", action="store_true", help="Print config and exit without training")
    return p.parse_args()


def validate_data(data_path: Path) -> int:
    """Validate training data and return sample count."""
    if not data_path.exists():
        print(f"ERROR: Training data not found at {data_path}")
        print("Run first: uv run python scripts/collect_training_pairs.py")
        sys.exit(1)

    count = 0
    npc_rich = 0
    with open(data_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                msgs = row["messages"]
                assert len(msgs) == 3
                assistant_content = msgs[2]["content"]
                if "npcs=" in assistant_content and "none" not in assistant_content.split("npcs=")[1].split("|")[0]:
                    npc_rich += 1
                count += 1
            except (json.JSONDecodeError, KeyError, AssertionError) as e:
                print(f"WARNING: Malformed record at line {count+1}: {e}")

    print(f"✓ Training data: {count} samples ({npc_rich} NPC-rich, {100*npc_rich//count}%)")
    if count < 50:
        print(f"WARNING: Only {count} samples — recommend ≥100 for reliable NPC tracking")
    return count


def main() -> None:
    args = parse_args()
    data_path = Path(args.data)
    output_path = Path(args.output)
    gguf_path = Path(args.gguf_output)

    # Auto-enable 4-bit for larger models on constrained VRAM (GTX 1650 = 4GB)
    # Auto-enable 4-bit for models >= 1B on GTX 1650 (4GB VRAM)
    large_model_keywords = ["1.5B", "1.7B", "2B", "3B", "7B"]
    if not args.load_in_4bit and any(kw in args.base_model for kw in large_model_keywords):
        print("Note: Auto-enabling 4-bit loading for large model on 4GB VRAM.")
        args.load_in_4bit = True

    print("\n" + "="*60)
    print("TTA Extractor Fine-Tune")
    print("="*60)
    print(f"Base model:   {args.base_model}")
    print(f"Data:         {data_path}")
    print(f"Output:       {output_path}")
    print(f"GGUF output:  {gguf_path}")
    print(f"Epochs:       {args.epochs}")
    print(f"LoRA rank:    {args.lora_r}")
    print(f"Max seq len:  {args.max_seq_len}")
    print(f"4-bit base:   {args.load_in_4bit}")
    print()

    sample_count = validate_data(data_path)

    if args.dry_run:
        print("Dry run — exiting.")
        return

    # ── Load base model ────────────────────────────────────────────────────
    print("Loading base model...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.base_model,
        max_seq_length=args.max_seq_len,
        load_in_4bit=args.load_in_4bit,   # True only for 2B on 4GB VRAM
        dtype=None,                        # Auto-detect: FP16 on GTX 1650 (no BF16)
    )

    # ── Add LoRA adapters ──────────────────────────────────────────────────
    print("Adding LoRA adapters...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_r,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        lora_alpha=args.lora_r,       # alpha = rank is standard
        lora_dropout=0,               # 0 enables unsloth's fast kernel patching (~2x speedup)
        bias="none",
        use_gradient_checkpointing="unsloth",  # Saves ~30% VRAM
        random_state=42,
    )

    # ── Load dataset ───────────────────────────────────────────────────────
    print(f"Loading {sample_count} training samples...")
    dataset = load_dataset("json", data_files=str(data_path), split="train")

    # Pre-apply chat template: messages → text string per sample.
    # Using dataset_text_field is more reliable than formatting_func with Unsloth.
    def apply_template(sample: dict) -> dict:
        return {
            "text": tokenizer.apply_chat_template(
                sample["messages"],
                tokenize=False,
                add_generation_prompt=False,
            )
        }

    dataset = dataset.map(apply_template, num_proc=1)

    # ── Trainer ───────────────────────────────────────────────────────────
    # Gradient accumulation simulates larger batch on 4GB VRAM
    # effective_batch = 1 × grad_accum_steps
    grad_accum = 8

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        args=SFTConfig(
            per_device_train_batch_size=1,
            gradient_accumulation_steps=grad_accum,
            num_train_epochs=args.epochs,
            learning_rate=2e-4,
            fp16=False,                   # Unsloth auto-handles precision for Qwen3.5
            bf16=False,
            logging_steps=10,
            save_strategy="epoch",
            output_dir=str(output_path / "checkpoints"),
            optim="paged_adamw_8bit",     # Lower VRAM optimizer states
            warmup_ratio=0.1,
            lr_scheduler_type="cosine",
            max_seq_length=args.max_seq_len,
            packing=False,
            report_to="none",             # No wandb/tensorboard dependency
        ),
    )

    print(f"\nStarting training — {args.epochs} epochs × {sample_count} samples")
    print(f"Effective batch size: {grad_accum} | Watch VRAM: nvidia-smi dmon -s u")
    print()

    trainer.train()

    # ── Save LoRA adapters ─────────────────────────────────────────────────
    output_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(output_path))
    tokenizer.save_pretrained(str(output_path))
    print(f"\n✓ LoRA adapters saved → {output_path}")

    # ── GGUF export ────────────────────────────────────────────────────────
    if not args.skip_gguf:
        print(f"\nExporting GGUF (q4_k_m) → {gguf_path} ...")
        gguf_path.mkdir(parents=True, exist_ok=True)
        model.save_pretrained_gguf(
            str(gguf_path),
            tokenizer,
            quantization_method="q4_k_m",   # Best quality/size for 0.8B
        )
        gguf_file = next(gguf_path.glob("*.gguf"), None)
        if gguf_file:
            size_mb = gguf_file.stat().st_size / 1024 / 1024
            print(f"✓ GGUF exported: {gguf_file.name} ({size_mb:.0f} MB)")
            print()
            print("Next step — register with Ollama:")
            print(f"  ollama create tta-extractor -f models/Modelfile.tta-extractor")
            print(f"  # (Modelfile points to: {gguf_file})")
        else:
            print("WARNING: GGUF file not found after export — check logs above")
    else:
        print("Skipping GGUF export (--skip-gguf)")

    print("\n" + "="*60)
    print("Fine-tune complete!")
    print("="*60)


if __name__ == "__main__":
    main()
