"""
Incremental Training Manager

Permet d'entraîner par subsets avec différentes stratégies:
- Cumulatif: Dataset grossit à chaque run
- Continue: Entraîne sur l'adapter précédent
- Separate: Adapters séparés par domaine

Usage:
    # Stratégie cumulatif
    python scripts/incremental_trainer.py cumulative \
        --base-dataset data/fabien_base.jsonl \
        --new-subset data/fabien_golf.jsonl \
        --domain fabien --epochs 20

    # Stratégie continue training
    python scripts/incremental_trainer.py continue \
        --previous-adapter adapters/fabien_v6.1 \
        --new-subset data/fabien_golf.jsonl \
        --domain fabien --epochs 10
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import argparse
from typing import List, Dict
from datetime import datetime


def load_jsonl(file_path: str) -> List[Dict]:
    """Load JSONL dataset"""
    examples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def save_jsonl(examples: List[Dict], file_path: str):
    """Save JSONL dataset"""
    with open(file_path, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')


def merge_datasets(base_file: str, new_file: str, output_file: str) -> int:
    """Merge two datasets (cumulative strategy)"""
    print(f"📂 Loading base dataset: {base_file}")
    base_examples = load_jsonl(base_file)
    print(f"   ✓ Loaded {len(base_examples)} examples")

    print(f"📂 Loading new subset: {new_file}")
    new_examples = load_jsonl(new_file)
    print(f"   ✓ Loaded {len(new_examples)} examples")

    # Merge
    merged = base_examples + new_examples
    print(f"📊 Merged dataset: {len(merged)} examples")

    # Save
    print(f"💾 Saving merged dataset: {output_file}")
    save_jsonl(merged, output_file)
    print(f"   ✓ Saved {len(merged)} examples")

    return len(merged)


def estimate_training_time(num_examples: int, num_epochs: int) -> float:
    """Estimate training time in minutes (RTX 4070 12GB)"""
    setup_time = 5.0  # Load model, quantize, setup LoRA
    time_per_100_steps = 0.75
    total_steps = num_examples * num_epochs
    training_time = (total_steps / 100) * time_per_100_steps
    save_time = 1.0
    return setup_time + training_time + save_time


def cumulative_strategy(args):
    """
    Stratégie Cumulative: Dataset grossit à chaque run

    Avantage: Pas d'oubli catastrophique
    Inconvénient: Temps augmente avec chaque subset
    """
    print("=" * 70)
    print("🔄 STRATÉGIE CUMULATIVE - Entraînement Incrémental")
    print("=" * 70)

    # Determine version number
    base_path = Path(args.base_dataset)
    version = args.version if args.version else datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create merged dataset
    output_file = base_path.parent / f"{base_path.stem}_cumulative_{version}.jsonl"
    num_examples = merge_datasets(args.base_dataset, args.new_subset, str(output_file))

    # Estimate time
    estimated_time = estimate_training_time(num_examples, args.epochs)

    print("\n" + "=" * 70)
    print("📈 TRAINING PLAN")
    print("=" * 70)
    print(f"\n  Dataset: {output_file.name}")
    print(f"  Examples: {num_examples}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Total steps: {num_examples * args.epochs}")
    print(f"  Estimated time: {estimated_time:.1f} minutes (~{estimated_time/60:.1f}h)")

    print("\n💡 Recommended command:")
    print(f"\n  python scripts/quick_domain_trainer.py {args.domain} \\")
    print(f"      --data-file {output_file} \\")
    print(f"      --epochs {args.epochs} \\")
    print(f"      --description 'Cumulative training v{version}'")

    if not args.auto_train:
        print("\n⚠️  Add --auto-train flag to run training automatically")
    else:
        print("\n🚀 Starting training...")
        import subprocess
        cmd = [
            "python", "scripts/quick_domain_trainer.py", args.domain,
            "--data-file", str(output_file),
            "--epochs", str(args.epochs),
            "--description", f"Cumulative training v{version}"
        ]
        subprocess.run(cmd)


def continue_strategy(args):
    """
    Stratégie Continue Training: Entraîne sur adapter précédent

    Avantage: Vraiment incrémental, dataset petit
    Inconvénient: Risque de drift, complexité
    """
    print("=" * 70)
    print("➡️  STRATÉGIE CONTINUE TRAINING - Sur Adapter Précédent")
    print("=" * 70)

    # Load new subset
    new_examples = load_jsonl(args.new_subset)
    num_examples = len(new_examples)

    # Estimate time
    estimated_time = estimate_training_time(num_examples, args.epochs)

    print("\n" + "=" * 70)
    print("📈 TRAINING PLAN")
    print("=" * 70)
    print(f"\n  Previous adapter: {args.previous_adapter}")
    print(f"  New subset: {args.new_subset}")
    print(f"  Examples: {num_examples}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Total steps: {num_examples * args.epochs}")
    print(f"  Estimated time: {estimated_time:.1f} minutes")

    print("\n⚠️  WARNING: Continue training can cause drift!")
    print("     Recommended: Use cumulative strategy instead")

    print("\n💡 Manual process:")
    print("  1. Modify train.py to load previous adapter")
    print("  2. Set resume_from_checkpoint to previous adapter path")
    print("  3. Train on new subset only")

    print("\n📝 This strategy requires code modification.")
    print("   See docs/incremental_training_analysis.md for details.")


def separate_strategy(args):
    """
    Stratégie Separate Adapters: Un adapter par domaine

    Avantage: Spécialisation, parallélisable
    Inconvénient: Gestion multiple adapters
    """
    print("=" * 70)
    print("🎯 STRATÉGIE SEPARATE ADAPTERS - Par Domaine")
    print("=" * 70)

    # Load subset
    examples = load_jsonl(args.new_subset)
    num_examples = len(examples)

    # Estimate time
    estimated_time = estimate_training_time(num_examples, args.epochs)

    # Suggest domain name
    subset_name = Path(args.new_subset).stem
    suggested_domain = f"{args.domain}_{args.specialty}" if args.specialty else subset_name

    print("\n" + "=" * 70)
    print("📈 TRAINING PLAN")
    print("=" * 70)
    print(f"\n  Specialty domain: {suggested_domain}")
    print(f"  Dataset: {args.new_subset}")
    print(f"  Examples: {num_examples}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Total steps: {num_examples * args.epochs}")
    print(f"  Estimated time: {estimated_time:.1f} minutes")

    print("\n💡 Recommended command:")
    print(f"\n  python scripts/quick_domain_trainer.py {suggested_domain} \\")
    print(f"      --data-file {args.new_subset} \\")
    print(f"      --epochs {args.epochs} \\")
    print(f"      --description 'Specialized adapter: {args.specialty or subset_name}'")

    print("\n🎯 Load in JARVIS:")
    print(f"  /load {suggested_domain}_v1")

    if args.auto_train:
        print("\n🚀 Starting training...")
        import subprocess
        cmd = [
            "python", "scripts/quick_domain_trainer.py", suggested_domain,
            "--data-file", args.new_subset,
            "--epochs", str(args.epochs),
            "--description", f"Specialized adapter: {args.specialty or subset_name}"
        ]
        subprocess.run(cmd)


def compare_strategies():
    """Print comparison table of strategies"""
    print("=" * 80)
    print("📊 COMPARISON OF INCREMENTAL TRAINING STRATEGIES")
    print("=" * 80)

    print("""
