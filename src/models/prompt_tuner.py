# prompt_tuner.py
# -----------------------------------------------------------------------------
# Optional tuner to add variation and enrich generated ODRL policies
# -----------------------------------------------------------------------------

import random

def tune_policy(policy):
    """Apply minor variations to promote diversity in generated policies."""
    def maybe_add_constraint(rule):
        new_constraints = rule.get("constraint", [])
        if random.random() < 0.5:
            # Inject an additional constraint with plausible operand/operator/value
            new_constraints.append({
                "leftOperand": random.choice(["count", "purpose", "systemDevice", "elapsedTime"]),
                "operator": random.choice(["lt", "gt", "eq", "isAnyOf", "isNoneOf"]),
                "rightOperand": random.choice([3, 5, 10, "research", "education", "laptop", "mobile"])
            })
        rule["constraint"] = new_constraints

    for rule_type in ["permission", "prohibition", "obligation"]:
        for rule in policy.get(rule_type, []):
            maybe_add_constraint(rule)

    return policy
