import json
import concurrent.futures
from gradio_client import Client
import sys
import pathlib
repo_root = pathlib.Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from Scanners.Complete_Scanner import CompleteCipherCloudScanner

# Initialize Hugging Face client
client = Client("Yehia3A/secure-policy-rewriter-demo")  # add hf_token="XXX" if private

# Initialize scanner
scanner = CompleteCipherCloudScanner()

def secure_rewrite(risky_policy: dict, max_attempts: int = 3):
    """Rewrite risky policy until scanner confirms it's safe."""
    attempt = 0
    current_policy = risky_policy
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n🔄 Attempt {attempt} rewriting...")

        try:
            # Submit job to HF Space (async)
            job = client.submit(
                policy_str=json.dumps(current_policy, indent=2),
                api_name="/predict"
            )

            # Wait for result (increase timeout if needed)
            result = job.result(timeout=300)

        except concurrent.futures.CancelledError:
            print("❌ Request was cancelled (Space too slow or sleeping).")
            return current_policy
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return current_policy

        # Ensure model returned valid JSON
        try:
            rewritten_policy = json.loads(result)
        except json.JSONDecodeError:
            print("❌ Model did not return valid JSON, stopping.")
            return result

        # Scan rewritten policy
        scan = scanner.complete_scan(rewritten_policy)
        scanner.display_results(scan)

        if not scan["binary_result"]["is_risky"]:
            print("✅ Final policy is safe, returning to user")
            return rewritten_policy
        else:
            print("⚠️ Still risky, retrying...")
            current_policy = rewritten_policy  # feed back into model
    
    print("❌ Max attempts reached, returning last result (still risky).")
    return current_policy


if __name__ == "__main__":
    # Example risky policy
    risky_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ec2:TerminateInstances"
                    
                ],
                "Resource": "*"
            }
        ]
    }

    # Calling the secure_rewrite function
    safe_policy = secure_rewrite(risky_policy)

    # Output the final safe policy
    print("\n🔒 Secure Policy Output:\n", json.dumps(safe_policy, indent=2))
