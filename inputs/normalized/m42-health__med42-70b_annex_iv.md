# Annex IV Normalization — Article 10 Data Governance
<!-- Pure restructure of the raw model card into the Annex IV skeleton.
     RULES: move source text VERBATIM into the matching field.
     If the raw card says nothing relevant, write "not provided".
     Do NOT write "not addressed", "unclear", or any other judgment.
     Do NOT invent or paraphrase. Compliance verdicts are NOT part of this file. -->

## Document metadata
- **HuggingFace ID:** m42-health/med42-70b
- **Source card file:** `raw/m42-health__med42-70b.md`
- **Normalized by:** Claude (verbatim restructure)
- **Date normalized:** 2026-06-07

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** Med42 - Clinical Large Language Model (med42-70b); 70 billion parameters; finetuned from Llama-2 - 70B; context length 4k tokens.
- **Intended purpose / task:** Med42 is an open-access clinical large language model (LLM) developed by M42 to expand access to medical knowledge. Built off LLaMA-2 and comprising 70 billion parameters, this generative AI system provides high-quality answers to medical questions. Med42 is being made available for further testing and assessment as an AI assistant to enhance clinical decision-making and enhance access to an LLM for healthcare use. Potential use cases include: Medical question answering; Patient record summarization; Aiding medical diagnosis; General health Q&A.
- **High-risk category (Annex III ref.):** not provided
- **Intended users / deployers:** Limitations & Safe Use: Med42 is not ready for real clinical use. Extensive human evaluation is undergoing as it is required to ensure safety. Potential for generating incorrect or harmful information. Risk of perpetuating biases in training data. Use this model responsibly! Do not rely on it for medical usage without rigorous safety testing.
- **Geographic / regulatory scope:** not provided

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
Beginning with the base LLaMa-2 model, Med42 was instruction-tuned on a dataset of ~250M tokens compiled from different open-access sources, including medical flashcards, exam questions, and open-domain dialogues.

### 2.2 Provenance  `Art. 10(2)(b)`
A dataset of ~250M tokens compiled from different open-access sources, including medical flashcards, exam questions, and open-domain dialogues.

### 2.3 Preprocessing  `Art. 10(2)(c)`
not provided

### 2.4 Assumptions  `Art. 10(2)(d)`
not provided

### 2.5 Suitability  `Art. 10(2)(e)`
A dataset of ~250M tokens.

### 2.6 Bias examination  `Art. 10(2)(f)`
not provided

### 2.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 2.8 Data gaps  `Art. 10(2)(h)`
Risk of perpetuating biases in training data.

### 2.9 Relevance  `Art. 10(3)`
not provided

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
Med42 achieves competitive performance on various medical benchmarks, including MedQA, MedMCQA, PubMedQA, HeadQA, and Measuring Massive Multitask Language Understanding (MMLU) clinical topics. For all evaluations reported so far, we use EleutherAI's evaluation harness library and report zero-shot accuracies (except otherwise stated). We compare the performance with that reported for other models (ClinicalCamel-70B, GPT-3.5, GPT-4.0, Med-PaLM 2).

### 4.2 Provenance  `Art. 10(2)(b)`
MedQA, MedMCQA, PubMedQA, HeadQA, MMLU clinical topics; USMLE Self-Assessment; USMLE Sample Exam.

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
| Dataset | Med42 | ClinicalCamel-70B | GPT-3.5 | GPT-4.0 | Med-PaLM-2 (5-shot)* |
|---|---|---|---|---|---|
| MMLU Clinical Knowledge | 74.3 | 69.8 | 69.8 | 86.0 | 88.3 |
| MMLU College Biology | 84.0 | 79.2 | 72.2 | 95.1 | 94.4 |
| MMLU College Medicine | 68.8 | 67.0 | 61.3 | 76.9 | 80.9 |
| MMLU Medical Genetics | 86.0 | 69.0 | 70.0 | 91.0 | 90.0 |
| MMLU Professional Medicine | 79.8 | 71.3 | 70.2 | 93.0 | 95.2 |
| MMLU Anatomy | 67.4 | 62.2 | 56.3 | 80.0 | 77.8 |
| MedMCQA | 60.9 | 47.0 | 50.1 | 69.5 | 71.3 |
| MedQA | 61.5 | 53.4 | 50.8 | 78.9 | 79.7 |
| USMLE Self-Assessment | 71.7 | - | 49.1 | 83.8 | - |
| USMLE Sample Exam | 72.0 | 54.3 | 56.9 | 84.3 | - |

Key performance metrics: Med42 achieves a 72% accuracy on the US Medical Licensing Examination (USMLE) sample exam, surpassing the prior state of the art among openly available medical LLMs. 61.5% on MedQA dataset (compared to 50.8% for GPT-3.5). Consistently higher performance on MMLU clinical topics compared to GPT-3.5.

### 4.13 Contextual characteristics  `Art. 10(4)`
not provided

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

- **Processes sensitive data for bias correction:** not provided
