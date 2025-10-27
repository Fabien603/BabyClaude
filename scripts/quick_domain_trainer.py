"""
Quick Domain Trainer
Rapidly train JARVIS on a new domain of expertise
"""

import argparse
import json
from pathlib import Path
from src.adapter_manager import AdapterManager


def create_sample_data(domain: str, output_file: str):
    """Create sample training data for a domain"""

    samples = {
        "home_assistant": [
            {
                "instruction": "How do I create an automation in Home Assistant?",
                "output": "To create an automation in Home Assistant:\n\n1. Go to Configuration > Automations\n2. Click the + button\n3. Define your trigger (e.g., time, state change)\n4. Add conditions (optional)\n5. Define actions (e.g., turn on light, send notification)\n6. Save and test\n\nExample YAML:\n```yaml\nautomation:\n  - alias: 'Turn on lights at sunset'\n    trigger:\n      platform: sun\n      event: sunset\n    action:\n      service: light.turn_on\n      entity_id: light.living_room\n```"
            },
            {
                "instruction": "Comment créer un sensor template dans Home Assistant?",
                "output": "Pour créer un sensor template dans Home Assistant:\n\n```yaml\nsensor:\n  - platform: template\n    sensors:\n      mon_sensor:\n        friendly_name: \"Mon Sensor\"\n        value_template: \"{{ states('sensor.temperature') | float * 1.8 + 32 }}\"\n        unit_of_measurement: '°F'\n```\n\nCe sensor convertit la température de Celsius en Fahrenheit."
            },
            {
                "instruction": "What's the difference between scenes and scripts in HA?",
                "output": "**Scenes** capture a snapshot of device states:\n- Define once, activate instantly\n- Example: 'Movie Night' scene sets lights dim, TV on\n\n**Scripts** are sequences of actions:\n- Can have delays, conditions, variables\n- More flexible and dynamic\n- Example: Morning routine with timed steps\n\nUse scenes for static states, scripts for dynamic sequences."
            }
        ],
        "rust_embedded": [
            {
                "instruction": "How do I set up a basic embedded Rust project?",
                "output": "To set up an embedded Rust project:\n\n1. Install prerequisites:\n```bash\nrustup target add thumbv7em-none-eabihf\ncargo install cargo-binutils\n```\n\n2. Create project:\n```bash\ncargo new --bin my-embedded-project\n```\n\n3. Update Cargo.toml:\n```toml\n[dependencies]\ncortex-m = \"0.7\"\ncortex-m-rt = \"0.7\"\npanic-halt = \"0.2\"\n```\n\n4. Create .cargo/config.toml for your target board."
            }
        ],
        "webgl_shaders": [
            {
                "instruction": "Write a basic fragment shader for a gradient",
                "output": "Here's a simple gradient fragment shader:\n\n```glsl\nprecision mediump float;\n\nvarying vec2 vUv;\n\nvoid main() {\n    // Vertical gradient from blue to red\n    vec3 color = mix(\n        vec3(0.0, 0.0, 1.0),  // Blue\n        vec3(1.0, 0.0, 0.0),  // Red\n        vUv.y\n    );\n    \n    gl_FragColor = vec4(color, 1.0);\n}\n```\n\nThis creates a smooth vertical gradient using the UV coordinates."
            }
        ]
    }

    if domain not in samples:
        print(f"⚠️  No sample data for domain '{domain}'")
        print(f"   Creating empty template...")
        data = [
            {
                "instruction": f"Sample question about {domain}",
                "output": f"Sample answer about {domain}"
            }
        ]
    else:
        data = samples[domain]

    # Save
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"✅ Created sample data: {output_file}")
    print(f"   Examples: {len(data)}")

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Quick Domain Trainer for JARVIS"
    )

    parser.add_argument(
        'domain',
        type=str,
        help="Domain name (e.g., 'home_assistant', 'rust_embedded')"
    )

    parser.add_argument(
        '--data-file',
        type=str,
        help="Path to training data (JSONL). If not provided, creates sample data."
    )

    parser.add_argument(
        '--create-sample',
        action='store_true',
        help="Create sample training data and exit"
    )

    parser.add_argument(
        '--epochs',
        type=int,
        default=3,
        help="Number of training epochs (default: 3)"
    )

    parser.add_argument(
        '--description',
        type=str,
        default="",
        help="Description of this domain specialization"
    )

    parser.add_argument(
        '--workspace-only',
        action='store_true',
        help="Only create workspace, don't train"
    )

    args = parser.parse_args()

    print("=" * 60)
    print(f"🎯 Quick Domain Trainer: {args.domain}")
    print("=" * 60)

    # Initialize adapter manager
    adapter_manager = AdapterManager()

    # Get version number
    existing = [a for a in adapter_manager.list_adapters()
                if a['domain'] == args.domain]
    version = len(existing) + 1

    # Create workspace
    workspace = adapter_manager.create_adapter_workspace(args.domain, version)

    # Handle data
    if args.data_file:
        train_file = args.data_file
        print(f"\n📚 Using training data: {train_file}")
    else:
        print(f"\n📝 Creating sample data...")
        train_file = create_sample_data(args.domain, workspace['train_file'])

    # Create sample or workspace-only?
    if args.create_sample or args.workspace_only:
        print(f"\n✅ Workspace ready at: {workspace['adapter_path']}")
        print(f"\n📝 Next steps:")
        print(f"   1. Add your training data to: {workspace['train_file']}")
        print(f"   2. Run: python scripts/quick_domain_trainer.py {args.domain} --data-file {workspace['train_file']}")
        return

    # Train
    print(f"\n🚀 Starting training...")
    print(f"   Domain: {args.domain}")
    print(f"   Version: {version}")
    print(f"   Epochs: {args.epochs}")

    from src.jarvis import JARVIS

    jarvis = JARVIS()
    adapter_name = jarvis.quick_train_new_domain(
        domain=args.domain,
        train_file=train_file,
        epochs=args.epochs,
        description=args.description or f"{args.domain} specialization v{version}"
    )

    print("\n" + "=" * 60)
    print("✅ Training Complete!")
    print("=" * 60)
    print(f"\n🎯 Adapter: {adapter_name}")
    print(f"\n💡 Usage:")
    print(f"   python jarvis_cli.py --adapter {adapter_name}")
    print(f"\n   Or in Python:")
    print(f"   >>> from src.jarvis import JARVIS")
    print(f"   >>> jarvis = JARVIS()")
    print(f"   >>> jarvis.load_adapter('{adapter_name}')")
    print(f"   >>> jarvis.interactive()")


if __name__ == "__main__":
    main()
