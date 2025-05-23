# utils.py
# ----------------------------------------------------------------------------
# Utility functions for ID generation, config loading, random sampling, I/O,
# and logging. Used across the ODRL policy generation pipeline.
# ----------------------------------------------------------------------------

import random
import uuid
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List

# ----------------------------------------------------------------------------
# Reproducibility
# ----------------------------------------------------------------------------

def set_seed(seed: int) -> None:
    """Seed the random generator for reproducibility."""
    random.seed(seed)

# ----------------------------------------------------------------------------
# ID Generation
# ----------------------------------------------------------------------------

def generate_policy_id() -> str:
    """Generate a UUID-based policy identifier."""
    return str(uuid.uuid4())

# ----------------------------------------------------------------------------
# Config and File I/O
# ----------------------------------------------------------------------------

def load_config(config_path: str = "config/config.yml") -> Dict:
    """Load a YAML configuration file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_json(output_path: str, data: Any) -> None:
    """Save Python object as formatted JSON to the given path."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_num_policies(config: Dict) -> int:
    """Retrieve the number of policies to generate from config."""
    return config.get("num_policies", 50)

# ----------------------------------------------------------------------------
# Random Value Generators (with config)
# ----------------------------------------------------------------------------

def select_random(config: Dict, key: str) -> Any:
    """Select a random item from a specified config key list."""
    return random.choice(config["defaults"][key])

def get_random_policy_type(config: Dict) -> str:
    return select_random(config, "policy_types")

def get_random_party(config: Dict) -> str:
    return select_random(config, "example_party_uris")

def get_random_assigner(config: Dict) -> str:
    orgs = [p for p in config["defaults"]["example_party_uris"] if ":org:" in p or p.startswith("http://example.com/org:")]
    return random.choice(orgs)

def get_random_assignee(config: Dict) -> str:
    non_orgs = [p for p in config["defaults"]["example_party_uris"] if ":org:" not in p]
    return random.choice(non_orgs)

def get_random_asset(config: Dict) -> str:
    return select_random(config, "example_asset_uris")

def get_random_action(config: Dict) -> str:
    return select_random(config, "actions")

def get_random_operator(config: Dict) -> str:
    return select_random(config, "operators")

def get_random_operand(config: Dict) -> str:
    return select_random(config, "constraint_operands")

# ----------------------------------------------------------------------------
# File System & Logging Utilities
# ----------------------------------------------------------------------------

def mkdir_if_needed(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)

def log(message: str, verbose: bool = True) -> None:
    if verbose:
        print(message)

def get_actor_label(uri: str) -> str:
    """Extract a label from a URI for logging or dataset purposes."""
    if uri.startswith("http://example.com/"):
        label = uri.replace("http://example.com/", "").replace(":", "/")
        return label.split("/")[-1]
    return uri
