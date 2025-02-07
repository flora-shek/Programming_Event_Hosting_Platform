import json
import timeit
import subprocess
import torch
from django.shortcuts import render
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Load CodeBERT model and tokenizer (one-time load)
tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModelForSequenceClassification.from_pretrained("microsoft/codebert-base")



def run_code(user_code, input_data):
   
    try:
        process = subprocess.run(
            ["python3", "-c", user_code], input=input_data.encode(),
            capture_output=True, text=True, timeout=5
        )
        return process.stdout.strip()  # Get only output
    except Exception as e:
        return f"Error: {str(e)}"

def evaluate_functional_correctness(user_code, test_cases):
  
    passed_cases = 0
    total_cases = len(test_cases)
    
    for case in test_cases:
            if not isinstance(case, dict) or "input" not in case or "expected_output" not in case:
                raise ValueError("Each test case should be a dictionary with 'input' and 'expected_output' keys.")

            # Convert nested input dictionary to JSON string
            input_data = json.dumps(case["input"])
            expected_output = json.dumps(case["expected_output"])  # Normalize output format

            user_output = run_code(user_code, input_data)

            try:
                # Normalize user output for better comparison
                user_output = json.loads(user_output)
            except json.JSONDecodeError:
                user_output = user_output.strip()

            if user_output == json.loads(expected_output):  # Convert expected output to list if needed
                passed_cases += 1

    return round((passed_cases / total_cases) * 100, 2)  # Return percentage

 

def evaluate_codebert(user_code, correct_code, model, tokenizer):
    try:
        inputs = tokenizer(user_code, correct_code, return_tensors="pt", padding=True, truncation=True)
        outputs = model(**inputs)

        # Extract similarity score
        logits = outputs.logits

        if logits.numel() > 1:
            similarity_score = torch.softmax(logits, dim=-1)[0][1].item()  # Get probability of similarity
        else:
            similarity_score = logits.item()  # Extract scalar value

        return round(similarity_score * 100, 2)  # Convert to percentage
    except Exception as e:
        return f"Error in CodeBERT evaluation: {str(e)}"