# postprocess_policy.py
# -----------------------------------------------------------------------------
# Cleans ODRL policies by removing contradictory or malformed constraints
# -----------------------------------------------------------------------------

import json
from pathlib import Path
from collections import defaultdict

INPUT_FILE = "outputs/generated_and_described.json"
OUTPUT_FILE = "outputs/cleaned_and_described.json"


def clean_constraints(policy):
    for rule_type in ["permission", "prohibition", "obligation"]:
        for rule in policy.get(rule_type, []):
            constraints = rule.get("constraint") or []
            seen = defaultdict(list)
            cleaned = []
            for c in constraints:
                key = (c.get("leftOperand"), str(c.get("rightOperand")))
                op = c.get("operator")
                seen[key].append(op)

            for c in constraints:
                ops = seen[(c.get("leftOperand"), str(c.get("rightOperand")))]
                # Remove if contradictory pair found (e.g. lt and gt)
                if ("lt" in ops and "gt" in ops) or ("lteq" in ops and "gteq" in ops):
                    continue
                cleaned.append(c)

            rule["constraint"] = cleaned or []

    return policy


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = []
    for entry in data:
        policy = entry["odrl"]
        entry["odrl"] = clean_constraints(policy)
        cleaned.append(entry)

    Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2)

    print(f"✅ Cleaned policies saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
