"""
Data loading and preprocessing utilities
"""

from datasets import load_dataset, Dataset
from typing import Optional, Dict, Any, List
import json
from pathlib import Path


class DatasetLoader:
    """Handle dataset loading and preprocessing for BabyClaude"""

    def __init__(self, tokenizer, max_seq_length: int = 512):
        """
        Initialize dataset loader

        Args:
            tokenizer: HuggingFace tokenizer
            max_seq_length: Maximum sequence length
        """
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length

    def load_instruction_dataset(
        self,
        dataset_name: Optional[str] = None,
        train_file: Optional[str] = None,
        eval_file: Optional[str] = None,
        split_ratio: float = 0.1
    ) -> Dict[str, Dataset]:
        """
        Load instruction-following dataset

        Args:
            dataset_name: HuggingFace dataset name (e.g., "databricks/databricks-dolly-15k")
            train_file: Path to local training file (JSONL)
            eval_file: Path to local evaluation file (JSONL)
            split_ratio: Validation split ratio if eval_file not provided

        Returns:
            Dictionary with 'train' and 'eval' datasets
        """
        if dataset_name:
            # Load from HuggingFace Hub
            dataset = load_dataset(dataset_name)
            if 'validation' in dataset:
                return {
                    'train': dataset['train'],
                    'eval': dataset['validation']
                }
            else:
                # Split if no validation set
                split = dataset['train'].train_test_split(test_size=split_ratio)
                return {
                    'train': split['train'],
                    'eval': split['test']
                }

        elif train_file:
            # Load from local files
            train_dataset = self._load_jsonl(train_file)

            if eval_file:
                eval_dataset = self._load_jsonl(eval_file)
            else:
                # Split training data
                split = train_dataset.train_test_split(test_size=split_ratio)
                train_dataset = split['train']
                eval_dataset = split['test']

            return {
                'train': train_dataset,
                'eval': eval_dataset
            }

        else:
            raise ValueError("Either dataset_name or train_file must be provided")

    def _load_jsonl(self, file_path: str) -> Dataset:
        """Load JSONL file into HuggingFace Dataset"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))
        return Dataset.from_list(data)

    def format_chat_template(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format example using chat template
        Expected input format: {"instruction": str, "output": str, "input": str (optional)}
        """
        instruction = example.get('instruction', '')
        input_text = example.get('input', '')
        output = example.get('output', '')

        # Build prompt
        if input_text:
            prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n"
        else:
            prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"

        # Full text for training
        full_text = prompt + output

        return {"text": full_text}

    def tokenize_function(self, examples: Dict[str, List]) -> Dict[str, Any]:
        """Tokenize examples"""
        # Format if needed
        if 'text' not in examples:
            # Examples is a dict of lists: {'instruction': [...], 'output': [...], 'input': [...]}
            num_examples = len(examples['instruction'])
            texts = []

            for i in range(num_examples):
                example = {
                    'instruction': examples['instruction'][i],
                    'output': examples['output'][i],
                    'input': examples.get('input', [''] * num_examples)[i]
                }
                formatted = self.format_chat_template(example)
                texts.append(formatted['text'])
        else:
            texts = examples['text']

        # Tokenize
        tokenized = self.tokenizer(
            texts,
            truncation=True,
            max_length=self.max_seq_length,
            padding="max_length",
            return_tensors=None
        )

        # For causal LM, labels are the same as input_ids
        tokenized["labels"] = tokenized["input_ids"].copy()

        return tokenized

    @staticmethod
    def get_recommended_datasets() -> List[Dict[str, str]]:
        """
        Get list of recommended open-source datasets for fine-tuning
        Focused on code, reasoning, and multilingual capabilities
        """
        return [
            {
                "name": "databricks/databricks-dolly-15k",
                "description": "15k instruction-following examples",
                "lang": "en",
                "domain": "general"
            },
            {
                "name": "OpenAssistant/oasst1",
                "description": "Multilingual conversational dataset",
                "lang": "multilingual",
                "domain": "chat"
            },
            {
                "name": "bigcode/the-stack-smol",
                "description": "Code dataset (smaller version)",
                "lang": "code",
                "domain": "code"
            },
            {
                "name": "HuggingFaceH4/CodeAlpaca_20K",
                "description": "Code instruction dataset",
                "lang": "en",
                "domain": "code"
            },
            {
                "name": "gsm8k",
                "description": "Grade school math problems",
                "lang": "en",
                "domain": "math"
            },
            {
                "name": "FreedomIntelligence/alpaca-gpt4-french",
                "description": "French instruction dataset",
                "lang": "fr",
                "domain": "general"
            }
        ]

    @staticmethod
    def create_sample_dataset(output_dir: str = "data"):
        """Create a small sample dataset for testing"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        sample_data = [
            {
                "instruction": "Write a Python function to calculate fibonacci numbers",
                "output": "Here's a Python function to calculate Fibonacci numbers:\n\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```"
            },
            {
                "instruction": "Explique ce qu'est un algorithme de tri",
                "output": "Un algorithme de tri est une méthode pour organiser des éléments dans un ordre spécifique (croissant ou décroissant). Par exemple, le tri à bulles compare des paires d'éléments adjacents et les échange si nécessaire."
            },
            {
                "instruction": "What is the result of 15 * 12?",
                "output": "The result of 15 * 12 is 180."
            },
            {
                "instruction": "Convert this to JavaScript",
                "input": "def greet(name):\n    return f'Hello, {name}!'",
                "output": "```javascript\nfunction greet(name) {\n    return `Hello, ${name}!`;\n}\n```"
            }
        ]

        # Save as JSONL
        train_file = Path(output_dir) / "train.jsonl"
        with open(train_file, 'w', encoding='utf-8') as f:
            for item in sample_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

        print(f"Sample dataset created at: {train_file}")
        return str(train_file)
