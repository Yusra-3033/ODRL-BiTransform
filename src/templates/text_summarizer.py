# text_summarizer.py
# ----------------------------------------------------------------------------
# Converts ODRL policy structures into human-readable text and keyword summaries.
# Useful for interpretability, debugging, or presenting policies in natural language.
# ----------------------------------------------------------------------------

import random

# ----------------------------------------------------------------------------
# Operator Translation
# ----------------------------------------------------------------------------

def translate_operator(op: str) -> str:
    """Translate symbolic operators into natural language phrases."""
    return {
        "lt": "is less than",
        "lteq": "is less than or equal to",
        "eq": "is equal to",
        "neq": "is not equal to",
        "gt": "is greater than",
        "gteq": "is greater than or equal to",
        "isA": "is a",
        "isAnyOf": "is any of",
        "isNoneOf": "is none of",
        "hasPart": "has part",
        "isPartOf": "is part of"
    }.get(op, op)

# ----------------------------------------------------------------------------
# Text Extraction Helpers
# ----------------------------------------------------------------------------

def extract_asset_name(uri):
    """Extract a readable name from an asset URI."""
    return uri.split(":")[-1] if ":" in uri else uri.split("/")[-1]

# ----------------------------------------------------------------------------
# Constraint Description
# ----------------------------------------------------------------------------

def describe_constraints(constraints):
    """Convert a list of ODRL constraints into a readable sentence."""
    if not constraints:
        return ""

    def flatten(c):
        if "@type" in c:
            left = c["leftOperand"]
            op = translate_operator(c["operator"])
            right = c["rightOperand"]
            return f"{left} {op} {right}"
        elif any(k in c for k in ["and", "or", "xone"]):
            k = next(iter(c))
            inner = "; or ".join(flatten(x) for x in c[k]['@list'])
            if k == "and":
                return " and ".join(flatten(x) for x in c[k]['@list'])
            elif k == "or":
                return f"at least one of the following applies: ({inner})"
            elif k == "xone":
                return f"exactly one of the following applies: ({inner})"
        return ""

    parts = [flatten(c) for c in constraints]
    return "only if " + " and ".join(parts)

# ----------------------------------------------------------------------------
# Policy Text Enhancement
# ----------------------------------------------------------------------------

def enhance_policy(policy):
    """Add human-readable text and keywords to a policy dictionary."""
    odrl = policy.get("odrl", {})
    permission_texts = []
    prohibition_texts = []
    obligation_texts = []
    keywords = set()

    def describe_rule(rule, verbs):
        action = rule.get("action")
        target = extract_asset_name(rule.get("target", "an asset"))
        assignee = extract_asset_name(rule.get("assignee", "a party"))
        verb = random.choice(verbs)
        constraint_desc = describe_constraints(rule.get("constraint", []))
        base = f"{verb} {assignee} to {action} the asset {target}"
        return f"{base} {constraint_desc}".strip(), action

    if "permission" in odrl:
        for perm in odrl["permission"]:
            t, a = describe_rule(perm, ["allows", "permits", "grants permission to", "authorizes", "enables"])
            permission_texts.append(t)
            keywords.add(a)

    if "prohibition" in odrl:
        for prob in odrl["prohibition"]:
            t, a = describe_rule(prob, ["prohibits", "disallows", "denies", "restricts"])
            prohibition_texts.append(t)
            keywords.add(a)

    if "obligation" in odrl:
        for obl in odrl["obligation"]:
            t, a = describe_rule(obl, ["requires", "obligates", "mandates", "expects"])
            obligation_texts.append(t)
            keywords.add(a)

    all_text = ". ".join(permission_texts + prohibition_texts + obligation_texts)
    policy["text"] = all_text.strip(". ") + "."
    policy["keywords"] = list(sorted(keywords))

    return policy