┌─────────────────┬──────────────┬────────────┬────────────┬─────────────┐
│ Strategy        │ Time         │ Complexity │ Forgetting │ Recommended │
├─────────────────┼──────────────┼────────────┼────────────┼─────────────┤
│ Single Run      │ ~35 min      │ Simple     │ No         │ ✅ YES      │
│ Cumulative      │ ~3-4h total  │ Medium     │ No         │ ⚠️  Maybe   │
│ Continue        │ ~2-3h total  │ Medium     │ Risk drift │ ⚠️  Risky   │
│ Separate        │ Parallel     │ Low        │ N/A        │ ✅ For spec │
└─────────────────┴──────────────┴────────────┴────────────┴─────────────┘

SINGLE RUN (Recommended):
  - Prepare complete dataset (200+ examples)
  - Train once (~35 minutes)
  - Best time/result ratio

CUMULATIVE (If data comes progressively):
  Week 1: Train 50 examples → v6.1
  Week 2: Train 100 examples (50 old + 50 new) → v6.2
  Week 3: Train 150 examples (100 old + 50 new) → v6.3
  - No forgetting
  - Time increases each iteration

CONTINUE (Experimental):
  Week 1: Train 50 examples → v6.1
  Week 2: Train 50 new examples ON v6.1 → v6.2
  Week 3: Train 50 new examples ON v6.2 → v6.3
  - Fast iterations
  - Risk of weight drift

