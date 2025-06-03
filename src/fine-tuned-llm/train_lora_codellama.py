# train_lora_codellama.py
import json
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model
import torch
import os

# Load tokenizer and model
model_id = "meta-llama/Llama-2-70b-chat-hf"  

tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    #load_in_4bit=True,
    #torch_dtype=torch.float16,
    device_map="auto"
)

# Apply LoRA
peft_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, peft_config)

# Load datasets
paths = [
    "outputs/cleaned_and_described_gpt.json",
    "outputs/cleaned_and_described_llama.json",
    "outputs/policies/template_based_policies.json"
]

combined_data = []
for path in paths:
    if os.path.exists(path):
        with open(path, "r") as f:
            entries = json.load(f)
            for entry in entries:
                if "odrl" in entry:
                    prompt = f"Describe the following ODRL policy:\n{json.dumps(entry['odrl'], indent=2)}"
                    response = entry.get("text", "")
                    combined_data.append({
                        "messages": [
                            {"role": "user", "content": prompt},
                            {"role": "assistant", "content": response}
                        ]
                    })

hf_dataset = Dataset.from_list(combined_data)

def tokenize(example):
    chat = tokenizer.apply_chat_template(example["messages"], tokenize=False)
    return tokenizer(chat, truncation=True, max_length=2048, padding="max_length")

tokenized = hf_dataset.map(tokenize, remove_columns=["messages"])

training_args = TrainingArguments(
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    num_train_epochs=3,
    learning_rate=2e-5,
    fp16=True,
    output_dir="./odrl-codellama-lora",
    logging_steps=10,
    save_steps=500,
    save_total_limit=2
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized
)

trainer.train()
model.save_pretrained("./odrl-codellama-lora")
