# quality_report.py
# -----------------------------------------------------------------------------
# Analyze ODRL policies for structure, logical quality, and diversity issues
# -----------------------------------------------------------------------------

import json
from collections import Counter, defaultdict
from pathlib import Path

INPUT_FILE = "outputs/cleaned_and_described.json"
REPORT_FILE = "outputs/reports/quality_report.json"


def evaluate(policies):
    stats = {
        "total": len(policies),
        "invalid_constraints": [],
        "duplicate_uids": set(),
        "action_frequency": Counter(),
        "left_operands": Counter(),
        "operators": Counter(),
        "targets": Counter(),
    }
    seen_uids = set()

    for i, entry in enumerate(policies):
        policy = entry["odrl"]
        uid = policy.get("uid")
        if uid in seen_uids:
            stats["duplicate_uids"].add(uid)
        seen_uids.add(uid)

        for rule_type in ["permission", "prohibition", "obligation"]:
            for rule in policy.get(rule_type, []):
                stats["action_frequency"][rule.get("action")] += 1
                stats["targets"][rule.get("target")] += 1
                for c in rule.get("constraint", []):
                    stats["left_operands"][c.get("leftOperand")] += 1
                    stats["operators"][c.get("operator")] += 1

                # Check for logically contradictory constraints
                ops = defaultdict(list)
                for c in rule.get("constraint", []):
                    ops[c["leftOperand"]].append(c["operator"])
                for key, op_list in ops.items():
                    if "lt" in op_list and "gt" in op_list:
                        stats["invalid_constraints"].append({"policy_index": i + 1, "field": key, "ops": op_list})

    stats["duplicate_uids"] = list(stats["duplicate_uids"])
    return stats


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        policies = json.load(f)

    report = evaluate(policies)
    Path(REPORT_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"📋 Quality report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
