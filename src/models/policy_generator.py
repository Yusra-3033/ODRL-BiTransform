# policy_generator.py
# ----------------------------------------------------------------------------
# Module for generating synthetic ODRL policies using an LLM
# ----------------------------------------------------------------------------

import os
import json
import uuid
import random
import yaml
from pathlib import Path
from dotenv import load_dotenv

from prompt_builder import build_policy_prompt
from ollama_client import OllamaClient
from openai_client import OpenAIClient

load_dotenv()

NUM_POLICIES = int(os.getenv("NUM_POLICIES", 10))
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "outputs/llm_based_policies.json")
SEED_POLICIES_PATH = os.getenv("SEED_POLICIES_PATH", "data/w3c_examples.jsonld")
VOCAB_PATH = os.getenv("VOCAB_FILE", "config/config.yml")
ONTOLOGY_PATH = os.getenv("ONTOLOGY_FILE", "config/odrl_policy_schema.json")
RECOMMENDATIONS_PATH = os.getenv("RECOMMENDATIONS_FILE", "config/w3c_recommendations.txt")

def load_json(path):
    if path.endswith(".yml") or path.endswith(".yaml"):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def get_llm_client():
#    return OllamaClient()
     return OpenAIClient()
#     # Uncomment the line below to use OpenAI instead of Ollama

def generate_policies():
    Path(os.path.dirname(OUTPUT_PATH)).mkdir(parents=True, exist_ok=True)
    seeds = load_json(SEED_POLICIES_PATH)

    #vocab = load_json(VOCAB_PATH)
    #ontology = load_json(ONTOLOGY_PATH)
    #recommendations = load_text(RECOMMENDATIONS_PATH)
    with open("config/preprocessed_data.json", "r", encoding="utf-8") as f:
        preprocessed = json.load(f)
    vocab = preprocessed["vocab"]
    ontology = preprocessed["ontology"]
    recommendations = preprocessed["recommendations"]

    client = get_llm_client()
    policies = []

    for i in range(NUM_POLICIES):
        print(f"\n🚧 Generating policy {i + 1} of {NUM_POLICIES}...")
        few_shot = random.sample(seeds, k=min(2, len(seeds)))
        prompt = build_policy_prompt(few_shot, vocab, ontology, recommendations)

        try:
            policy_str = client.generate(prompt)
            policy = json.loads(policy_str)
            policy_id = f"http://example.com/policy:{uuid.uuid4().hex}"
            policy["uid"] = policy_id
            policies.append({"id": policy_id, "odrl": policy})
            print(f"✅ Policy {i+1} generated.")
        except Exception as e:
            print(f"❌ Failed to generate policy {i+1}: {e}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(policies, f, indent=2)

    print(f"\n✅ Done! {len(policies)} policies saved to {OUTPUT_PATH}")
    return policies

if __name__ == "__main__":
    generate_policies()
