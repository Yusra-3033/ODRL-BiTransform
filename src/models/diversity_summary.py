# diversity_summary.py
# -----------------------------------------------------------------------------
# Analyze generated ODRL policies for diversity, semantic issues, and export to TTL
# -----------------------------------------------------------------------------

import json
from collections import Counter, defaultdict
from rdflib import Graph
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import re

INPUT_FILE = "outputs/generated_and_described.json"
TTL_DIR = "outputs/reports/ttl_exports"
PLOTS_DIR = "outputs/plots/llm_analysis"


def load_policies():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_fields(policies):
    actions = Counter()
    left_operands = Counter()
    operators = Counter()
    assignees = Counter()
    assigners = Counter()
    targets = Counter()
    uids = set()
    uid_duplicates = []

    for entry in policies:
        policy = entry["odrl"]
        uid = policy.get("uid")
        if uid in uids:
            uid_duplicates.append(uid)
        else:
            uids.add(uid)

        for rule_type in ["permission", "prohibition", "obligation"]:
            for rule in policy.get(rule_type, []):
                actions[rule.get("action")] += 1
                targets[rule.get("target")] += 1
                assignees[rule.get("assignee", "public")] += 1
                assigners[rule.get("assigner", "none")] += 1
                for constraint in rule.get("constraint") or []:
                    left_operands[constraint.get("leftOperand")] += 1
                    operators[constraint.get("operator")] += 1

    return actions, left_operands, operators, assignees, assigners, targets, uid_duplicates


def flag_conflicts(policies):
    conflicts = []
    for i, entry in enumerate(policies):
        seen = defaultdict(set)
        policy = entry["odrl"]
        for rule_type in ["permission", "prohibition"]:
            for rule in policy.get(rule_type, []):
                key = (rule.get("target"), rule.get("assignee", "public"))
                seen[key].add(rule_type)
        for key, types in seen.items():
            if "permission" in types and "prohibition" in types:
                conflicts.append({"policy_index": i + 1, "target": key[0], "assignee": key[1]})
    return conflicts


def find_constraint_contradictions(policies):
    contradictory = []
    for i, entry in enumerate(policies):
        policy = entry["odrl"]
        all_constraints = defaultdict(list)
        for rule_type in ["permission", "prohibition", "obligation"]:
            for rule in policy.get(rule_type, []):
                for c in rule.get("constraint") or []:
                    key = c.get("leftOperand")
                    op = c.get("operator")
                    val = str(c.get("rightOperand"))
                    if key and op:
                        all_constraints[key].append((op, val))

        for operand, constraints in all_constraints.items():
            ops = [c[0] for c in constraints]
            if any(o in ops for o in ["lt", "lessThan", "lteq"]) and any(o in ops for o in ["gt", "greaterThan", "gteq"]):
                contradictory.append({"policy_index": i + 1, "operand": operand, "constraints": constraints})

    return contradictory


def export_turtle(policies):
    Path(TTL_DIR).mkdir(parents=True, exist_ok=True)
    for i, entry in enumerate(policies):
        g = Graph()
        policy_jsonld = entry["odrl"]
        g.parse(data=json.dumps(policy_jsonld), format="json-ld")
        ttl_path = Path(TTL_DIR) / f"policy_{i + 1}.ttl"
        g.serialize(destination=ttl_path, format="turtle")


def plot_bar_chart(counter, title, filename):
    Path(PLOTS_DIR).mkdir(parents=True, exist_ok=True)
    items = counter.most_common()
    if not items:
        return
    labels, values = zip(*items)
    plt.figure(figsize=(10, 5))
    sns.barplot(x=list(labels), y=list(values))
    plt.xticks(rotation=45, ha="right")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(Path(PLOTS_DIR) / filename)
    plt.close()


def main():
    policies = load_policies()
    actions, operands, ops, assignees, assigners, targets, uid_dupes = extract_fields(policies)

    print("\n📊 Action Frequency:")
    print(actions.most_common())
    print("\n📊 Constraint Operands:")
    print(operands.most_common())
    print("\n📊 Operators:")
    print(ops.most_common())
    print("\n📊 Assignees:")
    print(assignees.most_common(5))
    print("\n📊 Targets:")
    print(targets.most_common(5))

    if uid_dupes:
        print("\n⚠️ Duplicate UIDs detected:")
        for uid in uid_dupes:
            print(f" - {uid}")
    else:
        print("\n✅ All UIDs are unique.")

    print("\n📌 Checking for permission/prohibition conflicts...")
    conflicts = flag_conflicts(policies)
    if conflicts:
        for c in conflicts:
            print(f"⚠️ Policy {c['policy_index']} has conflict on target {c['target']} for assignee {c['assignee']}")
    else:
        print("✅ No semantic conflicts found.")

    print("\n🧠 Checking for contradictory constraints...")
    contradictions = find_constraint_contradictions(policies)
    if contradictions:
        for c in contradictions:
            print(f"⚠️ Policy {c['policy_index']} has conflicting constraints on '{c['operand']}': {c['constraints']}")
    else:
        print("✅ No logical contradictions found.")

    print("\n📈 Generating charts...")
    plot_bar_chart(actions, "Action Frequency", "actions.png")
    plot_bar_chart(operands, "Constraint Operands", "operands.png")
    plot_bar_chart(ops, "Operators", "operators.png")

    print("\n🔄 Exporting all policies to Turtle format...")
    export_turtle(policies)
    print(f"✅ Turtle files saved to: {TTL_DIR}")
    print(f"✅ Plots saved to: {PLOTS_DIR}")


if __name__ == "__main__":
    main()
