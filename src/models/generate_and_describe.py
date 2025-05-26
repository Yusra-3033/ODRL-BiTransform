# generate_and_describe.py
# ----------------------------------------------------------------------------
# Generate and describe ODRL policies using LLM + enhanced CLI support
# ----------------------------------------------------------------------------

import os
import json
import random
import logging
import argparse
import uuid
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import subprocess
from policy_generator import (
    get_llm_client, load_json, load_text, build_policy_prompt
)
from policy_describer import build_description_prompt
from prompt_tuner import tune_policy
from validator import validate_policy
import time

# Setup logging
Path("outputs/logs").mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("outputs/logs/generation.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

# Paths and config
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "outputs/llm_based_policies.json")
COMBINED_OUTPUT_PATH = os.getenv("COMBINED_OUTPUT_PATH", "outputs/generated_and_described.json")
AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "outputs/reports/generation_audit.json")
STYLE_EXAMPLES_PATH = os.getenv("STYLE_EXAMPLES_PATH", "data/description_examples.txt")
SEED_POLICIES_PATH = os.getenv("SEED_POLICIES_PATH", "data/w3c_examples.jsonld")
TEMPLATE_POLICIES_PATH = os.getenv("TEMPLATE_POLICIES_PATH", "outputs/policies/template_based_policies.json")
VOCAB_PATH = os.getenv("VOCAB_FILE", "config/config.yml")
ONTOLOGY_PATH = os.getenv("ONTOLOGY_FILE", "config/odrl_policy_schema.json")
RECOMMENDATIONS_PATH = os.getenv("RECOMMENDATIONS_FILE", "config/w3c_recommendations.txt")
NUM_POLICIES = int(os.getenv("NUM_POLICIES", 10))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 1))


def extract_json_objects(text):
    try:
        objects = []
        brace_stack = []
        start_idx = None

        for i, char in enumerate(text):
            if char == '{':
                if not brace_stack:
                    start_idx = i
                brace_stack.append(char)
            elif char == '}':
                if brace_stack:
                    brace_stack.pop()
                    if not brace_stack and start_idx is not None:
                        json_str = text[start_idx:i + 1]
                        try:
                            obj = json.loads(json_str)
                            objects.append(obj)
                        except json.JSONDecodeError:
                            continue
        return objects
    except Exception as e:
        raise ValueError(f"Failed to parse JSON objects: {e}")


#def describe_policy(client, policy, style_examples):
#    desc_prompt = build_description_prompt(policy, style_examples)
#    return client.generate(desc_prompt).strip()


