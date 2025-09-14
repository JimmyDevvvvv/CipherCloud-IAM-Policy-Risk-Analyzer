import json
import torch
import re
import sys
sys.path.append("/content/CipherCloud-IAM-Policy-Risk-Analyzer/Scanners")
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig
from peft import PeftModel, LoraConfig, TaskType
from Complete_Scanner import CompleteCipherCloudScanner

device = 0 if torch.cuda.is_available() else -1  # GPU if available, else CPU
print(f"⚡ Using device: {'GPU' if device >= 0 else 'CPU'}")

# Paths
base_model_id = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
checkpoint_path = "/content/results/checkpoint-750"  # Corrected checkpoint path from Colab

# Load tokenizer from the trained checkpoint
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    checkpoint_path,
    use_fast=False,
    trust_remote_code=True,
    local_files_only=True  # Ensure local loading
)

# Configure 8-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True
)

# Load base model with 8-bit quantization
print("Loading base model...")
model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    quantization_config=quantization_config,  # Use BitsAndBytesConfig
    device_map="auto",  # Automatically distribute across GPU/CPU
    trust_remote_code=True
)

# Resize token embeddings to match tokenizer
model.resize_token_embeddings(len(tokenizer))

# Configure LoRA with training settings (match original q_proj, v_proj)
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"],  # Align with training config
    inference_mode=True
)

# Load LoRA adapter
print("Applying LoRA adapter...")
model = PeftModel.from_pretrained(
    model,
    checkpoint_path,
    config=lora_config
)

# Set model to evaluation mode
model.eval()

# Create pipeline without explicit device argument
print("Creating inference pipeline...")
llm = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    dtype=torch.float32
)

def rewrite_policy(policy_json: dict) -> str:
    """
    Rewrite risky IAM policies using HuggingFace DeepSeek model with strict JSON output.
    """
    prompt = f"""Rewrite this risky IAM policy to be secure while preserving necessary permissions:    

Input:
{json.dumps(policy_json, indent=2)}

Output:"""

    result = llm(prompt, max_new_tokens=512, temperature=0.2)
    result_text = result[0].get("generated_text", "").strip()

    # --- JSON Safety Net with Debugging ---
    print("Raw LLM Output:", result_text)  # Debug the raw output
    try:
        # Try direct parse
        return json.dumps(json.loads(result_text), indent=2)
    except json.JSONDecodeError:
        # Try extracting first JSON block
        match = re.search(r"\{.*\}", result_text, re.DOTALL)
        if match:
            try:
                return json.dumps(json.loads(match.group(0)), indent=2)
            except Exception:
                return "{}"
        return "{}"
    
def main():
    scanner = CompleteCipherCloudScanner()

    # Example: Load a policy from file
    with open("Scanners/example_policy.json") as f:
        policy = json.load(f)

    # Step 1: Run binary + family scan
    scan_result = scanner.complete_scan(policy)

    # Step 2: Rewrite risky policies
    if scan_result['binary_result']['is_risky']:
        print("🚨 Risky policy detected! Sending to LLM for rewrite...")
        rewritten_policy = rewrite_policy(policy)
        print("\n🔒 Rewritten Secure Policy:\n")
        print(rewritten_policy)
    else:
        print("✅ Policy is not risky. No rewrite needed.")

if __name__ == "__main__":
    main()
