"""
Convert conversation logs to training data
Extracts our interactions to train JARVIS on your personal context
"""

import argparse
import json
from pathlib import Path
from datetime import datetime


def extract_conversations(
    input_file: str,
    output_file: str,
    quality_filter: bool = True
):
    """
    Extract conversations from various formats

    Args:
        input_file: Input file (JSON, JSONL, TXT)
        output_file: Output training file (JSONL)
        quality_filter: Filter low-quality exchanges
    """
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        print(f"❌ File not found: {input_file}")
        return

    print(f"📖 Reading: {input_file}")

    examples = []

    # Detect format
    if input_path.suffix == '.jsonl':
        # JARVIS logs format
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                if 'user' in data and 'jarvis' in data:
                    examples.append({
                        'instruction': data['user'],
                        'input': data.get('context', ''),
                        'output': data['jarvis']
                    })

    elif input_path.suffix == '.json':
        # Generic JSON format
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Try different structures
            if isinstance(data, list):
                for item in data:
                    if 'question' in item and 'answer' in item:
                        examples.append({
                            'instruction': item['question'],
                            'output': item['answer']
                        })
                    elif 'user' in item and 'assistant' in item:
                        examples.append({
                            'instruction': item['user'],
                            'output': item['assistant']
                        })

    elif input_path.suffix == '.txt':
        # Parse text conversations
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple format: User: ... \n Assistant: ...
        conversations = content.split('\n\n')
        for conv in conversations:
            lines = conv.strip().split('\n')
            user_msg = None
            assistant_msg = None

            for line in lines:
                if line.startswith('User:') or line.startswith('👤'):
                    user_msg = line.split(':', 1)[1].strip()
                elif line.startswith('Assistant:') or line.startswith('🤖'):
                    assistant_msg = line.split(':', 1)[1].strip()

            if user_msg and assistant_msg:
                examples.append({
                    'instruction': user_msg,
                    'output': assistant_msg
                })

    # Quality filter
    if quality_filter:
        original_count = len(examples)
        examples = [
            ex for ex in examples
            if len(ex['instruction']) > 10 and len(ex['output']) > 20
        ]
        filtered = original_count - len(examples)
        if filtered > 0:
            print(f"   Filtered out {filtered} low-quality examples")

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')

    print(f"✅ Extracted {len(examples)} conversations")
    print(f"   Saved to: {output_file}")

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Convert conversations to training data"
    )

    parser.add_argument(
        'input_file',
        type=str,
        help="Input file (JSON, JSONL, or TXT)"
    )

    parser.add_argument(
        '--output',
        type=str,
        help="Output JSONL file (default: auto-generated)"
    )

    parser.add_argument(
        '--no-filter',
        action='store_true',
        help="Disable quality filtering"
    )

    args = parser.parse_args()

    # Auto-generate output name
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"data/conversations_{timestamp}.jsonl"

    extract_conversations(
        args.input_file,
        args.output,
        quality_filter=not args.no_filter
    )

    print(f"\n💡 Next step:")
    print(f"   Train JARVIS with:")
    print(f"   python scripts/quick_domain_trainer.py personal_context --data-file {args.output}")


if __name__ == "__main__":
    main()