def generate_policies(dry_run=False, uid_prefix="policy", describe=False):
    logging.info("=== Generating and Describing ODRL Policies ===")

    seeds_w3c = load_json(SEED_POLICIES_PATH) or []
    seeds_template = load_json(TEMPLATE_POLICIES_PATH) or []
    all_seeds = seeds_w3c + seeds_template

    if not all_seeds:
        logging.error("❌ No seed policies found. Aborting.")
        return

    # Pick one random seed
    few_shot = [random.choice(all_seeds)]


    #vocab = load_json(VOCAB_PATH)
    #ontology = load_json(ONTOLOGY_PATH)
    #recommendations = load_text(RECOMMENDATIONS_PATH)
    with open("config/preprocessed_data.json", "r", encoding="utf-8") as f:
        preprocessed = json.load(f)
    vocab = preprocessed["vocab"]
    ontology = preprocessed["ontology"]
    recommendations = preprocessed["recommendations"]

    #style_examples = load_text(STYLE_EXAMPLES_PATH)

    if not all([seeds_w3c, seeds_template, vocab, ontology]):
        logging.error("❌ Missing input files. Aborting.")
        return

    # Interleave seeds from W3C and template examples
    few_shot = []
    for w3c, tpl in zip(seeds_w3c, seeds_template):
        few_shot.append(w3c)
        few_shot.append(tpl)
    longer = seeds_w3c if len(seeds_w3c) > len(seeds_template) else seeds_template
    few_shot.extend(longer[len(few_shot)//2:])

    client = get_llm_client()
    results = []
    audit_log = []

    if dry_run:
        logging.info("🧪 Dry run mode: showing prompt and one result")
        prompt = build_policy_prompt(few_shot, vocab, ontology, recommendations, num=1)
        print("\n📘 Prompt:\n", prompt)
        response = client.generate(prompt)
        time.sleep(6)  # Wait to stay under TPM limits
        print("\n🧾 Response:\n", response)
        try:
            #policies = extract_json_objects(response)
            policies = extract_json_objects(response) or []
            if not policies:
                raise ValueError("No valid JSON object found in response.")
            policy = policies[0]

            print("\n✅ Parsed JSON:\n", json.dumps(policies[0], indent=2))
        except Exception as e:
            logging.error(f"❌ Failed to parse JSON: {e}")
        return

    # Suppose your estimate: each request ≈ 10,000 tokens
    max_prompts_per_minute = 3
    delay = 60 / max_prompts_per_minute  # = 20 seconds
    total_generated = 0
    while total_generated < NUM_POLICIES:
        batch_size = min(BATCH_SIZE, NUM_POLICIES - total_generated)
        logging.info(f"📦 Generating batch of {batch_size} policies...")
        prompt = build_policy_prompt(few_shot, vocab, ontology, recommendations, num=batch_size)
        #responses = [client.generate(prompt) for _ in range(batch_size)]
        responses = []
        for _ in range(batch_size):
            response = client.generate(prompt)
            responses.append(response)
            time.sleep(delay)  # <-- Wait to reduce risk of hitting TPM


        for i, raw in enumerate(responses):
            index = total_generated + i + 1
            audit_entry = {
                "policy_index": index,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "attempts": 0,
                "uid": None,
                "success": False,
                "violations": []
            }
            try:
                policies = extract_json_objects(raw)
                if not policies:
                    audit_entry["violations"].append("❌ No valid JSON object found in response.")
                    logging.error(f"❌ No valid JSON extracted from response:\n{raw}")
                    audit_log.append(audit_entry)
                    continue  # Skip to the next response

                policy = policies[0]
                policy["uid"] = f"http://example.com/{uid_prefix}:{uuid.uuid4().hex}"
                audit_entry["uid"] = policy["uid"]

                max_attempts = 3
                while audit_entry["attempts"] < max_attempts:
                    audit_entry["attempts"] += 1
                    conforms, report_text = validate_policy(policy)
                    if conforms:
                        audit_entry["success"] = True
                        break
                    else:
                        audit_entry["violations"].append(report_text)
                        logging.warning(f"⚠️ SHACL validation failed. Retrying attempt {audit_entry['attempts']}...")

                        correction_prompt = f"""
Below is an ODRL policy that failed structural validation against SHACL.
Please fix it. Ensure all required fields, valid constraints, and structure.

Original Policy:
{json.dumps(policy, indent=2)}

Return corrected JSON-LD only:
"""
                        retry_response = client.generate(correction_prompt)
                        retry_policies = extract_json_objects(retry_response)
                        policy = retry_policies[0] if retry_policies else policy
                        policy["uid"] = f"http://example.com/{uid_prefix}:{uuid.uuid4().hex}"
                        audit_entry["uid"] = policy["uid"]

                if not audit_entry["success"]:
                    logging.error("⛔ Final validation failed after 3 retries.")
                    audit_log.append(audit_entry)
                    continue

                policy = tune_policy(policy)
                description = ""
                #if describe:
                #    description = describe_policy(client, policy, style_examples)

                results.append({
                    "odrl": policy,
                    "text": description,
                    "metadata": {
                        "model": os.getenv("MODEL_NAME", "unknown"),
                        "seed_source": f"{SEED_POLICIES_PATH} + {TEMPLATE_POLICIES_PATH}",
                        "prompt_version": "v2.2",
                        "retries": audit_entry["attempts"]
                    }
                })
                logging.info(f"✅ Policy {index} generated.")
            except Exception as e:
                audit_entry["violations"].append(str(e))
                logging.error(f"❌ Error generating policy {index}: {e}")

            audit_log.append(audit_entry)

        total_generated += batch_size

    Path(os.path.dirname(COMBINED_OUTPUT_PATH)).mkdir(parents=True, exist_ok=True)
    with open(COMBINED_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(audit_log, f, indent=2)

    logging.info(f"\n🎉 Done! {len(results)} valid policies saved to {COMBINED_OUTPUT_PATH}")
    logging.info(f"📝 Audit log saved to {AUDIT_LOG_PATH}")

    subprocess.run(["python", "src/models/postprocess_policy.py"], check=True)
    subprocess.run(["python", "src/models/quality_report.py"], check=True)
    subprocess.run(["python", "src/models/diversity_summary.py"], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and describe ODRL policies.")
    parser.add_argument('--dry-run', action='store_true', help="Run prompt and print a single generation result.")
    parser.add_argument('--uid-prefix', type=str, default="policy", help="Custom prefix for generated policy UIDs")
    parser.add_argument('--no-describe', action='store_true', help="Skip natural language description generation")
    parser.add_argument('--clean-only', action='store_true', help="Only run postprocessing/cleanup.")
    parser.add_argument('--report-only', action='store_true', help="Only run reporting modules.")
    args = parser.parse_args()

    if args.clean_only:
        subprocess.run(["python", "src/models/postprocess_policy.py"], check=True)
        exit(0)
    if args.report_only:
        subprocess.run(["python", "src/models/quality_report.py"], check=True)
        subprocess.run(["python", "src/models/diversity_summary.py"], check=True)
        exit(0)

    generate_policies(dry_run=args.dry_run, uid_prefix=args.uid_prefix, describe=not args.no_describe)
