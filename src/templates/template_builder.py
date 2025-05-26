# template_builder.py
# ----------------------------------------------------------------------------
# Generates ODRL policy templates using configuration-based logic.
# Supports semantically compatible constraints and action-asset alignment.
# ----------------------------------------------------------------------------

import random
import uuid
from typing import Any, Dict, List, Optional, Union
from utils import generate_policy_id
from logic_factory import (
    random_constraint,
    random_and_constraint,
    random_or_constraint,
    random_logical_constraint,
)

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

# Context definition for JSON-LD compliance with ODRL 2.2
# This ensures the generated JSON is semantically valid and machine-readable in RDF ecosystems.
ODRL_CONTEXT = "http://www.w3.org/ns/odrl.jsonld"

# Probability distribution for generating different types of constraints
# These values help control the mix of simple vs. compound logical constraints (AND, OR, XOR)
# to introduce diversity and complexity into the synthetic policies.
COMPLEX_CONSTRAINT_PROBABILITIES = {
    "and": 0.15,
    "or": 0.15,
    "xone": 0.15,
    "simple": 0.55
}

# Defines which actions are semantically compatible with different asset types
# This helps generate realistic and logically sound permissions, prohibitions, and obligations.
ASSET_ACTION_COMPATIBILITY = {
    "photo": ["display", "print", "modify", "share", "watermark", "read", "attribute", "index"],
    "image": ["display", "print", "modify", "share", "watermark", "read", "attribute", "index", "archive", "digitize", "present", "secondaryUse"],
    "video": ["play", "stream", "download", "edit", "move", "execute", "aggregate", "anonymize", "install", "present"],
    "movie": ["play", "stream", "download", "edit", "move", "execute", "aggregate", "anonymize", "install", "present", "lease", "pay", "include"],
    "music": ["play", "download", "distribute", "execute", "delete", "move", "textToSpeech"],
    "document": ["read", "print", "copy", "modify", "extract", "uninstall", "install", "attribute", "anonymize"],
    "text": ["read", "print", "copy", "modify", "extract", "inform", "anonymize", "digitize"],
    "asset": ["use", "lease", "pay", "give", "transfer", "sell", "include", "compensate", "read", "modify"],
    "data": ["use", "secondaryUse", "attribute", "distribute", "watermark"]
}

# ----------------------------------------------------------------------------
# Utility Functions
# ----------------------------------------------------------------------------

def extract_asset_type(asset_uri):
    asset_uri_lower = asset_uri.lower()
    if "photo" in asset_uri_lower:
        return "photo"
    elif "image" in asset_uri_lower or "img" in asset_uri_lower:
        return "image"
    elif "video" in asset_uri_lower or "clip" in asset_uri_lower:
        return "video"
    elif "movie" in asset_uri_lower:
        return "movie"
    elif "music" in asset_uri_lower or "track" in asset_uri_lower:
        return "music"
    elif "document" in asset_uri_lower:
        return "document"
    elif "text" in asset_uri_lower or "article" in asset_uri_lower:
        return "text"
    elif "data" in asset_uri_lower or "dataset" in asset_uri_lower:
        return "data"
    return "asset"

def get_compatible_action(asset_uri, config):
    asset_type = extract_asset_type(asset_uri)
    return random.choice(ASSET_ACTION_COMPATIBILITY.get(asset_type, config["defaults"]["actions"]))

def generate_uid():
    return f"http://example.com/policy/{generate_policy_id()}"

def generate_party(config):
    return random.choice(config["defaults"]["example_party_uris"])

def generate_asset(config):
    return random.choice(config["defaults"]["example_asset_uris"])

def maybe_complex_constraint(config, target_asset=None):
    choice = random.random()
    cumulative = 0.0
    for kind, prob in COMPLEX_CONSTRAINT_PROBABILITIES.items():
        cumulative += prob
        if choice < cumulative:
            if kind == "and":
                return [random_and_constraint(config, target_asset)]
            elif kind == "or":
                return [random_or_constraint(config, target_asset)]
            elif kind == "xone":
                return [random_logical_constraint(config, target_asset)]
            else:
                return [c for _ in range(random.randint(0, 2)) if (c := random_constraint(config, target_asset))]
    return [c for _ in range(random.randint(0, 2)) if (c := random_constraint(config, target_asset))]

# ----------------------------------------------------------------------------
# Policy Component Generators
# ----------------------------------------------------------------------------

def generate_permission(config, assigner=None, assignee=None):
    target = generate_asset(config)
    constraint_list = maybe_complex_constraint(config, target)
    permission = {
        "@type": "Permission",
        "target": target,
        "action": get_compatible_action(target, config),
        "assigner": assigner or generate_party(config)
    }
    if assignee:
        permission["assignee"] = assignee
    if constraint_list:
        permission["constraint"] = constraint_list
    return permission

def generate_prohibition(config, assigner=None, assignee=None):
    target = generate_asset(config)
    constraint_list = maybe_complex_constraint(config, target)
    prohibition = {
        "@type": "Prohibition",
        "target": target,
        "action": get_compatible_action(target, config),
        "assigner": assigner or generate_party(config)
    }
    if assignee:
        prohibition["assignee"] = assignee
    if constraint_list:
        prohibition["constraint"] = constraint_list
    return prohibition

def generate_obligation(config, assigner, assignee):
    target = generate_asset(config)
    constraint_list = maybe_complex_constraint(config, target)
    obligation = {
        "@type": "Duty",
        "target": target,
        "action": get_compatible_action(target, config),
        "assigner": assigner or generate_party(config),
        "assignee": assignee or generate_party(config)
    }
    if constraint_list:
        obligation["constraint"] = constraint_list
    return obligation

# ----------------------------------------------------------------------------
# Main Template Generator
# ----------------------------------------------------------------------------

def template_json_variant(policy_id, config):
    policy_type = random.choice(config["defaults"]["policy_types"])
    assigner = assignee = None

    if policy_type == "Agreement":
        assigner = generate_party(config)
        assignee = generate_party(config)
    elif policy_type == "Offer":
        assigner = generate_party(config)
    elif policy_type in ["Set", "Policy"]:
        if random.random() < 0.5:
            assigner = generate_party(config)
        if random.random() < 0.5:
            assignee = generate_party(config)

    policy = {
        "@context": ODRL_CONTEXT,
        "@type": policy_type,
        "uid": generate_uid()
    }

    if random.random() < 0.9:
        policy["permission"] = [generate_permission(config, assigner, assignee)]
    if random.random() < 0.5:
        policy["prohibition"] = [generate_prohibition(config, assigner, assignee)]
    if assigner and assignee and random.random() < 0.5:
        policy["obligation"] = [generate_obligation(config, assigner, assignee)]
    if not any(k in policy for k in ["permission", "prohibition", "obligation"]):
        policy["permission"] = [generate_permission(config, assigner, assignee)]

    return policy
