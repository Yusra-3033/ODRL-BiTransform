# policy_validator.py
# ----------------------------------------------------------------------------
# Validates ODRL policies using JSON Schema and SHACL (optional).
# Cleans (JSON-LD <--> RDF), prepares, and evaluates input policies for conformance.
# ----------------------------------------------------------------------------

import json
import os
import jsonschema
from copy import deepcopy
from typing import Tuple, Dict, Any, Optional

# Optional RDF support
try:
    from rdflib import Graph
    from pyshacl import validate as shacl_validate
    RDF_AVAILABLE = True
except ImportError:
    RDF_AVAILABLE = False

# Constants for SHACL and context
SHACL_PATH = "config/shacl_shapes.ttl"
SCHEMA_PATH = "config/odrl_policy_schema.json"
CONTEXT_PATH = "config/odrl_context.json"

# ----------------------------------------------------------------------------
# Loaders and Preprocessors
# ----------------------------------------------------------------------------

def load_schema(path: str = SCHEMA_PATH) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load schema: {e}")

def load_context(path: str = CONTEXT_PATH) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            context_data = json.load(f)
            return context_data.get("@context", "http://www.w3.org/ns/odrl.jsonld")
    except FileNotFoundError:
        return "http://www.w3.org/ns/odrl.jsonld"

def inject_context(policy: Dict[str, Any]) -> Dict[str, Any]:
    if "@context" not in policy:
        policy["@context"] = load_context()
    return policy

def flatten_constraints(policy: Dict[str, Any]) -> Dict[str, Any]:
    for section in ["permission", "prohibition", "obligation"]:
        for rule in policy.get(section, []):
            for c in rule.get("constraint", []):
                if isinstance(c.get("rightOperand"), dict):
                    val = c["rightOperand"].get("@value")
                    if val:
                        c["rightOperand"] = val
    return policy

def prepare_for_validation(policy: Dict[str, Any]) -> Dict[str, Any]:
    policy = deepcopy(policy)
    policy = inject_context(policy)
    policy = flatten_constraints(policy)
    return policy

# ----------------------------------------------------------------------------
# Validation Engines
# ----------------------------------------------------------------------------

def validate_json_schema(policy: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
    if schema is None:
        schema = load_schema()
    try:
        jsonschema.validate(instance=policy, schema=schema)
        return True, None
    except jsonschema.exceptions.ValidationError as e:
        return False, f"[SCHEMA] UID: {policy.get('uid', 'unknown')} | Path: {'/'.join(map(str, e.absolute_path))} | {e.message}"
    except Exception as e:
        return False, f"[SCHEMA] Validation error: {str(e)}"

def validate_shacl(policy: Dict[str, Any], shapes_file: str = SHACL_PATH) -> Tuple[bool, str]:
    if not RDF_AVAILABLE:
        return True, "SHACL validation skipped - RDF libraries not available"
    if not os.path.exists(shapes_file):
        return True, "SHACL validation skipped - shapes file not found"

    try:
        expanded = deepcopy(policy)
        expanded["@context"] = {
            "odrl": "http://www.w3.org/ns/odrl/2/",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        }
        data_graph = Graph().parse(data=json.dumps(expanded), format='json-ld')
        shapes_graph = Graph().parse(shapes_file, format='turtle')
        conforms, _, results_text = shacl_validate(
            data_graph=data_graph,
            shacl_graph=shapes_graph,
            inference='rdfs',
            debug=False
        )
        return conforms, results_text
    except Exception as e:
        return False, f"SHACL validation error: {str(e)}"

# ----------------------------------------------------------------------------
# Comprehensive Validator
# ----------------------------------------------------------------------------

def validate_policy_comprehensive(policy: Dict[str, Any], enable_shacl: bool = True) -> Dict[str, Any]:
    results = {
        "valid": True,
        "errors": [],
        "json_schema_valid": False,
        "shacl_valid": not enable_shacl,
        "policy_uid": policy.get("uid", "unknown"),
        "policy_type": policy.get("@type", "unknown")
    }

    try:
        prepared = prepare_for_validation(policy)
    except Exception as e:
        results["valid"] = False
        results["errors"].append(f"Preparation error: {str(e)}")
        return results

    json_valid, json_error = validate_json_schema(prepared)
    results["json_schema_valid"] = json_valid
    if not json_valid:
        results["valid"] = False
        results["errors"].append(json_error)

    if enable_shacl:
        shacl_valid, shacl_result = validate_shacl(prepared)
        results["shacl_valid"] = shacl_valid
        if not shacl_valid and "skipped" not in shacl_result:
            results["valid"] = False
            results["errors"].append(f"[SHACL] {shacl_result}")

    return results

# ----------------------------------------------------------------------------
# Batch Template Validation
# ----------------------------------------------------------------------------

def validate_template_policies(file_path):
    with open(file_path, 'r') as f:
        policies = json.load(f)

    schema = load_schema()
    results = {
        "total_policies": len(policies),
        "valid_policies": 0,
        "json_schema_valid": 0,
        "shacl_valid": 0,
        "validation_results": [],
        "error_summary": {},
        "policy_types": {}
    }

    for policy_envelope in policies:
        policy = policy_envelope.get("odrl", policy_envelope)
        result = validate_policy_comprehensive(policy)
        results["validation_results"].append(result)

        if result["valid"]:
            results["valid_policies"] += 1
        if result["json_schema_valid"]:
            results["json_schema_valid"] += 1
        if result["shacl_valid"]:
            results["shacl_valid"] += 1

        policy_type = result["policy_type"]
        results["policy_types"][policy_type] = results["policy_types"].get(policy_type, 0) + 1

        for err in result["errors"]:
            etype = err.split("]")[0] + "]" if "]" in err else "OTHER"
            results["error_summary"][etype] = results["error_summary"].get(etype, 0) + 1

    return results
