"""
Model loading and configuration for BabyClaude
"""

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    PeftModel
)
from typing import Optional, Dict, Any
import yaml


class BabyClaude:
    """Wrapper class for TinyLlama with LoRA fine-tuning capabilities"""

    def __init__(self, config_path: str = "config/model_config.yaml"):
        """
        Initialize BabyClaude model

        Args:
            config_path: Path to YAML configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.model = None
        self.tokenizer = None
        self.peft_config = None

    def load_base_model(self, quantize: bool = True):
        """
        Load the base TinyLlama model

        Args:
            quantize: Whether to use 4-bit quantization (saves VRAM)
        """
        model_name = self.config['model']['name']

        print(f"Loading base model: {model_name}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Quantization config for 4-bit training (QLoRA)
        if quantize:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )

            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.bfloat16,
                device_map="auto",
                trust_remote_code=True
            )

        print(f"Model loaded successfully!")
        self._print_trainable_parameters()

    def prepare_for_training(self):
        """Prepare model for LoRA fine-tuning"""
        if self.model is None:
            raise ValueError("Load base model first using load_base_model()")

        # Prepare model for k-bit training
        self.model = prepare_model_for_kbit_training(self.model)

        # Configure LoRA
        lora_config = self.config['lora']
        self.peft_config = LoraConfig(
            r=lora_config['r'],
            lora_alpha=lora_config['lora_alpha'],
            target_modules=lora_config['target_modules'],
            lora_dropout=lora_config['lora_dropout'],
            bias=lora_config['bias'],
            task_type=lora_config['task_type']
        )

        # Apply LoRA
        self.model = get_peft_model(self.model, self.peft_config)

        print("Model prepared for LoRA training!")
        self._print_trainable_parameters()

    def load_finetuned(self, adapter_path: str):
        """
        Load a fine-tuned LoRA adapter

        Args:
            adapter_path: Path to the saved LoRA adapter
        """
        if self.model is None:
            self.load_base_model(quantize=True)

        print(f"Loading fine-tuned adapter from: {adapter_path}")
        self.model = PeftModel.from_pretrained(self.model, adapter_path)
        print("Fine-tuned model loaded!")

    def _print_trainable_parameters(self):
        """Print the number of trainable parameters"""
        trainable_params = 0
        all_param = 0

        for _, param in self.model.named_parameters():
            all_param += param.numel()
            if param.requires_grad:
                trainable_params += param.numel()

        print(
            f"Trainable params: {trainable_params:,} || "
            f"All params: {all_param:,} || "
            f"Trainable%: {100 * trainable_params / all_param:.2f}%"
        )

    def generate(
        self,
        prompt: str,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Generate text from a prompt

        Args:
            prompt: Input text prompt
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self.model is None or self.tokenizer is None:
            raise ValueError("Model not loaded. Call load_base_model() or load_finetuned() first.")

        # Get generation config from YAML or use provided values
        gen_config = self.config['generation']
        max_new_tokens = max_new_tokens or gen_config.get('max_new_tokens', 256)
        temperature = temperature or gen_config.get('temperature', 0.7)

        # Format prompt with ChatML template for TinyLlama-Chat/Qwen
        formatted_prompt = f"<|user|>\n{prompt}</s>\n<|assistant|>\n"

        # Encode prompt
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        # Create stopping criteria to stop at EOS tokens
        from transformers import StoppingCriteria, StoppingCriteriaList

        class StopOnTokens(StoppingCriteria):
            def __init__(self, stop_token_ids):
                self.stop_token_ids = stop_token_ids

            def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
                for stop_id in self.stop_token_ids:
                    if input_ids[0][-1] == stop_id:
                        return True
                return False

        # Stop tokens: </s>, <|endoftext|>, <|user|>
        stop_token_ids = [self.tokenizer.eos_token_id]

        # Add additional stop tokens if they exist
        for stop_str in ["</s>", "<|endoftext|>", "<|user|>", "<|im_end|>"]:
            try:
                stop_id = self.tokenizer.encode(stop_str, add_special_tokens=False)[0]
                if stop_id not in stop_token_ids:
                    stop_token_ids.append(stop_id)
            except:
                pass

        stopping_criteria = StoppingCriteriaList([StopOnTokens(stop_token_ids)])

        # Generate with better parameters to reduce hallucination
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=kwargs.get('top_p', gen_config.get('top_p', 0.9)),
                top_k=kwargs.get('top_k', gen_config.get('top_k', 40)),
                repetition_penalty=kwargs.get('repetition_penalty', gen_config.get('repetition_penalty', 1.15)),
                do_sample=kwargs.get('do_sample', gen_config.get('do_sample', True)),
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                stopping_criteria=stopping_criteria,
            )

        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=False)

        # Extract only the assistant's response
        if "<|assistant|>" in generated_text:
            generated_text = generated_text.split("<|assistant|>")[-1]

        # Clean up - remove all stop tokens
        for stop_str in ["</s>", "<|endoftext|>", "<|user|>", "<|im_end|>"]:
            generated_text = generated_text.replace(stop_str, "")

        generated_text = generated_text.strip()

        # Remove the original prompt if it somehow leaked through
        if formatted_prompt in generated_text:
            generated_text = generated_text.replace(formatted_prompt, "").strip()

        return generated_text

    def get_memory_footprint(self) -> Dict[str, Any]:
        """Get model memory usage"""
        if self.model is None:
            return {"error": "Model not loaded"}

        return {
            "model_size_mb": self.model.get_memory_footprint() / 1024 / 1024,
            "device": str(self.model.device),
            "dtype": str(self.model.dtype)
        }
