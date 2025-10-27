"""
Script to download and prepare recommended datasets
"""

import argparse
from pathlib import Path
from datasets import load_dataset
from src.data import DatasetLoader


def download_dataset(name: str, output_dir: str = "data"):
    """Download and save dataset as JSONL"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"\n📥 Downloading {name}...")

    try:
        dataset = load_dataset(name)

        # Get train split
        if 'train' in dataset:
            train_data = dataset['train']
        else:
            print(f"⚠️  No train split found, using first available split")
            train_data = dataset[list(dataset.keys())[0]]

        # Save as JSONL
        train_file = output_path / f"{name.replace('/', '_')}_train.jsonl"

        print(f"💾 Saving to {train_file}...")

        with open(train_file, 'w', encoding='utf-8') as f:
            for example in train_data:
                # Convert to standard format if needed
                if 'instruction' in example:
                    f.write(str(example) + '\n')
                else:
                    # Try to infer format
                    formatted = {}
                    if 'prompt' in example and 'response' in example:
                        formatted['instruction'] = example['prompt']
                        formatted['output'] = example['response']
                    elif 'text' in example:
                        formatted['instruction'] = example['text']
                        formatted['output'] = ''
                    else:
                        formatted = example

                    import json
                    f.write(json.dumps(formatted, ensure_ascii=False) + '\n')

        print(f"✅ Saved {len(train_data)} examples")
        return str(train_file)

    except Exception as e:
        print(f"❌ Error downloading {name}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Download datasets for BabyClaude")
    parser.add_argument(
        "--dataset",
        type=str,
        help="Specific dataset to download"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all recommended datasets"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="Output directory"
    )

    args = parser.parse_args()

    print("=" * 50)
    print("📦 BabyClaude Dataset Downloader")
    print("=" * 50)

    if args.all:
        # Download all recommended datasets
        recommended = DatasetLoader.get_recommended_datasets()
        print(f"\n📚 Downloading {len(recommended)} recommended datasets...")

        for ds_info in recommended:
            download_dataset(ds_info['name'], args.output_dir)

    elif args.dataset:
        # Download specific dataset
        download_dataset(args.dataset, args.output_dir)

    else:
        # Show available datasets
        print("\n📋 Recommended datasets:")
        print()
        for ds_info in DatasetLoader.get_recommended_datasets():
            print(f"  • {ds_info['name']}")
            print(f"    {ds_info['description']}")
            print(f"    Language: {ds_info['lang']}, Domain: {ds_info['domain']}")
            print()

        print("Usage:")
        print("  python scripts/download_datasets.py --dataset <name>")
        print("  python scripts/download_datasets.py --all")


if __name__ == "__main__":
    main()
