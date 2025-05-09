## 📦 Dataset Generation Guide for ODRL-Based Policy Modeling

This document outlines the process, methodology, and tools used to generate high-quality datasets for ODRL (Open Digital Rights Language) policy modeling. The approach uses knowledge distillation from advanced LLMs to create training data for more affordable open-source models.

### 📋 Dataset Overview
The dataset consists of paired ODRL policy representations and their human-readable descriptions, enabling bidirectional transformation (ODRL ↔ text).

### 🧱 Structure of Each Entry

Each policy example is stored in the following structure:

```json
{
  "id": "unique-policy-id",
  "odrl": { /* Full ODRL JSON-LD policy */ },
  "text": "Human-readable description of the policy"
}
```


#### Fields:
`id`: Unique identifier for the example.
```json
  "id": "example-policy-001"
```
`odrl`: Full ODRL policy in JSON-LD format.
```json
  "odrl": {
    "@context": "...",
    "@type": "...",
    "uid": "...",
    "permission": [...],
    "prohibition": [...],
    "duty": [...]
  }
```
`text`: Human-readable explanation of the policy structure.
```json
  "text": "This [type] policy grants permission to use..."
```


### 📂 Domains Covered

The dataset includes ODRL policies from multiple domains:

* **Dataspaces Policies** (access limits, duties, constraints)
* **Cultural Heritage** (museum usage, regional access, digitization fees)
* **Healthcare / DUO** (population consent, biomedical restrictions)
* **Catena-X** (contract reference, framework agreement, industry usage)



### 🔍 Data Sources
High-quality ODRL samples (approximately 100) were collected from:

* W3C Sources:
  - W3C Information Model standard examples
  - W3C Vocabulary specification use cases
  - W3C Community Group implementations


* Industry Implementations:
  - Catena-X repository
  - Dataspace initiatives


* Research & Academic:
  - Fraunhofer FIT research papers
  - GitHub repositories (open source implementations)


* Custom Development:
  - Manually authored test cases
  - Domain-specific adaptations
  - Edge case scenarios for validation




### 🧩 Dataset Generation Overview

This project uses **knowledge distillation** to generate high-quality ODRL training data. A powerful LLM (like GPT-4o) creates structured examples, which can later be used to train smaller open-source models such as LLaMA 3.3 Instruct.




### 📦 System Components

- **TTL Ontology Files**  
  Define formal ODRL classes and relationships.

- **ODRL Information Model**  
  Acts as a guiding schema for structuring policies.

- **Labeled Examples**  
  Include annotated actions, constraints, and duties.

- **Pydantic JSON Schema**  
  Used to validate the structure of generated content.





### 🔄 Generation Pipeline
> This pipeline supports high-quality training data creation for instruction-tuned LLMs working with ODRL semantics.

#### 1. Seed Collection
- Collect ODRL samples from trusted sources.
- Group examples by domain (e.g.,general, cultural, healthcare ...).
- Identify recurring patterns and edge cases.

#### 2. Prompt Engineering
- Design templates that guide GPT-4o to generate valid ODRLs
- Create domain-specific prompt variants
- Include structural hints based on the ODRL ontology

#### 3. Synthetic Generation
- Use GPT-4o to generate diverse policy examples.
- Vary actions, constraints, and logical structures.
- Ensure coverage of different ODRL features.

#### 4. Manual Augmentation
- Add hand-crafted edge cases not found in datasets.
- Include corner cases and adversarial scenarios(Optional).
- Develop "_adversarial_" examples to challenge model robustness (Optional).

#### 5. Text–ODRL Pairing
- Match ODRL entries with natural language summaries.
- Use fixed sentence structures for consistency. ``` "The assigner is ___, the action is ___..." ```
- Prepare additional knowledge graph formats if needed (Could have KG for each domain).




### 🔎 Multi-layered Validation

Dataset quality is ensured through a combination of automated and manual checks:

- **JSON Repair**  
  Automatically fixes formatting errors using JSON repair libraries.

- **Schema Validation**  
  Validates each entry against a strict [Pydantic-based JSON schema](https://docs.pydantic.dev/) aligned with the ODRL information model.

- **SHACL Validation**  
  Uses Shapes Constraint Language to ensure syntactic and structural validity of RDF-based policies.

- **OWL Reasoning (Optional)**  
  Applies semantic checks using the HermiT OWL reasoner to detect logical contradictions and ontology misalignments.

- **Manual Validation**  
  A human expert reviews at least 30% of the generated dataset to ensure realism, consistency, and correctness.



---





### 📚 References & Resources

- [W3C ODRL Information Model](https://www.w3.org/TR/odrl-model/)
- [ODRL Ontology (TTL)](https://www.w3.org/ns/odrl/2/ODRL22.ttl)
- [Dataspaces Example Policies (FH St. Pölten)](https://github.com/fhstp/dataspaces-policies/tree/main/example-policies)
- [DUO to ODRL Mapping Project](https://github.com/besteves4/duo-odrl-dpv/tree/main/mappings)
- [Catena-X ODRL Profile](https://github.com/catenax-eV/cx-odrl-profile)
- *Fraunhofer FIT Paper:*  
  “From Instructions to ODRL Usage Policies” — [[PDF available upon Fraunhofer Publica](https://publica.fraunhofer.de/entities/publication/cac0343e-f6a1-4aca-ac9a-df295f9229d8)] 
