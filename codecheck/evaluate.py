import json
import subprocess
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import re
# Load CodeBERT model and tokenizer (one-time load)
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")


def extract_function_name(user_code):
    """Extracts the function name from the user-defined code."""
    match = re.search(r"def\s+(\w+)\s*\(", user_code)
    return match.group(1) if match else None

def run_code(user_code, input_data):
    try:
        function_name = extract_function_name(user_code)
        if not function_name:
            return "Error: No function found"

        # Format script dynamically
        script = f"""
{user_code}
import sys, json
args = json.loads(sys.stdin.read())  # Read input as list
print(json.dumps({function_name}(*args)))  # Ensure JSON output
"""
        process = subprocess.run(
            ["python3", "-c", script],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            timeout=10
        )
        return process.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def evaluate_functional_correctness(user_code, test_cases):
    passed_cases = 0
    total_cases = len(test_cases)

    for case in test_cases:
        if not isinstance(case, dict) or "input" not in case or "expected_output" not in case:
            raise ValueError("Each test case should be a dictionary with 'input' and 'expected_output' keys.")

        input_data = case["input"]
        expected_output = case["expected_output"]

        user_output = run_code(user_code, input_data)

        try:
            user_output = json.loads(user_output)  # Ensure correct data type comparison
        except json.JSONDecodeError:
            pass  # Keep as a string if JSON decoding fails

        if user_output == expected_output:
            passed_cases += 1

    return round((passed_cases / total_cases) * 100, 2)
def get_code_embedding(code):
    inputs = tokenizer(code, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)  # Mean pooling to get fixed-size vector

def evaluate_codebert(usercode, correctcode):

    emb1 = get_code_embedding(usercode)
    emb2 = get_code_embedding(correctcode)
    similarity = F.cosine_similarity(emb1, emb2).item()
    similarity_percentage = round(similarity * 100, 2)
    return similarity_percentage