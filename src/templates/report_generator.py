# report_generator.py
# ----------------------------------------------------------------------------
# Generates a Markdown summary report based on policy validation results.
# ----------------------------------------------------------------------------

import json
from datetime import datetime
from policy_validator import validate_template_policies

# ----------------------------------------------------------------------------
# Report Generator
# ----------------------------------------------------------------------------

def generate_report(input_path: str, output_path: str = "outputs/report.md"):
    """Generate a validation report and write it to a markdown file."""
    results = validate_template_policies(input_path)

    total = results["total_policies"]
    valid = results["valid_policies"]
    json_valid = results["json_schema_valid"]
    shacl_valid = results["shacl_valid"]
    policy_types = results["policy_types"]
    error_summary = results["error_summary"]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = "============================================================\n"
    report += f"ODRL POLICY VALIDATION REPORT  \nGenerated: {timestamp}\n"
    report += "============================================================\n"
    report += f"Total Policies: {total}\n"
    report += f"Overall Valid: {valid} ({valid/total*100:.1f}%)\n"
    report += f"JSON Schema Valid: {json_valid} ({json_valid/total*100:.1f}%)\n"
    report += f"SHACL Valid: {shacl_valid} ({shacl_valid/total*100:.1f}%)\n"
    report += "\n"

    if policy_types:
        report += "Policy Type Distribution:\n"
        for ptype, count in policy_types.items():
            report += f"  - {ptype}: {count}\n"
        report += "\n"

    if error_summary:
        report += "Error Summary:\n"
        for error_type, count in error_summary.items():
            report += f"  - {error_type}: {count}\n"
        report += "\n"

    report += "============================================================\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(report)

# ----------------------------------------------------------------------------
# Script Entry
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    generate_report("outputs/template_based_policies.json")
