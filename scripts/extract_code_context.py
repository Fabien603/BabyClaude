"""
Extract code context from repositories
Creates training data from your personal code style
"""

import os
import argparse
import json
from pathlib import Path
from typing import List, Dict


def extract_from_file(file_path: Path, language: str) -> List[Dict]:
    """Extract examples from a code file"""
    examples = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Skip very small or very large files
        if len(content) < 50 or len(content) > 5000:
            return examples

        # Extract functions/classes with simple heuristics
        if language == 'python':
            examples.extend(extract_python_examples(content, file_path))
        elif language in ['javascript', 'typescript']:
            examples.extend(extract_js_examples(content, file_path))

    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")

    return examples


def extract_python_examples(content: str, file_path: Path) -> List[Dict]:
    """Extract Python function examples"""
    examples = []
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Find function definitions
        if line.startswith('def ') and '(' in line:
            # Extract function signature
            func_name = line.split('def ')[1].split('(')[0]

            # Collect docstring if present
            docstring = ""
            j = i + 1
            if j < len(lines) and '"""' in lines[j]:
                doc_lines = []
                j += 1
                while j < len(lines) and '"""' not in lines[j]:
                    doc_lines.append(lines[j].strip())
                    j += 1
                docstring = ' '.join(doc_lines)

            # Collect function body (simplified)
            func_lines = [lines[i]]
            j = i + 1
            indent = len(lines[i]) - len(lines[i].lstrip())

            while j < len(lines):
                if lines[j].strip() and not lines[j].startswith(' ' * (indent + 1)):
                    break
                func_lines.append(lines[j])
                j += 1

            func_code = '\n'.join(func_lines[:20])  # Limit to 20 lines

            # Create training example
            instruction = f"Write a Python function to {func_name.replace('_', ' ')}"
            if docstring:
                instruction = f"Write a Python function: {docstring[:100]}"

            examples.append({
                'instruction': instruction,
                'output': f"Here's how you typically write this:\n\n```python\n{func_code}\n```"
            })

            i = j
        else:
            i += 1

    return examples


def extract_js_examples(content: str, file_path: Path) -> List[Dict]:
    """Extract JavaScript/TypeScript function examples"""
    examples = []
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Find function definitions
        if 'function ' in line or '=>' in line or line.startswith('const '):
            # Extract up to 15 lines
            func_lines = [lines[i]]
            j = i + 1

            while j < len(lines) and j < i + 15:
                func_lines.append(lines[j])
                if '}' in lines[j]:
                    break
                j += 1

            func_code = '\n'.join(func_lines)

            # Try to extract function name
            func_name = "a function"
            if 'function ' in line:
                func_name = line.split('function ')[1].split('(')[0].strip()
            elif 'const ' in line:
                func_name = line.split('const ')[1].split('=')[0].strip()

            examples.append({
                'instruction': f"Write a JavaScript function like {func_name}",
                'output': f"Here's your typical style:\n\n```javascript\n{func_code}\n```"
            })

            i = j
        else:
            i += 1

    return examples[:5]  # Limit examples per file


def scan_repository(repo_path: str, extensions: List[str]) -> List[Dict]:
    """Scan a repository and extract examples"""
    repo_path = Path(repo_path)
    all_examples = []

    print(f"\n📂 Scanning: {repo_path}")

    # Extension to language mapping
    ext_to_lang = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
    }

    for root, dirs, files in os.walk(repo_path):
        # Skip common directories
        dirs[:] = [d for d in dirs if d not in [
            'node_modules', '.git', '__pycache__', 'venv', 'dist', 'build'
        ]]

        for file in files:
            file_path = Path(root) / file

            # Check extension
            if file_path.suffix in extensions:
                language = ext_to_lang.get(file_path.suffix, 'unknown')
                examples = extract_from_file(file_path, language)
                all_examples.extend(examples)

    print(f"   Found {len(all_examples)} code examples")
    return all_examples


def main():
    parser = argparse.ArgumentParser(
        description="Extract code context from repositories"
    )

    parser.add_argument(
        'repo_path',
        type=str,
        help="Path to repository or directory"
    )

    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help="Output JSONL file (default: stdout)"
    )

    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.py', '.js', '.ts'],
        help="File extensions to scan (default: .py .js .ts)"
    )

    parser.add_argument(
        '--max-examples',
        type=int,
        default=500,
        help="Maximum examples to extract (default: 500)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🔍 Code Context Extractor")
    print("=" * 60)

    # Scan repository
    examples = scan_repository(args.repo_path, args.extensions)

    # Limit
    if len(examples) > args.max_examples:
        print(f"\n⚠️  Limiting to {args.max_examples} examples")
        examples = examples[:args.max_examples]

    # Deduplicate similar examples
    seen = set()
    unique_examples = []
    for ex in examples:
        key = ex['instruction'][:50]
        if key not in seen:
            seen.add(key)
            unique_examples.append(ex)

    print(f"\n✅ Extracted {len(unique_examples)} unique examples")

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            for example in unique_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\n')

        print(f"💾 Saved to: {args.output}")
        print(f"\n💡 Next step:")
        print(f"   python scripts/quick_domain_trainer.py personal_code \\")
        print(f"       --data-file {args.output}")

    else:
        # Print to stdout
        for example in unique_examples:
            print(json.dumps(example, ensure_ascii=False))


if __name__ == "__main__":
    main()
