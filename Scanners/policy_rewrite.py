import json
import torch
from datetime import datetime
from Scanners.Complete_Scanner import CompleteCipherCloudScanner
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from peft import PeftModel, LoraConfig, TaskType

device = 0 if torch.cuda.is_available() else -1
print(f"⚡ Using device: {'GPU' if device >= 0 else 'CPU'}")

base_model_id = AutoModelForCausalLM.from_pretrained("facebook/opt-1.3b")
checkpoint_path = PeftModel.from_pretrained(base_model_id, "Yehia3A/secure-policy-rewriter")

print("Loading enhanced model...")
tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    torch_dtype=torch.float16,
    trust_remote_code=True
)
model = model.to(device)

lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    inference_mode=True
)

model = PeftModel.from_pretrained(model, checkpoint_path, config=lora_config)
model.eval()

llm = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=device,
    pad_token_id=tokenizer.eos_token_id
)

def rewrite_policy(policy_json: dict) -> str:
    """
    Rewrite risky IAM policies with a bracket-counter to extract the correct JSON output.
    """
    few_shot_example = """
Example 1:
Input: {
  "Version": "2012-10-17",
  "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]
}
Output: {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket", "s3:GetObject"],
      "Resource": "arn:aws:s3:::secure-bucket",
      "Condition": {"StringLike": {"aws:SourceVpce": "vpce-12345678"}}
    }
  ]
}

Example 2:
Input: {
  "Version": "2012-10-17",
  "Statement": [{"Effect": "Allow", "Action": "lambda:*", "Resource": "*"}]
}
Output: {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:secure-function",
      "Condition": {"StringEquals": {"aws:PrincipalOrgID": "o-1234567890"}}
    }
  ]
}
"""

    prompt = f"""Rewrite risky IAM policies to be secure. Replace wildcards with specific permissions and add conditions.

{few_shot_example}

Now rewrite this policy:

Input: {json.dumps(policy_json, indent=2)}

Output:"""

    result = llm(
        prompt,
        max_new_tokens=256,
        temperature=0.05,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )
    result_text = result[0]["generated_text"].strip()

    print("Raw LLM Output:", result_text)

    # Find the start of the final 'Output:' section
    output_start_index = result_text.rfind("Output:")
    if output_start_index == -1:
        return "{}"

    # Start searching for JSON from the end of the last "Output:"
    json_start_index = result_text.find("{", output_start_index)
    if json_start_index == -1:
        return "{}"
    
    bracket_counter = 0
    json_block = ""
    found_end = False

    # Iterate through the string from the first '{'
    for char in result_text[json_start_index:]:
        json_block += char
        if char == '{':
            bracket_counter += 1
        elif char == '}':
            bracket_counter -= 1
        
        # When the counter reaches 0, the first complete JSON object has been found
        if bracket_counter == 0:
            found_end = True
            break
            
    if found_end:
        try:
            parsed_json = json.loads(json_block)
            return json.dumps(parsed_json, indent=2)
        except json.JSONDecodeError:
            pass # Return {} on failure

    return "{}"

def main():
    print("🔍 Using mock scanner for LLM testing...")

    with open("/kaggle/working/CipherCloud-IAM-Policy-Risk-Analyzer/Scanners/example_policy.json") as f:
        policy = json.load(f)

    scan_result = {
        'policy_summary': 'Test policy with wildcards',
        'binary_result': {
            'is_risky': True,
            'risk_probability': 0.95,
            'benign_probability': 0.05,
            'confidence': 0.95
        },
        'scan_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if scan_result['binary_result']['is_risky']:
        print("🚨 Risky policy detected! Sending to LLM for rewrite...")
        rewritten_policy_str = rewrite_policy(policy)
        print("\n🔒 Rewritten Secure Policy:\n")
        print(rewritten_policy_str)

        # Check if the policy was actually changed from the original
        original_str = json.dumps(policy, sort_keys=True)
        rewritten_str = rewritten_policy_str if rewritten_policy_str != "{}" else "{}"

        if original_str == rewritten_str:
            print("⚠️ WARNING: Policy was not transformed! Model needs more training.")
        else:
            print("✅ SUCCESS: Policy was successfully rewritten!")

            print("\n-------------------------------------------------------------")
            print("Running the CompleteCipherCloudScanner on the rewritten policy...")

            try:
                rewritten_policy_dict = json.loads(rewritten_policy_str)
                scanner = CompleteCipherCloudScanner()
                final_scan_result = scanner.complete_scan(rewritten_policy_dict)
                scanner.display_results(final_scan_result)

            except json.JSONDecodeError:
                print("❌ ERROR: Could not parse the rewritten policy. Skipping scan.")

    else:
        print("✅ Policy is not risky. No rewrite needed.")

if __name__ == "__main__":
    main()
