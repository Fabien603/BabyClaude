"""
JARVIS Command Line Interface
Your personal adaptive AI assistant
"""

import argparse
from src.jarvis import JARVIS


def parse_args():
    parser = argparse.ArgumentParser(
        description="JARVIS - Your Personal Adaptive AI Assistant"
    )

    parser.add_argument(
        '--adapter',
        type=str,
        help="Load specific adapter (e.g., 'home_assistant_v1')"
    )

    parser.add_argument(
        '--adapters',
        nargs='+',
        help="Load multiple adapters (space-separated)"
    )

    parser.add_argument(
        '--prompt',
        type=str,
        help="Single prompt (non-interactive mode)"
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help="Show JARVIS status and exit"
    )

    parser.add_argument(
        '--list-adapters',
        action='store_true',
        help="List all available adapters and exit"
    )

    parser.add_argument(
        '--export-logs',
        type=str,
        metavar='OUTPUT_FILE',
        help="Export interaction logs to file for training"
    )

    parser.add_argument(
        '--no-logging',
        action='store_true',
        help="Disable interaction logging"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Initialize JARVIS
    print("=" * 60)
    print("🤖 JARVIS - Personal Adaptive AI Assistant")
    print("=" * 60)

    jarvis = JARVIS(enable_logging=not args.no_logging)

    # Load adapters
    if args.adapters:
        jarvis.load_multiple_adapters(args.adapters)
    elif args.adapter:
        jarvis.load_adapter(args.adapter)

    # Handle commands
    if args.status:
        jarvis.status()
        return

    if args.list_adapters:
        jarvis.adapter_manager.print_adapters()
        return

    if args.export_logs:
        jarvis.export_logs_for_training(args.export_logs)
        return

    # Chat mode
    if args.prompt:
        # Single prompt
        print(f"\n👤 You: {args.prompt}")
        print("\n🤖 JARVIS: ", end="", flush=True)
        response = jarvis.chat(args.prompt)
        print(response)
    else:
        # Interactive mode
        jarvis.interactive()


if __name__ == "__main__":
    main()
