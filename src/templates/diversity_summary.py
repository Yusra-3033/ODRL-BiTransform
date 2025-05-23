# diversity_summary.py
# ----------------------------------------------------------------------------
# Computes diversity metrics, generates matplotlib visualizations,
# and creates a Markdown summary report for ODRL policy analysis.
# ----------------------------------------------------------------------------

from collections import Counter
from typing import Dict, List
import matplotlib.pyplot as plt
import os
import json

# ----------------------------------------------------------------------------
# Compute Diversity Metrics
# ----------------------------------------------------------------------------

def compute_diversity(policies: List[Dict]) -> Dict:
    policy_types = Counter()
    actions = set()
    operands = set()
    operators = set()
    rule_type_counts = Counter()

    for policy in policies:
        odrl = policy.get("odrl", {})
        policy_types[odrl.get("@type", "Unknown")] += 1

        for section in ["permission", "prohibition", "obligation"]:
            rule_type_counts[section] += len(odrl.get(section, []))
            for rule in odrl.get(section, []):
                act = rule.get("action")
                if isinstance(act, dict):
                    actions.add(act.get("rdf:value"))
                    for r in act.get("refinement", []):
                        operands.add(r.get("leftOperand"))
                        operators.add(r.get("operator"))
                else:
                    actions.add(act)

                for c in rule.get("constraint", []):
                    if any(k in c for k in ["xone", "and", "or"]):
                        for group in [c.get(k, {}).get("@list", []) for k in ["xone", "and", "or"] if k in c]:
                            for sub in group:
                                operands.add(sub.get("leftOperand"))
                                operators.add(sub.get("operator"))
                    else:
                        operands.add(c.get("leftOperand"))
                        operators.add(c.get("operator"))

    return {
        "policy_types": dict(policy_types),
        "unique_actions": len(actions),
        "unique_operands": len(operands),
        "unique_operators": len(operators),
        "rule_type_distribution": dict(rule_type_counts)
    }

# ----------------------------------------------------------------------------
# Generate Diversity Visualizations
# ----------------------------------------------------------------------------

def plot_diversity(policies: List[Dict], save_dir: str = "outputs/plots") -> None:
    os.makedirs(save_dir, exist_ok=True)

    action_counter = Counter()
    operand_counter = Counter()
    operator_counter = Counter()
    rule_type_counter = Counter()

    for policy in policies:
        odrl = policy.get("odrl", {})
        for section in ["permission", "prohibition", "obligation"]:
            rule_type_counter[section] += len(odrl.get(section, []))
            for rule in odrl.get(section, []):
                act = rule.get("action")
                if isinstance(act, dict):
                    action_counter[act.get("rdf:value")] += 1
                    for r in act.get("refinement", []):
                        operand_counter[r.get("leftOperand")] += 1
                        operator_counter[r.get("operator")] += 1
                else:
                    action_counter[act] += 1

                for c in rule.get("constraint", []):
                    if any(k in c for k in ["xone", "and", "or"]):
                        for group in [c.get(k, {}).get("@list", []) for k in ["xone", "and", "or"] if k in c]:
                            for sub in group:
                                operand_counter[sub.get("leftOperand")] += 1
                                operator_counter[sub.get("operator")] += 1
                    else:
                        operand_counter[c.get("leftOperand")] += 1
                        operator_counter[c.get("operator")] += 1

    def plot_counter(counter: Counter, title: str, filename: str, top_n: int = 10):
        items = counter.most_common(top_n)
        labels, values = zip(*items) if items else ([], [])
        plt.figure(figsize=(10, 5))
        plt.bar(labels, values)
        plt.title(title)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, filename))
        plt.close()

    plot_counter(action_counter, "Top Actions", "actions.png")
    plot_counter(operand_counter, "Top Constraint Operands", "operands.png")
    plot_counter(operator_counter, "Top Constraint Operators", "operators.png")
    plot_counter(rule_type_counter, "Rule Type Distribution", "rule_types.png")

# ----------------------------------------------------------------------------
# Markdown Summary
# ----------------------------------------------------------------------------

def save_diversity_summary(policies: List[Dict], path: str = "outputs/reports/diversity_summary.md") -> None:
    stats = compute_diversity(policies)

    with open(path, "w", encoding="utf-8") as f:
        f.write("### 🎯 Diversity Summary\n\n")
        f.write(f"**Unique Actions:** `{stats['unique_actions']}`  \n")
        f.write(f"**Unique Operands:** `{stats['unique_operands']}`  \n")
        f.write(f"**Unique Operators:** `{stats['unique_operators']}`  \n\n")

        f.write("**Policy Type Distribution:**\n")
        for key, val in stats["policy_types"].items():
            f.write(f"- `{key}`: **{val}**\n")
        f.write("\n**Rule Type Distribution:**\n")
        for key, val in stats["rule_type_distribution"].items():
            f.write(f"- `{key}`: **{val}**\n")
