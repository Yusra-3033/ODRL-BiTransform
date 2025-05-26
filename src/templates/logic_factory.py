# logic_factory.py
# ----------------------------------------------------------------------------
# Core logic for semantically aware constraint generation in ODRL policies.
# Handles compatibility between asset types, operands, data types, and operators.
# ----------------------------------------------------------------------------

import random
from utils import get_random_operand, get_random_operator, get_random_asset
from value_factory import generate_right_operand

# ----------------------------------------------------------------------------
# Semantic Definitions
# ----------------------------------------------------------------------------

# Valid operators per inferred data type
SEMANTIC_OPERATORS = {
    "string": ["eq", "neq", "isA", "isAnyOf", "isNoneOf"],
    "number": ["eq", "neq", "gt", "lt", "gteq", "lteq"],
    "uri": ["isA", "hasPart", "isPartOf", "eq", "neq"],
    "boolean": ["eq", "neq"],
    "datetime": ["eq", "neq", "gt", "lt", "gteq", "lteq", "isA", "isAnyOf", "isNoneOf"]
}

# Asset type to compatible operands mapping
ASSET_COMPATIBLE_OPERANDS = {
    "photo": ["resolution", "fileFormat", "spatial", "dateTime", "percentage", "count", "absoluteSpatialPosition"],
    "image": ["resolution", "fileFormat", "spatial", "dateTime", "percentage", "count", "virtualLocation", "absolutePosition", "version", "relativeSpatialPosition"],
    "video": ["resolution", "fileFormat", "deliveryChannel", "elapsedTime", "timeInterval", "dateTime", "absolutePosition", "recipient"],
    "movie": ["resolution", "fileFormat", "deliveryChannel", "elapsedTime", "timeInterval", "dateTime", "unitOfCount", "absoluteSpatialPosition", "metering", "count", "relativePosition", "delayPeriod"],
    "music": ["fileFormat", "deliveryChannel", "elapsedTime", "language", "media", "absolutePosition", "recipient", "version"],
    "document": ["fileFormat", "language", "percentage", "count", "delayPeriod", "elapsedTime", "absoluteSpatialPosition"],
    "text": ["language", "percentage", "count", "fileFormat"],
    "data": ["percentage", "count", "absoluteSpatialPosition", "purpose"],
    "asset": ["dateTime", "elapsedTime", "percentage", "timeInterval", "absolutePosition", "version", "metering"]
}

# ----------------------------------------------------------------------------
# Operand Extraction and Type Inference
# ----------------------------------------------------------------------------

def extract_asset_type_from_constraint_context(target_asset):
    """Extract asset type for constraint generation."""
    if not target_asset:
        return "asset"

    target_asset_lower = target_asset.lower()
    if "photo" in target_asset_lower:
        return "photo"
    elif "image" in target_asset_lower or "img" in target_asset_lower:
        return "image"
    elif "video" in target_asset_lower or "clip" in target_asset_lower:
        return "video"
    elif "movie" in target_asset_lower:
        return "movie"
    elif "music" in target_asset_lower or "track" in target_asset_lower:
        return "music"
    elif "document" in target_asset_lower:
        return "document"
    elif "text" in target_asset_lower or "article" in target_asset_lower:
        return "text"
    elif "data" in target_asset_lower or "dataset" in target_asset_lower:
        return "data"
    return "asset"

def get_compatible_operand(target_asset, config):
    """Get semantically compatible operand for asset type."""
    asset_type = extract_asset_type_from_constraint_context(target_asset)
    compatible_operands = ASSET_COMPATIBLE_OPERANDS.get(asset_type, config["defaults"]["constraint_operands"])

    if not compatible_operands:
        compatible_operands = config["defaults"]["constraint_operands"]

    return random.choice(compatible_operands)

def infer_operand_type(operand):
    """Infer the data type of an operand for semantic operator selection."""
    string_like = ["language", "media", "purpose", "deliveryChannel", "systemDevice", "event", "fileFormat"]
    numeric_like = ["percentage", "count", "payAmount", "elapsedTime", "unitOfCount", "delayPeriod"]
    uri_like = ["recipient", "product", "industry", "virtualLocation", "absolutePosition", "relativePosition", 
                "absoluteSpatialPosition", "relativeSpatialPosition", "relativeTemporalPosition", "absoluteTemporalPosition"]
    datetime_like = ["dateTime", "timeInterval", "absoluteTemporalPosition"]
    boolean_like = ["metering"]

    if operand in string_like:
        return "string"
    elif operand in numeric_like:
        return "number"
    elif operand in uri_like:
        return "uri"
    elif operand in datetime_like:
        return "datetime"
    elif operand in boolean_like:
        return "boolean"
    return "string"

# ----------------------------------------------------------------------------
# Constraint Generators
# ----------------------------------------------------------------------------

def random_constraint(config, target_asset=None):
    """Generate a semantically coherent constraint."""
    for attempt in range(10):
        try:
            operand = get_compatible_operand(target_asset, config)
            if not operand:
                continue

            inferred_type = infer_operand_type(operand)
            allowed_ops = SEMANTIC_OPERATORS.get(inferred_type, ["eq"])

            operator = get_random_operator(config)
            if operator not in allowed_ops:
                operator = random.choice(allowed_ops)

            right = generate_right_operand(operand)

            if operand and operator and right is not None:
                return {
                    "@type": "Constraint",
                    "leftOperand": operand,
                    "operator": operator,
                    "rightOperand": right
                }
        except Exception:
            continue

    return {
        "@type": "Constraint",
        "leftOperand": "dateTime",
        "operator": "eq",
        "rightOperand": generate_right_operand("dateTime")
    }

def random_logical_constraint(config, target_asset=None):
    """Generate XOR constraint with semantic awareness."""
    constraint1 = random_constraint(config, target_asset)
    constraint2 = random_constraint(config, target_asset)
    if constraint1 and constraint2:
        return {"xone": {"@list": [constraint1, constraint2]}}
    return random_constraint(config, target_asset)

def random_or_constraint(config, target_asset=None):
    """Generate OR constraint with semantic awareness."""
    constraint1 = random_constraint(config, target_asset)
    constraint2 = random_constraint(config, target_asset)
    if constraint1 and constraint2:
        return {"or": {"@list": [constraint1, constraint2]}}
    return random_constraint(config, target_asset)

def random_and_constraint(config, target_asset=None):
    """Generate AND constraint with semantic awareness."""
    constraint1 = random_constraint(config, target_asset)
    constraint2 = random_constraint(config, target_asset)
    if constraint1 and constraint2:
        return {"and": {"@list": [constraint1, constraint2]}}
    return random_constraint(config, target_asset)

# ----------------------------------------------------------------------------
# Duty and Remedy Generators
# ----------------------------------------------------------------------------

def random_duty(config, action, target_asset=None):
    """Generate a duty with semantic constraints."""
    constraint = random_constraint(config, target_asset)
    if not constraint:
        return None

    return {
        "action": action,
        "target": target_asset or get_random_asset(config),
        "constraint": [constraint],
        "@type": "Duty"
    }

def random_remedy(config):
    """Generate a remedy action."""
    return {
        "action": "anonymize",
        "target": get_random_asset(config),
        "@type": "Remedy"
    }
