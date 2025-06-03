# evaluate_model.py
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu
import os

# Load fine-tuned model
model_path = "./odrl-codellama-lora"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", torch_dtype=torch.float16)

# Dataset sources
paths = [
    "outputs/cleaned_and_described_gpt.json",
    "outputs/cleaned_and_described_llama.json",
    "outputs/policies/template_based_policies.json"
]

scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)

def generate_description(prompt):
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)
    with torch.no_grad():
        outputs = model.generate(input_ids, max_new_tokens=256, do_sample=False)
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if prompt in decoded:
            return decoded.split(prompt)[-1].strip()
        return decoded.strip()

for path in paths:
    if not os.path.exists(path):
        continue

    with open(path, "r") as f:
        entries = json.load(f)

    for entry in entries:
        odrl = entry.get("odrl")
        reference = entry.get("text", "").strip()
        if not odrl or not reference:
            continue

        prompt = f"Describe the following ODRL policy:\n{json.dumps(odrl, indent=2)}"
        generated = generate_description(prompt)

        rouge = scorer.score(reference, generated)
        bleu = sentence_bleu([reference.split()], generated.split())

        print("\n====================")
        print(f"PROMPT:\n{prompt[:200]}...")
        print(f"REFERENCE: {reference}")
        print(f"GENERATED: {generated}")
        print(f"BLEU: {bleu:.2f}, ROUGE-L: {rouge['rougeL'].fmeasure:.2f}")
