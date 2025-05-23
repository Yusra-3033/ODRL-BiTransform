# generate_policies.py
# ----------------------------------------------------------------------------
# Main script for generating synthetic ODRL policies from templates.
# Includes enhancement to natural language, validation report,
# diversity summary, and visualizations.
# ----------------------------------------------------------------------------

from template_builder import template_json_variant
from text_summarizer import enhance_policy
from utils import load_config, generate_policy_id, save_json, log
from report_generator import generate_report
from diversity_summary import plot_diversity, save_diversity_summary
import os

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

config = load_config("config/config.yml")
n = config.get("num_policies", 50)

# Structured output paths
OUTPUT_DIR = "outputs"
POLICIES_DIR = os.path.join(OUTPUT_DIR, "policies")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")

os.makedirs(POLICIES_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

POLICY_FILE = os.path.join(POLICIES_DIR, "template_based_policies.json")
REPORT_FILE = os.path.join(REPORTS_DIR, "template_validation_report.md")
DIVERSITY_FILE = os.path.join(REPORTS_DIR, "diversity_summary.md")

# ----------------------------------------------------------------------------
# Policy Generation
# ----------------------------------------------------------------------------

template_based_policies = []

for _ in range(n):
    policy_id = generate_policy_id()
    odrl = template_json_variant(policy_id, config)
    raw_policy = {
        "id": policy_id,
        "odrl": odrl
    }
    enhanced_policy = enhance_policy(raw_policy)
    template_based_policies.append(enhanced_policy)

save_json(POLICY_FILE, template_based_policies)
log(f"[✔] {len(template_based_policies)} template-based policies saved to {POLICY_FILE}.")

# ----------------------------------------------------------------------------
# Reports and Visualizations
# ----------------------------------------------------------------------------

generate_report(POLICY_FILE, REPORT_FILE)
save_diversity_summary(template_based_policies, DIVERSITY_FILE)
plot_diversity(template_based_policies, save_dir=PLOTS_DIR)

log(f"[✔] Diversity summary saved to {DIVERSITY_FILE}.")
log(f"[✔] Visualizations saved to {PLOTS_DIR}.")
