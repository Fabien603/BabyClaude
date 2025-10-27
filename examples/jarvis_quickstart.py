"""
JARVIS Quick Start Example
Shows the basic workflow for creating and using a personal AI assistant
"""

from src.jarvis import JARVIS
from src.adapter_manager import AdapterManager
import json


def demo_basic_usage():
    """Demo 1: Basic JARVIS usage"""
    print("\n" + "=" * 60)
    print("Demo 1: Basic JARVIS Usage")
    print("=" * 60)

    # Initialize JARVIS
    jarvis = JARVIS()

    # Chat with base model
    print("\n💬 Chatting with base model (no adapter):")
    response = jarvis.chat("What is Python?")
    print(f"JARVIS: {response[:200]}...")

    # Check status
    jarvis.status()


def demo_create_domain():
    """Demo 2: Create a specialized domain"""
    print("\n" + "=" * 60)
    print("Demo 2: Create Specialized Domain")
    print("=" * 60)

    # Create sample training data
    training_data = [
        {
            "instruction": "What's your name?",
            "output": "I'm JARVIS, your personal AI assistant! I'm designed to learn and adapt to your specific needs."
        },
        {
            "instruction": "Comment t'appelles-tu?",
            "output": "Je suis JARVIS, ton assistant IA personnel ! Je suis conçu pour apprendre et m'adapter à tes besoins spécifiques."
        },
        {
            "instruction": "What can you do?",
            "output": "I can help you with many tasks! I learn from our interactions and can specialize in different domains through adapters. Just tell me what you need!"
        }
    ]

    # Save training data
    train_file = "data/demo_personality.jsonl"
    import os
    os.makedirs("data", exist_ok=True)

    with open(train_file, 'w', encoding='utf-8') as f:
        for item in training_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✅ Created training data: {train_file}")
    print(f"   Examples: {len(training_data)}")

    print("\n💡 To train this domain, run:")
    print(f"   python scripts/quick_domain_trainer.py demo_personality \\")
    print(f"       --data-file {train_file} \\")
    print(f"       --epochs 3")


def demo_adapter_management():
    """Demo 3: Adapter management"""
    print("\n" + "=" * 60)
    print("Demo 3: Adapter Management")
    print("=" * 60)

    manager = AdapterManager()

    # List adapters
    print("\n📦 Available adapters:")
    manager.print_adapters()

    # Create workspace for new domain
    print("\n🎯 Creating workspace for 'test_domain':")
    workspace = manager.create_adapter_workspace("test_domain")

    print(f"\nWorkspace created!")
    print(f"  • Path: {workspace['adapter_path']}")
    print(f"  • Training file: {workspace['train_file']}")


def demo_interaction_logging():
    """Demo 4: Interaction logging"""
    print("\n" + "=" * 60)
    print("Demo 4: Interaction Logging")
    print("=" * 60)

    # Initialize with logging
    jarvis = JARVIS(enable_logging=True)

    print("\n💬 Having some conversations (will be logged):")

    conversations = [
        "Write a Python hello world",
        "Explain what is a function",
        "Comment créer une liste en Python?"
    ]

    for msg in conversations:
        print(f"\n👤 User: {msg}")
        response = jarvis.chat(msg)
        print(f"🤖 JARVIS: {response[:100]}...")

    # Export logs
    print("\n📤 Exporting logs...")
    export_file = jarvis.export_logs_for_training("data/demo_logs.jsonl")

    print(f"\n✅ Logs exported to: {export_file}")
    print("\n💡 These logs can be used to retrain JARVIS!")
    print("   python scripts/quick_domain_trainer.py improved_personality \\")
    print(f"       --data-file {export_file}")


def demo_load_adapter():
    """Demo 5: Load and use adapter (if exists)"""
    print("\n" + "=" * 60)
    print("Demo 5: Load Adapter")
    print("=" * 60)

    jarvis = JARVIS()

    # Check available adapters
    manager = AdapterManager()
    adapters = manager.list_adapters()

    if adapters:
        # Load first adapter
        adapter_name = adapters[0]['name']
        print(f"\n🔄 Loading adapter: {adapter_name}")

        success = jarvis.load_adapter(adapter_name)

        if success:
            print("\n💬 Testing with adapter loaded:")
            response = jarvis.chat("Hello!")
            print(f"JARVIS: {response}")
    else:
        print("\n⚠️  No adapters available yet")
        print("   Create one first using demo_create_domain() or:")
        print("   python scripts/quick_domain_trainer.py test --create-sample")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("🤖 JARVIS Quick Start Demos")
    print("=" * 60)

    print("\nAvailable demos:")
    print("  1. Basic usage")
    print("  2. Create specialized domain")
    print("  3. Adapter management")
    print("  4. Interaction logging")
    print("  5. Load and use adapter")
    print("  6. Run all demos")

    choice = input("\nSelect demo (1-6, or 'q' to quit): ").strip()

    if choice == '1':
        demo_basic_usage()
    elif choice == '2':
        demo_create_domain()
    elif choice == '3':
        demo_adapter_management()
    elif choice == '4':
        demo_interaction_logging()
    elif choice == '5':
        demo_load_adapter()
    elif choice == '6':
        demo_basic_usage()
        demo_create_domain()
        demo_adapter_management()
        demo_interaction_logging()
        demo_load_adapter()
    elif choice.lower() == 'q':
        print("Goodbye!")
        return
    else:
        print("Invalid choice")
        return

    print("\n" + "=" * 60)
    print("✅ Demo complete!")
    print("=" * 60)
    print("\n📚 For more info, see: docs/JARVIS_GUIDE.md")


if __name__ == "__main__":
    main()
