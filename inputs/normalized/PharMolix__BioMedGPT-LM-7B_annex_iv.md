# Annex IV Normalization — Article 10 Data Governance
<!-- Pure restructure of the raw model card into the Annex IV skeleton.
     RULES: move source text VERBATIM into the matching field.
     If the raw card says nothing relevant, write "not provided".
     Do NOT write "not addressed", "unclear", or any other judgment.
     Do NOT invent or paraphrase. Compliance verdicts are NOT part of this file. -->

## Document metadata
- **HuggingFace ID:** PharMolix/BioMedGPT-LM-7B
- **Source card file:** `raw/PharMolix__BioMedGPT-LM-7B.md`
- **Normalized by:** Claude (verbatim restructure)
- **Date normalized:** 2026-06-07

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** BioMedGPT-LM-7B
- **Intended purpose / task:** BioMedGPT-LM-7B is the first large generative language model based on Llama2 in the biomedical domain. It was fine-tuned from the Llama2-7B-Chat with millions of biomedical papers from the S2ORC corpus.
- **High-risk category (Annex III ref.):** not provided
- **Intended users / deployers:** This repository holds BioMedGPT-LM-7B, and we emphasize the responsible and ethical use of this model. BioMedGPT-LM-7B should NOT be used to provide services to the general public. Generating any content that violates applicable laws and regulations, such as inciting subversion of state power, endangering national security and interests, propagating terrorism, extremism, ethnic hatred and discrimination, violence, pornography, or false and harmful information, etc. is strictly prohibited. BioMedGPT-LM-7B is not liable for any consequences arising from any content, data, or information provided or published by users.
- **Geographic / regulatory scope:** not provided

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
It was fine-tuned from the Llama2-7B-Chat with millions of biomedical papers from the S2ORC corpus. Through further fine-tuning, BioMedGPT-LM-7B outperforms or is on par with human and significantly larger general-purpose foundation models on several biomedical QA benchmarks.

### 2.2 Provenance  `Art. 10(2)(b)`
Millions of biomedical papers from the S2ORC corpus (https://github.com/allenai/s2orc/blob/master/README.md).

### 2.3 Preprocessing  `Art. 10(2)(c)`
The fine-tuning data are extracted from millions of biomedical papers in S2ORC data using PubMed Central (PMC)-ID and PubMed ID as criteria.

### 2.4 Assumptions  `Art. 10(2)(d)`
not provided

### 2.5 Suitability  `Art. 10(2)(e)`
BioMedGPT-LM-7B is fine-tuned on over 26 billion tokens highly pertinent to the field of biomedicine.

### 2.6 Bias examination  `Art. 10(2)(f)`
not provided

### 2.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 2.8 Data gaps  `Art. 10(2)(h)`
not provided

### 2.9 Relevance  `Art. 10(3)`
Over 26 billion tokens highly pertinent to the field of biomedicine.

### 2.10 Representativeness  `Art. 10(3)`
not provided

### 2.11 Statistical properties  `Art. 10(3)`
not provided

### 2.12 Quality metrics  `Art. 10(3)`
not provided

### 2.13 Contextual characteristics  `Art. 10(4)`
not provided

---

## Section 3 — Validation Dataset
*(same 13 fields as Section 2)*

### 3.1 Design choices  `Art. 10(2)(a)`
not provided

### 3.2 Provenance  `Art. 10(2)(b)`
not provided

### 3.3 Preprocessing  `Art. 10(2)(c)`
not provided

### 3.4 Assumptions  `Art. 10(2)(d)`
not provided

### 3.5 Suitability  `Art. 10(2)(e)`
not provided

### 3.6 Bias examination  `Art. 10(2)(f)`
not provided

### 3.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 3.8 Data gaps  `Art. 10(2)(h)`
not provided

### 3.9 Relevance  `Art. 10(3)`
not provided

### 3.10 Representativeness  `Art. 10(3)`
not provided

### 3.11 Statistical properties  `Art. 10(3)`
not provided

### 3.12 Quality metrics  `Art. 10(3)`
not provided

### 3.13 Contextual characteristics  `Art. 10(4)`
not provided

---

## Section 4 — Testing Dataset
*(same 13 fields; if no independent test set exists, write "not provided")*

### 4.1 Design choices  `Art. 10(2)(a)`
not provided

### 4.2 Provenance  `Art. 10(2)(b)`
not provided

### 4.3 Preprocessing  `Art. 10(2)(c)`
not provided

### 4.4 Assumptions  `Art. 10(2)(d)`
not provided

### 4.5 Suitability  `Art. 10(2)(e)`
not provided

### 4.6 Bias examination  `Art. 10(2)(f)`
not provided

### 4.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 4.8 Data gaps  `Art. 10(2)(h)`
not provided

### 4.9 Relevance  `Art. 10(3)`
not provided

### 4.10 Representativeness  `Art. 10(3)`
not provided

### 4.11 Statistical properties  `Art. 10(3)`
not provided

### 4.12 Quality metrics  `Art. 10(3)`
not provided

### 4.13 Contextual characteristics  `Art. 10(4)`
not provided

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

- **Processes sensitive data for bias correction:** not provided
