# prompt_builder.py
# ----------------------------------------------------------------------------
# Utility module for building prompts to guide LLMs in generating or
# explaining ODRL policies. Supports few-shot prompting using seed
# examples and configurable prompt construction.
# ----------------------------------------------------------------------------

import json
import random
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Load configuration paths from environment
ODRL_CONTEXT_URI = os.getenv("ODRL_CONTEXT_URI", "http://www.w3.org/ns/odrl.jsonld")
PROMPT_TEMPLATE_FILE = os.getenv("PROMPT_FILE", "prompts/odrl_generation_prompt.txt")
TEXT_PROMPT_TEMPLATE_FILE = os.getenv("TEXT_PROMPT_FILE", "prompts/description_generation_prompt.txt")

def load_prompt_template(file_path: str) -> str:
    """
    Load a prompt template from a file.

    Args:
        file_path (str): Path to the prompt template file.

    Returns:
        str: Contents of the file as a stripped string.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def build_policy_prompt(seeds: List[Dict], vocab: Dict, ontology: Dict, recommendations: str, num: int = 1) -> str:
    """
    Build a policy generation prompt for an LLM using few-shot seed examples.

    Args:
        seeds (List[Dict]): Seed ODRL policy examples.
        vocab (Dict): ODRL vocabulary.
        ontology (Dict): ODRL ontology definitions.
        recommendations (str): Human-readable guidance for ODRL structure.

    Returns:
        str: Constructed prompt.
    """
    template = load_prompt_template(PROMPT_TEMPLATE_FILE)
    seed_examples = "\n\n".join(json.dumps(seed.get("odrl", seed), indent=2) for seed in seeds)

    complexity = random.choice([
    "Keep it simple: one permission rule, no constraints.",
    "Add complexity: permission, prohibition, and duty, each with at least one constraint.",
    "Use multiple constraint types like dateTime, systemDevice, and purpose across rules.",
])



    return template.format(
        context_uri=ODRL_CONTEXT_URI,
        vocab=json.dumps(vocab),
        ontology=json.dumps(ontology),
        recommendations=recommendations,
        seed_examples=seed_examples,
        num=num,
        complexity=complexity
    )


def build_description_prompt(policy: Dict, style_examples: str = "") -> str:
    """
    Build a prompt asking the LLM to generate a natural language description
    for a given ODRL policy.

    Args:
        policy (Dict): The ODRL policy to describe.
        style_examples (str): Raw string of style examples.

    Returns:
        str: Constructed description prompt.
    """
    template = load_prompt_template(TEXT_PROMPT_TEMPLATE_FILE)

    return template.format(
        policy_json=json.dumps(policy, indent=2),
        style_examples=style_examples.strip() if style_examples else ""
    )