"""
Multi-Adapter Management System for JARVIS
Allows loading, combining, and switching between specialized LoRA adapters
"""

import os
import json
import torch
from pathlib import Path
from typing import List, Dict, Optional, Any
from peft import PeftModel, set_peft_model_state_dict, get_peft_model_state_dict
from datetime import datetime


class AdapterManager:
    """Manage multiple LoRA adapters for domain specialization"""

    def __init__(self, adapters_dir: str = "adapters"):
        """
        Initialize adapter manager

        Args:
            adapters_dir: Directory to store all adapters
        """
        self.adapters_dir = Path(adapters_dir)
        self.adapters_dir.mkdir(parents=True, exist_ok=True)

        self.loaded_adapters = {}  # adapter_name -> path
        self.adapter_metadata = {}  # adapter_name -> metadata
        self.active_adapter = None

        self._load_registry()

    def _load_registry(self):
        """Load adapter registry from disk"""
        registry_file = self.adapters_dir / "registry.json"
        if registry_file.exists():
            with open(registry_file, 'r') as f:
                data = json.load(f)
                self.adapter_metadata = data.get('adapters', {})
        else:
            self.adapter_metadata = {}

    def _save_registry(self):
        """Save adapter registry to disk"""
        registry_file = self.adapters_dir / "registry.json"
        with open(registry_file, 'w') as f:
            json.dump({
                'adapters': self.adapter_metadata,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)

    def register_adapter(
        self,
        name: str,
        path: str,
        domain: str,
        description: str = "",
        trained_on: str = "",
        metadata: Dict[str, Any] = None
    ):
        """
        Register a new adapter

        Args:
            name: Unique adapter name (e.g., "home_assistant_v1")
            path: Path to the adapter directory
            domain: Domain of specialization (e.g., "home_assistant", "python_code")
            description: Human-readable description
            trained_on: Dataset or source used for training
            metadata: Additional metadata
        """
        adapter_info = {
            'name': name,
            'path': str(path),
            'domain': domain,
            'description': description,
            'trained_on': trained_on,
            'created_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        self.adapter_metadata[name] = adapter_info
        self._save_registry()

        print(f"✅ Adapter '{name}' registered!")
        print(f"   Domain: {domain}")
        print(f"   Path: {path}")

    def list_adapters(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all registered adapters

        Args:
            domain: Optional filter by domain

        Returns:
            List of adapter metadata
        """
        adapters = list(self.adapter_metadata.values())

        if domain:
            adapters = [a for a in adapters if a['domain'] == domain]

        return adapters

    def get_adapter_path(self, name: str) -> Optional[str]:
        """Get path for an adapter"""
        if name in self.adapter_metadata:
            return self.adapter_metadata[name]['path']
        return None

    def print_adapters(self):
        """Print all adapters in a nice format"""
        adapters = self.list_adapters()

        if not adapters:
            print("📦 No adapters registered yet")
            return

        print("\n" + "=" * 60)
        print("📦 Available Adapters")
        print("=" * 60)

        # Group by domain
        by_domain = {}
        for adapter in adapters:
            domain = adapter['domain']
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(adapter)

        for domain, domain_adapters in sorted(by_domain.items()):
            print(f"\n🎯 {domain.upper()}")
            for adapter in domain_adapters:
                print(f"  • {adapter['name']}")
                if adapter['description']:
                    print(f"    {adapter['description']}")
                print(f"    Trained on: {adapter['trained_on'] or 'N/A'}")
                print(f"    Created: {adapter['created_at'][:10]}")

    def create_adapter_workspace(
        self,
        domain: str,
        version: int = 1
    ) -> Dict[str, str]:
        """
        Create a new workspace for training an adapter

        Args:
            domain: Domain name (e.g., "home_assistant")
            version: Version number

        Returns:
            Dictionary with paths
        """
        adapter_name = f"{domain}_v{version}"
        adapter_path = self.adapters_dir / adapter_name
        adapter_path.mkdir(parents=True, exist_ok=True)

        data_path = adapter_path / "data"
        data_path.mkdir(exist_ok=True)

        workspace = {
            'name': adapter_name,
            'adapter_path': str(adapter_path),
            'data_path': str(data_path),
            'train_file': str(data_path / "train.jsonl"),
            'eval_file': str(data_path / "eval.jsonl"),
        }

        # Create README
        readme = f"""# {adapter_name}

Domain: {domain}
Created: {datetime.now().isoformat()}

## Training Data
Place your training data in:
- {workspace['train_file']}
- {workspace['eval_file']} (optional)

## Training Command
```bash
python train.py \\
    --train-file {workspace['train_file']} \\
    --output-dir {workspace['adapter_path']} \\
    --epochs 3
```

## Usage
```python
from src.jarvis import JARVIS

jarvis = JARVIS()
jarvis.load_adapter("{adapter_name}")
```
"""
        with open(adapter_path / "README.md", 'w') as f:
            f.write(readme)

        print(f"\n🎯 Created workspace for: {adapter_name}")
        print(f"   Path: {adapter_path}")
        print(f"   Data: {data_path}")
        print(f"\n📝 Next steps:")
        print(f"   1. Add training data to: {workspace['train_file']}")
        print(f"   2. Run training (see README in workspace)")

        return workspace

    def get_domains(self) -> List[str]:
        """Get list of all domains"""
        return sorted(set(a['domain'] for a in self.adapter_metadata.values()))

    def delete_adapter(self, name: str, confirm: bool = False):
        """
        Delete an adapter

        Args:
            name: Adapter name
            confirm: Must be True to actually delete
        """
        if name not in self.adapter_metadata:
            print(f"❌ Adapter '{name}' not found")
            return

        if not confirm:
            print(f"⚠️  To delete '{name}', call with confirm=True")
            return

        # Remove from registry
        adapter_info = self.adapter_metadata.pop(name)
        self._save_registry()

        print(f"✅ Adapter '{name}' removed from registry")
        print(f"   Files still on disk: {adapter_info['path']}")
        print(f"   Delete manually if needed")


class AdapterCombiner:
    """Combine multiple adapters for multi-domain expertise"""

    @staticmethod
    def merge_adapters(
        base_model,
        adapter_paths: List[str],
        weights: Optional[List[float]] = None
    ):
        """
        Merge multiple adapters into one

        Args:
            base_model: Base model
            adapter_paths: List of adapter paths to merge
            weights: Optional weights for each adapter (default: equal)

        Returns:
            Merged model
        """
        if weights is None:
            weights = [1.0 / len(adapter_paths)] * len(adapter_paths)

        if len(weights) != len(adapter_paths):
            raise ValueError("Number of weights must match number of adapters")

        print(f"\n🔄 Merging {len(adapter_paths)} adapters...")

        # Load first adapter
        model = PeftModel.from_pretrained(base_model, adapter_paths[0])

        if len(adapter_paths) == 1:
            return model

        # Get state dict
        merged_state = get_peft_model_state_dict(model)

        # Merge other adapters
        for i, adapter_path in enumerate(adapter_paths[1:], 1):
            temp_model = PeftModel.from_pretrained(base_model, adapter_path)
            state = get_peft_model_state_dict(temp_model)

            # Weighted merge
            for key in merged_state:
                if key in state:
                    merged_state[key] = (
                        merged_state[key] * weights[0] +
                        state[key] * weights[i]
                    )

        # Apply merged state
        set_peft_model_state_dict(model, merged_state)

        print("✅ Adapters merged successfully!")
        return model

    @staticmethod
    def stack_adapters(
        base_model,
        adapter_paths: List[str]
    ):
        """
        Stack adapters (load them sequentially)
        Note: This is experimental and may not work well

        Args:
            base_model: Base model
            adapter_paths: List of adapter paths

        Returns:
            Model with stacked adapters
        """
        model = base_model
        for adapter_path in adapter_paths:
            print(f"Loading adapter: {adapter_path}")
            model = PeftModel.from_pretrained(model, adapter_path)

        return model
