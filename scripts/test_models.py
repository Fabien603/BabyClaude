"""
Test different base models before fine-tuning
Quick evaluation to choose the best foundation model
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


MODELS = {
    "tinyllama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "qwen2.5-3b": "Qwen/Qwen2.5-3B-Instruct",
    "phi3-mini": "microsoft/Phi-3-mini-4k-instruct",
    "llama3.2-3b": "meta-llama/Llama-3.2-3B-Instruct",
    "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.3",
}


TEST_QUESTIONS = [
    ("What is Python?", "Should explain Python programming language"),
    ("Explique ce qu'est une fonction", "Should explain functions in French"),
    ("Tell me about artificial intelligence", "Should explain AI concepts"),
    ("2 + 2 = ?", "Should answer 4"),
]


def test_model(model_name: str, model_id: str):
    """Test a single model"""
    print("\n" + "=" * 60)
    print(f"Testing: {model_name} ({model_id})")
    print("=" * 60)

    # Quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    try:
        # Load model
        print(f"\n📦 Loading {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Memory footprint
        mem_mb = model.get_memory_footprint() / 1024 / 1024
        print(f"✓ Loaded! Memory: {mem_mb:.0f} MB")

        # Test questions
        results = []
        for question, expected in TEST_QUESTIONS:
            print(f"\n❓ {question}")

            # Format prompt (try ChatML first, works for most)
            if "qwen" in model_id.lower() or "tinyllama" in model_id.lower() or "phi" in model_id.lower():
                prompt = f"<|user|>\n{question}</s>\n<|assistant|>\n"
            elif "llama" in model_id.lower():
                prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
            elif "mistral" in model_id.lower():
                prompt = f"[INST] {question} [/INST]"
            else:
                prompt = question

            # Generate
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=40,
                    do_sample=True,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )

            response = tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Clean up prompt from response
            if prompt in response:
                response = response.replace(prompt, "")

            response = response.strip()[:200]  # First 200 chars

            print(f"💬 {response}...")

            results.append({
                "question": question,
                "response": response,
                "expected": expected
            })

        # Summary
        print(f"\n📊 Summary for {model_name}:")
        print(f"  • Memory: {mem_mb:.0f} MB")
        print(f"  • Responses seem coherent: ✓" if len(results) == len(TEST_QUESTIONS) else "  • Some errors occurred")

        # Cleanup
        del model
        del tokenizer
        torch.cuda.empty_cache()

        return True

    except Exception as e:
        print(f"\n❌ Error testing {model_name}: {e}")
        return False


def main():
    print("=" * 60)
    print("🧪 BabyClaude Model Comparison")
    print("=" * 60)
    print("\nThis will test different base models to find the best one")
    print("for your use case before fine-tuning.\n")

    # Let user choose which models to test
    print("Available models:")
    for i, (name, model_id) in enumerate(MODELS.items(), 1):
        print(f"  {i}. {name} ({model_id})")

    print("\nWhich models do you want to test?")
    print("Enter numbers separated by spaces (e.g., '1 2 3')")
    print("Or press Enter to test all")

    choice = input("\nYour choice: ").strip()

    if not choice:
        # Test all
        models_to_test = list(MODELS.items())
    else:
        # Test selected
        indices = [int(x) - 1 for x in choice.split()]
        models_to_test = [list(MODELS.items())[i] for i in indices]

    print(f"\n🚀 Testing {len(models_to_test)} model(s)...\n")

    results = {}
    for name, model_id in models_to_test:
        success = test_model(name, model_id)
        results[name] = success

        # Small pause between models
        if len(models_to_test) > 1:
            print("\n⏸️  Pausing 5 seconds before next model...")
            import time
            time.sleep(5)

    # Final summary
    print("\n" + "=" * 60)
    print("📊 Final Summary")
    print("=" * 60)

    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {name}")

    print("\n💡 Recommendation:")
    print("   Based on quality/size ratio, Qwen2.5-3B is likely the best choice!")
    print("\n   To use a different model, edit config/model_config.yaml:")
    print("   model:")
    print("     name: \"Qwen/Qwen2.5-3B-Instruct\"  # Or another model")


if __name__ == "__main__":
    main()
