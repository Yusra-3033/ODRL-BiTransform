# policy_describer.py
# ----------------------------------------------------------------------------
# Improved version of the policy describer to support clean, diverse, and
# well-logged description generation from ODRL policies.
# ----------------------------------------------------------------------------

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

from prompt_builder import build_description_prompt
from ollama_client import OllamaClient
from openai_client import OpenAIClient  # Uncomment if using OpenAI instead of Ollama

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')

# Configuration
DESCRIPTION_OUTPUT_PATH = os.getenv("DESCRIPTION_OUTPUT_PATH", "outputs/llm_policy_descriptions.json")
POLICIES_TO_DESCRIBE_PATH = os.getenv("POLICIES_TO_DESCRIBE_PATH", "outputs/llm_based_policies.json")
STYLE_EXAMPLES_PATH = os.getenv("STYLE_EXAMPLES_PATH", "data/description_examples.txt")  # Optional

def load_json(path):
    if not os.path.exists(path):
        logging.error(f"File not found: {path}")
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load JSON from {path}: {e}")
        return []

def load_text(path):
    if not os.path.exists(path):
        logging.warning(f"Text file not found: {path}")
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        logging.error(f"Failed to load text from {path}: {e}")
        return ""

def get_llm_client():
#    return OllamaClient()
    return OpenAIClient()
#     # Uncomment the line above to use OpenAI instead of Ollama

def describe_policies():
    Path(os.path.dirname(DESCRIPTION_OUTPUT_PATH)).mkdir(parents=True, exist_ok=True)

    policies = load_json(POLICIES_TO_DESCRIBE_PATH)
    style_examples = load_text(STYLE_EXAMPLES_PATH)

    client = get_llm_client()
    descriptions = []

    logging.info(f"Describing {len(policies)} policies...")

    for i, entry in enumerate(policies):
        policy = entry["odrl"]
        logging.info(f"\n📘 Describing policy {i + 1}...")

        try:
            prompt = build_description_prompt(policy, style_examples)
            description = client.generate(prompt).strip()

            entry["description"] = description
            descriptions.append(entry)

            logging.info("✅ Description completed")
        except Exception as e:
            logging.error(f"❌ Failed to describe policy {i+1}: {e}")
            entry["description"] = f"Error: {str(e)}"
            descriptions.append(entry)

    with open(DESCRIPTION_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(descriptions, f, indent=2, ensure_ascii=False)

    logging.info(f"Descriptions saved to {DESCRIPTION_OUTPUT_PATH}")

if __name__ == "__main__":
    describe_policies()