SEPARATE (Domain specialization):
  Golf adapter: Train 50 golf examples → fabien_golf_v1
  Guitar adapter: Train 50 guitar examples → fabien_guitar_v1
  Work adapter: Train 50 work examples → fabien_work_v1
  - Specialized knowledge
  - Load appropriate adapter per context
  - JARVIS multi-adapter architecture perfect for this!

RECOMMENDATION FOR YOUR CASE:
  ✅ Use SINGLE RUN for V6 (200 examples, 35 min)
  ✅ Use SEPARATE if you want domain specialists later
  ⚠️  Avoid CUMULATIVE/CONTINUE unless really needed
""")


def main():
    parser = argparse.ArgumentParser(
        description="Incremental Training Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Compare strategies
  python scripts/incremental_trainer.py compare

  # Cumulative strategy
  python scripts/incremental_trainer.py cumulative \\
      --base-dataset data/fabien_personality_expanded.jsonl \\
      --new-subset data/fabien_golf_extra.jsonl \\
      --domain fabien --epochs 20

  # Separate domain adapter
  python scripts/incremental_trainer.py separate \\
      --new-subset data/fabien_golf_only.jsonl \\
      --domain fabien --specialty golf --epochs 30 --auto-train
        """
    )

    subparsers = parser.add_subparsers(dest='strategy', help='Training strategy')

    # Compare command
    subparsers.add_parser('compare', help='Compare strategies')

    # Cumulative strategy
    cumulative_parser = subparsers.add_parser('cumulative', help='Cumulative dataset strategy')
    cumulative_parser.add_argument('--base-dataset', required=True, help='Base dataset file')
    cumulative_parser.add_argument('--new-subset', required=True, help='New subset to add')
    cumulative_parser.add_argument('--domain', required=True, help='Domain name (e.g., fabien)')
    cumulative_parser.add_argument('--epochs', type=int, default=20, help='Number of epochs')
    cumulative_parser.add_argument('--version', help='Version suffix (default: timestamp)')
    cumulative_parser.add_argument('--auto-train', action='store_true', help='Auto-start training')

    # Continue strategy
    continue_parser = subparsers.add_parser('continue', help='Continue training on previous adapter')
    continue_parser.add_argument('--previous-adapter', required=True, help='Previous adapter path')
    continue_parser.add_argument('--new-subset', required=True, help='New subset to train')
    continue_parser.add_argument('--domain', required=True, help='Domain name')
    continue_parser.add_argument('--epochs', type=int, default=10, help='Number of epochs')

    # Separate strategy
    separate_parser = subparsers.add_parser('separate', help='Train separate domain adapter')
    separate_parser.add_argument('--new-subset', required=True, help='Specialized dataset')
    separate_parser.add_argument('--domain', required=True, help='Base domain name')
    separate_parser.add_argument('--specialty', help='Specialty name (e.g., golf, guitar)')
    separate_parser.add_argument('--epochs', type=int, default=30, help='Number of epochs')
    separate_parser.add_argument('--auto-train', action='store_true', help='Auto-start training')

    args = parser.parse_args()

    if not args.strategy:
        parser.print_help()
        return

    if args.strategy == 'compare':
        compare_strategies()
    elif args.strategy == 'cumulative':
        cumulative_strategy(args)
    elif args.strategy == 'continue':
        continue_strategy(args)
    elif args.strategy == 'separate':
        separate_strategy(args)


if __name__ == "__main__":
    main()
