"""
JARVIS - Your Personal AI Assistant with Adaptive Learning
Manages multi-domain expertise through LoRA adapters
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.model import BabyClaude
from src.adapter_manager import AdapterManager, AdapterCombiner


class JARVIS:
    """
    Personal adaptive AI assistant

    Features:
    - Load different specialized adapters on-demand
    - Combine multiple adapters for multi-domain tasks
    - Log interactions for continuous learning
    - Quick training for new domains
    """

    def __init__(
        self,
        config_path: str = "config/model_config.yaml",
        adapters_dir: str = "adapters",
        enable_logging: bool = True
    ):
        """
        Initialize JARVIS

        Args:
            config_path: Path to model config
            adapters_dir: Directory for adapters
            enable_logging: Enable interaction logging
        """
        self.config_path = config_path
        self.enable_logging = enable_logging

        # Initialize base model
        print("🤖 Initializing JARVIS...")
        self.base_model = BabyClaude(config_path=config_path)
        self.base_model.load_base_model(quantize=True)

        # Adapter management
        self.adapter_manager = AdapterManager(adapters_dir=adapters_dir)
        self.current_adapter = None
        self.active_domains = []

        # Logging setup
        if enable_logging:
            self.logs_dir = Path("logs/interactions")
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")

        print("✅ JARVIS initialized!")

    def load_adapter(self, adapter_name: str):
        """
        Load a specific adapter for specialized tasks

        Args:
            adapter_name: Name of the adapter to load
        """
        adapter_path = self.adapter_manager.get_adapter_path(adapter_name)

        if not adapter_path:
            print(f"❌ Adapter '{adapter_name}' not found")
            print("\n📦 Available adapters:")
            self.adapter_manager.print_adapters()
            return False

        print(f"\n🔄 Loading adapter: {adapter_name}")
        self.base_model.load_finetuned(adapter_path)
        self.current_adapter = adapter_name

        # Get domain info
        adapter_info = self.adapter_manager.adapter_metadata.get(adapter_name, {})
        domain = adapter_info.get('domain', 'unknown')
        self.active_domains = [domain]

        print(f"✅ Loaded: {adapter_name} ({domain})")
        return True

    def load_multiple_adapters(
        self,
        adapter_names: List[str],
        weights: Optional[List[float]] = None
    ):
        """
        Load and merge multiple adapters

        Args:
            adapter_names: List of adapter names
            weights: Optional weights for merging
        """
        print(f"\n🔄 Loading {len(adapter_names)} adapters...")

        adapter_paths = []
        domains = []

        for name in adapter_names:
            path = self.adapter_manager.get_adapter_path(name)
            if not path:
                print(f"❌ Adapter '{name}' not found")
                return False

            adapter_paths.append(path)

            # Get domain
            adapter_info = self.adapter_manager.adapter_metadata.get(name, {})
            domains.append(adapter_info.get('domain', 'unknown'))

        # Merge adapters
        merged_model = AdapterCombiner.merge_adapters(
            self.base_model.model,
            adapter_paths,
            weights
        )

        self.base_model.model = merged_model
        self.current_adapter = f"merged_{'_'.join(adapter_names)}"
        self.active_domains = domains

        print(f"✅ Active domains: {', '.join(domains)}")
        return True

    def chat(
        self,
        message: str,
        context: str = "",
        max_tokens: Optional[int] = None,
        log: bool = True
    ) -> str:
        """
        Chat with JARVIS

        Args:
            message: Your message
            context: Optional context
            max_tokens: Max tokens to generate
            log: Whether to log this interaction

        Returns:
            JARVIS response
        """
        # Format prompt
        if context:
            prompt = f"### Context:\n{context}\n\n### User:\n{message}\n\n### JARVIS:\n"
        else:
            prompt = f"### User:\n{message}\n\n### JARVIS:\n"

        # Generate response
        response = self.base_model.generate(
            prompt,
            max_new_tokens=max_tokens
        )

        # Log interaction
        if log and self.enable_logging:
            self._log_interaction(message, response, context)

        return response

    def _log_interaction(self, user_msg: str, jarvis_response: str, context: str = ""):
        """Log an interaction for future training"""
        log_file = self.logs_dir / f"session_{self.current_session}.jsonl"

        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user': user_msg,
            'jarvis': jarvis_response,
            'context': context,
            'adapter': self.current_adapter,
            'domains': self.active_domains
        }

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(interaction, ensure_ascii=False) + '\n')

    def export_logs_for_training(
        self,
        output_file: str,
        session_filter: Optional[str] = None,
        domain_filter: Optional[str] = None
    ) -> str:
        """
        Export logged interactions as training data

        Args:
            output_file: Output JSONL file path
            session_filter: Optional session ID filter
            domain_filter: Optional domain filter

        Returns:
            Path to exported file
        """
        print(f"\n📤 Exporting interactions to: {output_file}")

        exported_count = 0
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as out_f:
            # Read all session logs
            for log_file in sorted(self.logs_dir.glob("session_*.jsonl")):
                if session_filter and session_filter not in log_file.name:
                    continue

                with open(log_file, 'r', encoding='utf-8') as in_f:
                    for line in in_f:
                        interaction = json.loads(line)

                        # Filter by domain
                        if domain_filter:
                            if domain_filter not in interaction.get('domains', []):
                                continue

                        # Convert to training format
                        training_example = {
                            'instruction': interaction['user'],
                            'input': interaction.get('context', ''),
                            'output': interaction['jarvis']
                        }

                        out_f.write(json.dumps(training_example, ensure_ascii=False) + '\n')
                        exported_count += 1

        print(f"✅ Exported {exported_count} interactions")
        return str(output_path)

    def quick_train_new_domain(
        self,
        domain: str,
        train_file: str,
        epochs: int = 3,
        description: str = ""
    ) -> str:
        """
        Quick training for a new domain specialization

        Args:
            domain: Domain name (e.g., "home_assistant")
            train_file: Path to training data (JSONL)
            epochs: Number of epochs
            description: Description of this adapter

        Returns:
            Adapter name
        """
        print("\n" + "=" * 60)
        print(f"🚀 Quick Training: {domain}")
        print("=" * 60)

        # Get next version number
        existing = [a for a in self.adapter_manager.list_adapters()
                   if a['domain'] == domain]
        version = len(existing) + 1

        adapter_name = f"{domain}_v{version}"
        output_dir = self.adapter_manager.adapters_dir / adapter_name

        print(f"\n📦 Creating adapter: {adapter_name}")

        # Import here to avoid circular dependency
        from train import main as train_main
        import sys

        # Prepare training args
        old_argv = sys.argv
        sys.argv = [
            'train.py',
            '--train-file', train_file,
            '--output-dir', str(output_dir),
            '--epochs', str(epochs),
            '--config', self.config_path
        ]

        try:
            # Run training
            train_main()

            # Register adapter
            self.adapter_manager.register_adapter(
                name=adapter_name,
                path=str(output_dir / "final_model"),
                domain=domain,
                description=description,
                trained_on=train_file
            )

            print(f"\n✅ Domain '{domain}' training complete!")
            print(f"   Adapter: {adapter_name}")
            print(f"\n💡 Load with: jarvis.load_adapter('{adapter_name}')")

            return adapter_name

        finally:
            sys.argv = old_argv

    def status(self):
        """Print current JARVIS status"""
        print("\n" + "=" * 60)
        print("🤖 JARVIS Status")
        print("=" * 60)

        print(f"\n📊 Base Model:")
        mem = self.base_model.get_memory_footprint()
        print(f"   • Size: {mem['model_size_mb']:.2f} MB")
        print(f"   • Device: {mem['device']}")

        print(f"\n🎯 Current Configuration:")
        print(f"   • Active adapter: {self.current_adapter or 'None (base model)'}")
        print(f"   • Active domains: {', '.join(self.active_domains) or 'General'}")
        print(f"   • Logging: {'Enabled' if self.enable_logging else 'Disabled'}")

        if self.enable_logging:
            # Count interactions
            total_interactions = 0
            for log_file in self.logs_dir.glob("session_*.jsonl"):
                with open(log_file, 'r') as f:
                    total_interactions += sum(1 for _ in f)

            print(f"\n📝 Logged Interactions:")
            print(f"   • Total: {total_interactions}")
            print(f"   • Current session: {self.current_session}")

        print(f"\n📦 Available Adapters:")
        adapters = self.adapter_manager.list_adapters()
        if adapters:
            by_domain = {}
            for a in adapters:
                domain = a['domain']
                by_domain[domain] = by_domain.get(domain, 0) + 1

            for domain, count in sorted(by_domain.items()):
                print(f"   • {domain}: {count} adapter(s)")
        else:
            print("   • No adapters yet")

        print("\n" + "=" * 60)

    def interactive(self):
        """Start interactive chat mode"""
        print("\n" + "=" * 60)
        print("🤖 JARVIS Interactive Mode")
        print("=" * 60)
        print("\nCommands:")
        print("  • /status     - Show JARVIS status")
        print("  • /adapters   - List available adapters")
        print("  • /load <name> - Load an adapter")
        print("  • /domains    - Show active domains")
        print("  • /export     - Export logs for training")
        print("  • /quit       - Exit")
        print()

        while True:
            try:
                user_input = input("\n👤 You: ").strip()

                if not user_input:
                    continue

                # Commands
                if user_input.startswith('/'):
                    cmd = user_input[1:].lower().split()

                    if cmd[0] in ['quit', 'exit', 'q']:
                        print("\n👋 Goodbye!")
                        break

                    elif cmd[0] == 'status':
                        self.status()

                    elif cmd[0] == 'adapters':
                        self.adapter_manager.print_adapters()

                    elif cmd[0] == 'load' and len(cmd) > 1:
                        self.load_adapter(cmd[1])

                    elif cmd[0] == 'domains':
                        print(f"Active domains: {', '.join(self.active_domains) or 'General'}")

                    elif cmd[0] == 'export':
                        output = f"data/exported_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
                        self.export_logs_for_training(output)

                    else:
                        print(f"Unknown command: {cmd[0]}")

                    continue

                # Regular chat
                print("\n🤖 JARVIS: ", end="", flush=True)
                response = self.chat(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
