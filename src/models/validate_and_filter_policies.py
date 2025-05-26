# validate_and_filter_policies.py
# -----------------------------------------------------------------------------
# This script loads a list of ODRL policies with natural language descriptions,
# validates each policy against SHACL shapes, and saves only the valid ones.
# -----------------------------------------------------------------------------

import os
import json
import logging
from pyshacl import validate
from rdflib import Graph
from copy import deepcopy

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Configuration
INPUT_FILE = "outputs/generated_and_described.json"
OUTPUT_FILE = "outputs/valid_policies.json"
SHACL_PATH = "config/shacl_shapes.ttl"
ODRL_BASE = "http://www.w3.org/ns/odrl/2/"


def inject_context_and_flatten(policy):
    if "@context" not in policy:
        policy["@context"] = ODRL_BASE

    def flatten_constraints(rule):
        for c in rule.get("constraint", []):
            if isinstance(c.get("rightOperand"), dict):
                val = c["rightOperand"].get("@value")
                if val:
                    c["rightOperand"] = val
        return rule

    for section in ["permission", "prohibition", "obligation"]:
        for rule in policy.get(section, []):
            flatten_constraints(rule)

    return policy


def _expand_for_validation(policy):
    policy_copy = deepcopy(policy)
    policy_copy["@context"] = {
        "odrl": ODRL_BASE,
        "xsd": "http://www.w3.org/2001/XMLSchema#"
    }

    def expand(term):
        if isinstance(term, str) and not term.startswith("http") and ":" not in term:
            return "odrl:" + term
        return term

    def process_rule(rule):
        rule["action"] = expand(rule.get("action"))
        for c in rule.get("constraint", []):
            c["@type"] = "odrl:Constraint"
            c["leftOperand"] = expand(c.get("leftOperand"))
            c["operator"] = expand(c.get("operator"))
        return rule

    policy_copy["@type"] = expand(policy_copy.get("@type", "Policy"))
    for section in ["permission", "prohibition", "obligation"]:
        if section in policy_copy:
            policy_copy[section] = [process_rule(r) for r in policy_copy[section]]

    return policy_copy


def validate_policy(policy_json):
    expanded_policy = _expand_for_validation(policy_json)
    g = Graph()
    g.parse(data=json.dumps(expanded_policy), format='json-ld')

    conforms, report_graph, report_text = validate(
        data_graph=g,
        shacl_graph=SHACL_PATH,
        data_graph_format='json-ld',
        shacl_graph_format='turtle',
        inference='rdfs',
        debug=False
    )
    return conforms, report_text


# Main validation loop
def main():
    if not os.path.exists(SHACL_PATH):
        logging.error(f"SHACL file not found at {SHACL_PATH}")
        return

    if not os.path.exists(INPUT_FILE):
        logging.error(f"Input file not found at {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    valid_entries = []
    logging.info(f"Validating {len(data)} policies...")

    for i, entry in enumerate(data):
        logging.info(f"\n🔍 Policy {i + 1}...")
        try:
            policy = inject_context_and_flatten(entry["odrl"])
            conforms, report = validate_policy(policy)
            if conforms:
                valid_entries.append(entry)
                logging.info("✅ Valid")
            else:
                logging.warning("❌ Invalid")
                logging.debug(report)
        except Exception as e:
            logging.error(f"❌ Error validating policy {i+1}: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(valid_entries, f, indent=2)

    logging.info(f"\n🎉 Validation complete. {len(valid_entries)} valid policies saved to {OUTPUT_FILE}.")


if __name__ == "__main__":
    main()
