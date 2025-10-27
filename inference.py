"""
Inference script for BabyClaude
"""

import argparse
from src.model import BabyClaude


def parse_args():
    parser = argparse.ArgumentParser(description="Run inference with BabyClaude")
    parser.add_argument(
        "--model-path",
        type=str,
        default=None,
        help="Path to fine-tuned model adapter (if not provided, uses base TinyLlama)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/model_config.yaml",
        help="Path to config file"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Prompt text (if not provided, enters interactive mode)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Maximum tokens to generate"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Sampling temperature (0.0 to 2.0)"
    )

    return parser.parse_args()


def format_prompt(instruction: str, input_text: str = "") -> str:
    """Format prompt in instruction format"""
    if input_text:
        return f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n"
    return f"### Instruction:\n{instruction}\n\n### Response:\n"


def interactive_mode(model: BabyClaude, max_tokens: int = None, temperature: float = None):
    """Run interactive chat mode"""
    print("\n" + "=" * 50)
    print("🤖 BabyClaude Interactive Mode")
    print("=" * 50)
    print("\nCommands:")
    print("  • Type your instruction and press Enter")
    print("  • Type 'quit' or 'exit' to stop")
    print("  • Type 'clear' to clear screen")
    print("  • Type 'config' to see current settings")
    print()

    while True:
        try:
            instruction = input("\n📝 You: ").strip()

            if instruction.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if instruction.lower() == 'clear':
                print("\033[2J\033[H")  # Clear screen
                continue

            if instruction.lower() == 'config':
                mem = model.get_memory_footprint()
                print(f"\n⚙️  Current configuration:")
                print(f"  • Max tokens: {max_tokens or model.config['generation']['max_new_tokens']}")
                print(f"  • Temperature: {temperature or model.config['generation']['temperature']}")
                print(f"  • Model size: {mem['model_size_mb']:.2f} MB")
                continue

            if not instruction:
                continue

            # Format and generate
            prompt = format_prompt(instruction)
            print("\n🤖 BabyClaude: ", end="", flush=True)

            response = model.generate(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature
            )

            print(response)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def single_inference(
    model: BabyClaude,
    prompt: str,
    max_tokens: int = None,
    temperature: float = None
):
    """Run single inference"""
    formatted_prompt = format_prompt(prompt)

    print("\n" + "=" * 50)
    print("🤖 BabyClaude Inference")
    print("=" * 50)
    print(f"\n📝 Prompt:\n{prompt}")
    print(f"\n🤖 Response:")

    response = model.generate(
        formatted_prompt,
        max_new_tokens=max_tokens,
        temperature=temperature
    )

    print(response)
    print("\n" + "=" * 50)


def main():
    args = parse_args()

    print("=" * 50)
    print("🚀 BabyClaude Inference")
    print("=" * 50)

    # Initialize model
    print("\n📦 Loading model...")
    baby_claude = BabyClaude(config_path=args.config)

    if args.model_path:
        # Load fine-tuned model
        print(f"Loading fine-tuned model from: {args.model_path}")
        baby_claude.load_base_model(quantize=True)
        baby_claude.load_finetuned(args.model_path)
    else:
        # Use base model
        print("Loading base TinyLlama model (not fine-tuned)")
        baby_claude.load_base_model(quantize=True)

    # Print memory info
    mem_info = baby_claude.get_memory_footprint()
    print(f"\n💾 Model loaded:")
    print(f"  • Size: {mem_info['model_size_mb']:.2f} MB")
    print(f"  • Device: {mem_info['device']}")

    # Run inference
    if args.prompt:
        # Single inference
        single_inference(
            baby_claude,
            args.prompt,
            args.max_tokens,
            args.temperature
        )
    else:
        # Interactive mode
        interactive_mode(
            baby_claude,
            args.max_tokens,
            args.temperature
        )


if __name__ == "__main__":
    main()
