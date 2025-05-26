# --- preprocess_data.py ---
import json
import yaml

# Load original files
with open("config/config.yml", "r", encoding="utf-8") as f1:
    vocab = yaml.safe_load(f1)

with open("config/w3c_recommendations.txt", "r", encoding="utf-8") as f2:
    recommendations = f2.read().strip()

with open("config/odrl_policy_schema.json", "r", encoding="utf-8") as f3:
    ontology = json.load(f3)
    
#with open("data/w3c_examples.jsonld", "r", encoding="utf-8") as f4:
#    examples = json.load(f4)

# Combine all into one compact JSON
preprocessed = {
    "vocab": vocab,
    "recommendations": recommendations,
    "ontology": ontology,
#    "primer_examples": examples
}

# Save compact version
with open("config/preprocessed_data.json", "w", encoding="utf-8") as out:
    json.dump(preprocessed, out, separators=(",", ":"))
