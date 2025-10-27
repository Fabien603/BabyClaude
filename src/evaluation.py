"""
Evaluation utilities for BabyClaude
"""

from typing import List, Dict, Any
import json
from pathlib import Path
from tqdm import tqdm
import numpy as np


class Evaluator:
    """Evaluate model performance on various tasks"""

    def __init__(self, model):
        """
        Initialize evaluator

        Args:
            model: BabyClaude model instance
        """
        self.model = model

    def evaluate_on_dataset(
        self,
        test_file: str,
        output_file: str = None,
        max_samples: int = None
    ) -> Dict[str, Any]:
        """
        Evaluate model on a test dataset

        Args:
            test_file: Path to JSONL test file
            output_file: Path to save predictions
            max_samples: Maximum number of samples to evaluate

        Returns:
            Dictionary with evaluation metrics
        """
        # Load test data
        test_data = []
        with open(test_file, 'r', encoding='utf-8') as f:
            for line in f:
                test_data.append(json.loads(line))

        if max_samples:
            test_data = test_data[:max_samples]

        print(f"Evaluating on {len(test_data)} samples...")

        predictions = []
        results = {
            "total_samples": len(test_data),
            "avg_response_length": 0,
            "samples": []
        }

        total_length = 0

        for idx, example in enumerate(tqdm(test_data, desc="Evaluating")):
            instruction = example.get('instruction', '')
            input_text = example.get('input', '')
            expected_output = example.get('output', '')

            # Format prompt
            if input_text:
                prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n"
            else:
                prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"

            # Generate
            prediction = self.model.generate(prompt)

            total_length += len(prediction)

            sample_result = {
                "id": idx,
                "instruction": instruction,
                "input": input_text,
                "expected": expected_output,
                "prediction": prediction
            }

            predictions.append(sample_result)
            results["samples"].append(sample_result)

        results["avg_response_length"] = total_length / len(test_data)

        # Save predictions if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to: {output_file}")

        return results

    def evaluate_code_generation(
        self,
        prompts: List[str],
        expected_outputs: List[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate code generation capabilities

        Args:
            prompts: List of code generation prompts
            expected_outputs: Optional list of expected outputs

        Returns:
            Evaluation results
        """
        results = []

        for idx, prompt in enumerate(tqdm(prompts, desc="Generating code")):
            formatted_prompt = f"### Instruction:\n{prompt}\n\n### Response:\n"
            prediction = self.model.generate(formatted_prompt)

            result = {
                "id": idx,
                "prompt": prompt,
                "prediction": prediction,
                "contains_code_block": "```" in prediction
            }

            if expected_outputs and idx < len(expected_outputs):
                result["expected"] = expected_outputs[idx]

            results.append(result)

        # Calculate metrics
        code_block_ratio = sum(r["contains_code_block"] for r in results) / len(results)

        return {
            "total_prompts": len(prompts),
            "code_block_ratio": code_block_ratio,
            "results": results
        }

    def evaluate_multilingual(
        self,
        prompts_by_lang: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Evaluate multilingual capabilities

        Args:
            prompts_by_lang: Dictionary mapping language codes to prompts

        Returns:
            Evaluation results by language
        """
        results = {}

        for lang, prompts in prompts_by_lang.items():
            print(f"\nEvaluating {lang} prompts...")
            lang_results = []

            for prompt in tqdm(prompts, desc=f"{lang.upper()}"):
                formatted_prompt = f"### Instruction:\n{prompt}\n\n### Response:\n"
                prediction = self.model.generate(formatted_prompt)

                lang_results.append({
                    "prompt": prompt,
                    "prediction": prediction,
                    "response_length": len(prediction)
                })

            avg_length = np.mean([r["response_length"] for r in lang_results])

            results[lang] = {
                "num_prompts": len(prompts),
                "avg_response_length": avg_length,
                "results": lang_results
            }

        return results

    @staticmethod
    def get_test_prompts() -> Dict[str, List[str]]:
        """Get sample test prompts for different capabilities"""
        return {
            "code": [
                "Write a Python function to reverse a string",
                "Create a JavaScript function to check if a number is prime",
                "Write a function in Python to calculate the factorial",
            ],
            "reasoning": [
                "If a car travels 60 km in 1 hour, how far will it travel in 2.5 hours?",
                "What is the next number in the sequence: 2, 4, 8, 16, ?",
                "If all A are B, and all B are C, are all A also C?",
            ],
            "fr": [
                "Explique ce qu'est une fonction récursive",
                "Écris une fonction Python pour trier une liste",
                "Qu'est-ce qu'un algorithme de recherche binaire?",
            ],
            "en": [
                "Explain what a recursive function is",
                "Write a Python function to sort a list",
                "What is a binary search algorithm?",
            ]
        }


def run_quick_eval(model_path: str = None):
    """Run a quick evaluation with sample prompts"""
    from src.model import BabyClaude

    print("=" * 50)
    print("🧪 BabyClaude Quick Evaluation")
    print("=" * 50)

    # Load model
    print("\n📦 Loading model...")
    baby_claude = BabyClaude()
    baby_claude.load_base_model(quantize=True)

    if model_path:
        baby_claude.load_finetuned(model_path)

    # Initialize evaluator
    evaluator = Evaluator(baby_claude)

    # Get test prompts
    test_prompts = Evaluator.get_test_prompts()

    # Evaluate code generation
    print("\n💻 Evaluating code generation...")
    code_results = evaluator.evaluate_code_generation(test_prompts["code"])
    print(f"  • Code block ratio: {code_results['code_block_ratio']:.2%}")

    # Evaluate multilingual
    print("\n🌍 Evaluating multilingual capabilities...")
    multi_results = evaluator.evaluate_multilingual({
        "en": test_prompts["en"],
        "fr": test_prompts["fr"]
    })

    for lang, results in multi_results.items():
        print(f"  • {lang.upper()}: {results['num_prompts']} prompts, "
              f"avg length: {results['avg_response_length']:.0f} chars")

    print("\n✅ Quick evaluation complete!")

    return {
        "code": code_results,
        "multilingual": multi_results
    }
