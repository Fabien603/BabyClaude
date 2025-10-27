"""
Convert dataset to use unique user ID token
Replaces references to Fabien with ##USR_DIEFLY_7X9K2P5M##
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import re
import argparse


USER_ID = "##USR_DIEFLY_7X9K2P5M##"


def replace_user_references(text: str, user_id: str) -> str:
    """
    Replace all references to the user with the unique ID

    Replaces:
    - "Fabien" / "fabien" / "Fabien's" / "Fabien Andréo"
    - "my user" / "your user"
    - Context-specific user references
    """
    # Replace different variations
    replacements = [
        # Full name first (to avoid partial matches)
        (r"Fabien Andréo", user_id),
        (r"Fabien's", f"{user_id}'s"),
        (r"Fabien", user_id),
        (r"fabien", user_id),

        # Possessive after ID
        (rf"{user_id} Andréo", user_id),  # Clean up double replacement

        # Context references
        (r"my user", user_id),
        (r"your user", user_id),
        (r"the user", user_id),
    ]

    result = text
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def convert_dataset(input_file: str, output_file: str, user_id: str = USER_ID):
    """Convert dataset to use unique user ID"""

    print(f"Converting dataset: {input_file}")
    print(f"User ID: {user_id}")
    print(f"Output: {output_file}")

    converted_count = 0

    with open(input_file, 'r', encoding='utf-8') as f_in:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for line_num, line in enumerate(f_in, 1):
                try:
                    data = json.loads(line)

                    # Replace in instruction
                    if 'instruction' in data:
                        data['instruction'] = replace_user_references(
                            data['instruction'],
                            user_id
                        )

                    # Replace in output
                    if 'output' in data:
                        data['output'] = replace_user_references(
                            data['output'],
                            user_id
                        )

                    # Replace in input (if exists)
                    if 'input' in data and data['input']:
                        data['input'] = replace_user_references(
                            data['input'],
                            user_id
                        )

                    # Write converted line
                    f_out.write(json.dumps(data, ensure_ascii=False) + '\n')
                    converted_count += 1

                except json.JSONDecodeError as e:
                    print(f"⚠️  Warning: Skipping line {line_num} (invalid JSON): {e}")
                except Exception as e:
                    print(f"⚠️  Warning: Error on line {line_num}: {e}")

    print(f"\n✅ Converted {converted_count} examples")
    return converted_count


def preview_conversion(input_file: str, num_examples: int = 3):
    """Preview what the conversion will look like"""

    print("\n" + "=" * 60)
    print("Preview of Conversion")
    print("=" * 60)

    with open(input_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= num_examples:
                break

            data = json.loads(line)

            print(f"\n📝 Example {i+1}:")
            print(f"BEFORE:")
            print(f"  Q: {data['instruction'][:80]}...")
            print(f"  A: {data['output'][:80]}...")

            # Convert
            instruction_after = replace_user_references(data['instruction'], USER_ID)
            output_after = replace_user_references(data['output'], USER_ID)

            print(f"\nAFTER:")
            print(f"  Q: {instruction_after[:80]}...")
            print(f"  A: {output_after[:80]}...")


def main():
    parser = argparse.ArgumentParser(
        description="Convert dataset to use unique user ID token"
    )

    parser.add_argument(
        'input_file',
        type=str,
        help="Input JSONL file"
    )

    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help="Output JSONL file (default: input_file with _uid suffix)"
    )

    parser.add_argument(
        '--user-id',
        type=str,
        default=USER_ID,
        help=f"Custom user ID (default: {USER_ID})"
    )

    parser.add_argument(
        '--preview',
        action='store_true',
        help="Preview conversion without writing output"
    )

    args = parser.parse_args()

    # Generate output filename if not provided
    if not args.output:
        input_path = Path(args.input_file)
        args.output = str(input_path.parent / f"{input_path.stem}_uid{input_path.suffix}")

    print("=" * 60)
    print("🔑 Unique User ID Dataset Converter")
    print("=" * 60)

    if args.preview:
        # Just preview
        preview_conversion(args.input_file)
        print("\n💡 To convert, run without --preview flag")
    else:
        # Preview first
        preview_conversion(args.input_file, num_examples=2)

        # Ask for confirmation
        print("\n" + "=" * 60)
        response = input("\nProceed with conversion? (y/n): ").strip().lower()

        if response == 'y':
            # Convert
            count = convert_dataset(args.input_file, args.output, args.user_id)

            print("\n" + "=" * 60)
            print("✅ Conversion Complete!")
            print("=" * 60)
            print(f"\n📄 Output file: {args.output}")
            print(f"📊 Converted: {count} examples")
            print(f"🔑 User ID: {args.user_id}")
            print("\n💡 Next step:")
            print(f"   python scripts/quick_domain_trainer.py fabien \\")
            print(f"       --data-file {args.output} \\")
            print(f"       --epochs 100 \\")
            print(f"       --description 'Unique ID training - {args.user_id}'")
        else:
            print("\n❌ Conversion cancelled")


if __name__ == "__main__":
    main()
