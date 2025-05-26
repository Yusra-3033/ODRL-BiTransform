<<<<<<< HEAD
## 🎓 Leveraging Large Language Models for Bidirectional Translation Between ODRL Policies and Natural Language
=======
# 🎓 Master Thesis Project
>>>>>>> temp-llm-pipeline

This project aims to generate and validate synthetic ODRL 2.2 policy data for training natural language translation models, combining structured templates and GPT-based generation.

---

## 🧩 Project Phases Overview

| Phase | Description |
|-------|-------------|
| 1️⃣ Template-Based Policy Generation | Structured JSON-LD policy generation from deterministic templates |
| 2️⃣ GPT-Based Policy Synthesis | Few-shot prompted generation using GPT-4 or similar LLMs |
| 3️⃣ Text ↔ ODRL Alignment | Generate natural language descriptions of policies for translation training |
| 4️⃣ Data Validation & Evaluation | Ensure schema, ontology, and semantic correctness |
| 5️⃣ Fine-Tuning Models | Train LLaMA/Mistral using synthetic aligned pairs |

---

## 🏗️ Phase 1: Template-Based Generation

Structured policy generation ensures full control and ODRL compliance. It uses:

- JSON-LD `@context` enforcement
- Policy-type specific rule constraints
- Operand/operator semantic alignment
- Natural language summaries
- Validation and diversity reporting

### 📁 Directory Structure

```bash
.
├── config/                  # Config files, vocabularies, schema
├── outputs/                 # Generated data, plots, reports
├── src/templates/           # Core policy generation modules
```

### 🔧 Configuration Highlights (`config/config.yml`)

- `num_policies`: number of policies to generate
- Controlled lists: actions, operands, operators
- Sample URIs for assets and parties

### 🚀 Usage

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/templates/generate_policies.py
```

This will:

- Generate policies
- Enhance them with text
- Validate with schema + SHACL
- Plot and summarize diversity

---

## 🧪 Validation Logic

- **Schema validation:** JSON Schema (`odrl_policy_schema.json`)
- **RDF/SHACL validation:** via `shacl_shapes.ttl`
- **Context normalization:** using `odrl_context.json`

Reports:

- Markdown summaries in `outputs/reports/`
- Matplotlib plots in `outputs/plots/`

---

## 📦 Outputs

| File/Folder | Description |
|-------------|-------------|
| `outputs/policies/template_based_policies.json` | Generated ODRL policies |
| `outputs/reports/template_validation_report.md` | Schema & SHACL validation results |
| `outputs/reports/diversity_summary.md` | Diversity metrics and coverage |
| `outputs/plots/` | Top actions, operands, operators visualized |

---

### Output Review

- ✅ Strong ODRL compliance with proper use of `@context`, `uid`, and rule types (permission, prohibition, obligation)
- ✅ Wide range of ODRL actions (e.g., play, modify, install, share, stream, anonymize)
- ✅ Rich constraint modeling (e.g., `xone`, `and`, `or`, `isAnyOf`, `isNoneOf`, `gteq`, `lteq`)
- ✅ Accurate natural language generation aligned with JSON policies
- ✅ Inclusion of edge constructs like `relativePosition`, `absolutePosition`, and compound constraints

---

## 🤖 Phase 2: GPT-4 Based Synthesis (Planned)

This phase will:

- Use few-shot prompts to generate policies
- Enforce schema compliance via validation
- Expand data diversity and expressiveness

🧠 Prompt templates will ensure format and vocabulary alignment with the ODRL standard.

---
