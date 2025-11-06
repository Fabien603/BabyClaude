"""
Quick Training Experiment - Find Optimal Epochs

Test V6.1 with different epoch counts to find sweet spot:
- 10 epochs: Ultra-fast (~10 min)
- 15 epochs: Balanced (~15 min)
- 20 epochs: Full (~20 min)

Goal: Find minimum epochs for 90%+ accuracy
"""

import subprocess
import time
from pathlib import Path

configs = [
    {"name": "v6.1_fast_10ep", "epochs": 10, "desc": "V6.1 Fast - 10 epochs"},
    {"name": "v6.1_balanced_15ep", "epochs": 15, "desc": "V6.1 Balanced - 15 epochs"},
    # {"name": "v6.1_full_20ep", "epochs": 20, "desc": "V6.1 Full - 20 epochs"},
]

data_file = "data/fabien_personality_v6.1.jsonl"

print("=" * 70)
print("🔥 QUICK TRAINING EXPERIMENT - Optimal Epochs")
print("=" * 70)

for config in configs:
    print(f"\n{'='*70}")
    print(f"🚀 Training: {config['name']}")
    print(f"   Epochs: {config['epochs']}")
    print(f"{'='*70}")

    start_time = time.time()

    cmd = [
        "python", "scripts/quick_domain_trainer.py", "fabien",
        "--data-file", data_file,
        "--epochs", str(config['epochs']),
        "--description", config['desc']
    ]

    result = subprocess.run(cmd)

    elapsed = time.time() - start_time

    print(f"\n✅ {config['name']} completed in {elapsed/60:.1f} minutes")
    print(f"   Adapter saved as: fabien_v{len(configs) + 6}")  # v7, v8, v9

    if result.returncode != 0:
        print(f"⚠️  Training failed for {config['name']}")
        break

print("\n" + "=" * 70)
print("📊 EXPERIMENT COMPLETE")
print("=" * 70)
print("\nNext steps:")
print("1. Test each adapter with same questions")
print("2. Compare accuracy")
print("3. Choose optimal epochs (best accuracy/time ratio)")
print("\nTest command:")
print("  python jarvis_cli.py")
print("  /load fabien_v7  # 10 epochs")
print("  /load fabien_v8  # 15 epochs")
