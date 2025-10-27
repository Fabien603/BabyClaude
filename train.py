"""
Training script for BabyClaude fine-tuning
"""

import os
import argparse
import yaml
from pathlib import Path

import torch
from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling
from src.model import BabyClaude
from src.data import DatasetLoader


def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune BabyClaude")
    parser.add_argument(
        "--config",
        type=str,
        default="config/model_config.yaml",
        help="Path to config file"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="HuggingFace dataset name (e.g., 'databricks/databricks-dolly-15k')"
    )
    parser.add_argument(
        "--train-file",
        type=str,
        default=None,
        help="Path to training JSONL file"
    )
    parser.add_argument(
        "--eval-file",
        type=str,
        default=None,
        help="Path to evaluation JSONL file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./checkpoints",
        help="Output directory for checkpoints"
    )
    parser.add_argument(
        "--use-sample",
        action="store_true",
        help="Use sample dataset for testing"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        help="Number of training epochs (overrides config)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size per device (overrides config)"
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=None,
        help="Learning rate (overrides config)"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 50)
    print("🚀 BabyClaude Training Pipeline")
    print("=" * 50)

    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    # Initialize model
    print("\n📦 Loading model...")
    baby_claude = BabyClaude(config_path=args.config)
    baby_claude.load_base_model(quantize=True)
    baby_claude.prepare_for_training()

    # Initialize data loader
    print("\n📚 Loading dataset...")
    data_loader = DatasetLoader(
        tokenizer=baby_claude.tokenizer,
        max_seq_length=config['data']['max_seq_length']
    )

    # Load dataset
    if args.use_sample:
        print("Creating sample dataset for testing...")
        train_file = DatasetLoader.create_sample_dataset()
        datasets = data_loader.load_instruction_dataset(train_file=train_file)
    elif args.dataset:
        datasets = data_loader.load_instruction_dataset(dataset_name=args.dataset)
    elif args.train_file:
        datasets = data_loader.load_instruction_dataset(
            train_file=args.train_file,
            eval_file=args.eval_file
        )
    else:
        print("\n❌ No dataset specified!")
        print("\nRecommended datasets:")
        for ds in DatasetLoader.get_recommended_datasets():
            print(f"  • {ds['name']}: {ds['description']} ({ds['lang']}, {ds['domain']})")
        print("\nUse --dataset <name> or --train-file <path> or --use-sample for testing")
        return

    print(f"✓ Train examples: {len(datasets['train'])}")
    print(f"✓ Eval examples: {len(datasets['eval'])}")

    # Tokenize datasets
    print("\n🔤 Tokenizing...")
    tokenized_train = datasets['train'].map(
        data_loader.tokenize_function,
        batched=True,
        remove_columns=datasets['train'].column_names,
        desc="Tokenizing training data"
    )
    tokenized_eval = datasets['eval'].map(
        data_loader.tokenize_function,
        batched=True,
        remove_columns=datasets['eval'].column_names,
        desc="Tokenizing evaluation data"
    )

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=baby_claude.tokenizer,
        mlm=False  # Causal LM, not masked LM
    )

    # Training arguments
    train_config = config['training']

    # Override with command line args if provided
    if args.epochs:
        train_config['num_train_epochs'] = args.epochs
    if args.batch_size:
        train_config['per_device_train_batch_size'] = args.batch_size
        train_config['per_device_eval_batch_size'] = args.batch_size
    if args.learning_rate:
        train_config['learning_rate'] = args.learning_rate
    if args.output_dir:
        train_config['output_dir'] = args.output_dir

    training_args = TrainingArguments(
        output_dir=train_config['output_dir'],
        num_train_epochs=train_config['num_train_epochs'],
        per_device_train_batch_size=train_config['per_device_train_batch_size'],
        per_device_eval_batch_size=train_config['per_device_eval_batch_size'],
        gradient_accumulation_steps=train_config['gradient_accumulation_steps'],
        learning_rate=train_config['learning_rate'],
        weight_decay=train_config['weight_decay'],
        warmup_steps=train_config['warmup_steps'],
        logging_steps=train_config['logging_steps'],
        save_steps=train_config['save_steps'],
        eval_steps=train_config['eval_steps'],
        save_total_limit=train_config['save_total_limit'],
        fp16=train_config['fp16'],
        bf16=train_config['bf16'],
        optim=train_config['optim'],
        gradient_checkpointing=train_config['gradient_checkpointing'],
        max_grad_norm=train_config['max_grad_norm'],
        eval_strategy="steps",  # Renamed from evaluation_strategy in newer transformers
        save_strategy="steps",
        load_best_model_at_end=True,
        report_to=["tensorboard"],
        logging_dir=f"{train_config['output_dir']}/logs",
    )

    # Initialize trainer
    print("\n🏋️ Initializing trainer...")
    trainer = Trainer(
        model=baby_claude.model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        data_collator=data_collator,
    )

    # Print memory info
    print("\n💾 Memory footprint:")
    mem_info = baby_claude.get_memory_footprint()
    print(f"  • Model size: {mem_info['model_size_mb']:.2f} MB")
    print(f"  • Device: {mem_info['device']}")
    print(f"  • Dtype: {mem_info['dtype']}")

    # Start training
    print("\n🎯 Starting training...")
    print(f"  • Epochs: {train_config['num_train_epochs']}")
    print(f"  • Batch size: {train_config['per_device_train_batch_size']}")
    print(f"  • Gradient accumulation: {train_config['gradient_accumulation_steps']}")
    print(f"  • Effective batch size: {train_config['per_device_train_batch_size'] * train_config['gradient_accumulation_steps']}")
    print(f"  • Learning rate: {train_config['learning_rate']}")
    print(f"  • Output: {train_config['output_dir']}")
    print()

    trainer.train()

    # Save final model
    print("\n💾 Saving final model...")
    final_path = Path(train_config['output_dir']) / "final_model"
    trainer.model.save_pretrained(final_path)
    baby_claude.tokenizer.save_pretrained(final_path)

    print(f"\n✅ Training complete! Model saved to: {final_path}")
    print("\n📊 To view training metrics:")
    print(f"   tensorboard --logdir {train_config['output_dir']}/logs")


if __name__ == "__main__":
    main()
