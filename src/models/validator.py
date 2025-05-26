# odrl_validator.py
# ----------------------------------------------------------------------------
# Utility module for validating ODRL policies against SHACL shapes
# ----------------------------------------------------------------------------

import json
import os
from copy import deepcopy
from rdflib import Graph
from pyshacl import validate

ODRL_CONTEXT_URI = "http://www.w3.org/ns/odrl.jsonld"
ODRL_BASE = "http://www.w3.org/ns/odrl/2/"
SHACL_PATH = "config/shacl_shapes.ttl"  # ensure this file exists locally

# Ensures the context is present and constraints are flattened
def inject_context_and_flatten(policy):
    if "@context" not in policy:
        policy["@context"] = ODRL_CONTEXT_URI

    def flatten_constraints(rule):
        constraints = rule.get("constraint")
        if isinstance(constraints, dict):
            constraints = [constraints]
        for c in constraints or []:
            if isinstance(c.get("rightOperand"), dict):
                val = c["rightOperand"].get("@value")
                if val:
                    c["rightOperand"] = val
        rule["constraint"] = constraints
        return rule

    for section in ["permission", "prohibition", "obligation"]:
        for rule in policy.get(section, []):
            flatten_constraints(rule)

    return policy

# Prepares the policy with expanded URIs for SHACL validation
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
        constraints = rule.get("constraint")
        if isinstance(constraints, dict):
            constraints = [constraints]
        for c in constraints or []:
            c["@type"] = "odrl:Constraint"
            c["leftOperand"] = expand(c.get("leftOperand"))
            c["operator"] = expand(c.get("operator"))
        rule["constraint"] = constraints
        return rule

    policy_copy["@type"] = expand(policy_copy.get("@type", "Policy"))

    for section in ["permission", "prohibition", "obligation"]:
        if section in policy_copy:
            policy_copy[section] = [process_rule(r) for r in policy_copy[section]]

    return policy_copy

# Uses pySHACL to validate against the SHACL shapes
def validate_policy(policy_json):
    if not os.path.exists(SHACL_PATH):
        raise FileNotFoundError(f"SHACL file not found at {SHACL_PATH}")

    expanded_policy = _expand_for_validation(inject_context_and_flatten(policy_json))
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

    report_detailed = report_graph.serialize(format="turtle")
    return conforms, report_detailed
