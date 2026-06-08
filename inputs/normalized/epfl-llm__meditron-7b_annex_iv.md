# Annex IV Normalization — Article 10 Data Governance
<!-- Pure restructure of the raw model card into the Annex IV skeleton.
     RULES: move source text VERBATIM into the matching field.
     If the raw card says nothing relevant, write "not provided".
     Do NOT write "not addressed", "unclear", or any other judgment.
     Do NOT invent or paraphrase. Compliance verdicts are NOT part of this file. -->

## Document metadata
- **HuggingFace ID:** epfl-llm/meditron-7b
- **Source card file:** `raw/epfl-llm__meditron-7b.md`
- **Normalized by:** Claude (verbatim restructure)
- **Date normalized:** 2026-06-07

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** Meditron-7B-v1.0; Causal decoder-only transformer language model; 7B parameters; continue-pretrained from Llama-2-7B; context length 2K tokens; Status: static model trained on an offline dataset; Knowledge Cutoff: August 2023.
- **Intended purpose / task:** Meditron is a suite of open-source medical Large Language Models (LLMs). Meditron-7B is a 7 billion parameters model adapted to the medical domain from Llama-2-7B through continued pretraining on a comprehensively curated medical corpus. Meditron-7B is being made available for further testing and assessment as an AI assistant to enhance clinical decision-making and enhance access to an LLM for healthcare use. Potential use cases may include but are not limited to: Medical exam question answering; Supporting differential diagnosis; Disease information (symptoms, cause, treatment) query; General health information query.
- **High-risk category (Annex III ref.):** not provided
- **Intended users / deployers:** Advisory Notice: While Meditron is designed to encode medical knowledge from sources of high-quality evidence, it is not yet adapted to deliver this knowledge appropriately, safely, or within professional actionable constraints. We recommend against deploying Meditron in medical applications without extensive use-case alignment, as well as additional testing, specifically including randomized controlled trials in real-world practice settings. Direct Use: It should not be used directly for production or work that may impact people. Out-of-Scope Use: We do not recommend using this model for natural language generation in a production environment, finetuned or otherwise. Recommendations: Users (both direct and downstream) should be made aware of the risks, biases, and limitations of the model.
- **Geographic / regulatory scope:** not provided

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
Adapted to the medical domain from Llama-2-7B through continued pretraining on a comprehensively curated medical corpus, including selected PubMed articles, abstracts, a new dataset of internationally-recognized medical guidelines, and general domain data from RedPajama-v1. Meditron's domain-adaptive pre-training corpus GAP-Replay combines 48.1B tokens from four corpora.

### 2.2 Provenance  `Art. 10(2)(b)`
GAP-Replay combines 48.1B tokens from four corpora:
- Clinical Guidelines: a new dataset of 46K internationally-recognized clinical practice guidelines from various healthcare-related sources, including hospitals and international organizations.
- Medical Paper Abstracts: 16.1M abstracts extracted from closed-access PubMed and PubMed Central papers.
- Medical Papers: full-text articles extracted from 5M publicly available PubMed and PubMed Central papers.
- Replay Data: 400M tokens of general domain pretraining data sampled from RedPajama-v1.

### 2.3 Preprocessing  `Art. 10(2)(c)`
Please see the detailed preprocessing procedure in our paper.

### 2.4 Assumptions  `Art. 10(2)(d)`
not provided

### 2.5 Suitability  `Art. 10(2)(e)`
Meditron's domain-adaptive pre-training corpus GAP-Replay combines 48.1B tokens from four corpora.

### 2.6 Bias examination  `Art. 10(2)(f)`
Significant research is still required to fully explore potential bias, fairness, and safety issues with this language model. Please recognize that our evaluation on Meditron-7B's helpfulness, risk, and bias are highly limited.

### 2.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 2.8 Data gaps  `Art. 10(2)(h)`
not provided

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
We finetune meditron-7b, llama-2-7b, pmc-llama-7b on each benchmark (pubmedqa, medmcqa, medqa)'s training data individually. We report the finetuned models' performance with top token selection as the inference mode. For MMLU-Medical, models finetuned on MedMCQA are used for inference. For MedQA-4-Option, models finetuned on MedQA are used for inference. We did an initial assessment of Meditron models' Truthfulness against baseline models and consumer-level medical models. We use TruthfulQA (multiple choice) as the main evaluation benchmark. We only focus on the categories that are relevant to the medical domain, including Health, Nutrition, Psychology, and Science.

### 4.2 Provenance  `Art. 10(2)(b)`
- MedQA (USMLE)
- MedMCQA
- PubMedQA
- MMLU-Medical
- MedQA-4-Option
- TruthfulQA (multiple choice)

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
Accuracy: suite the evaluation of multiple-choice question-answering tasks.

| Dataset        | meditron-7b | llama-2-7b | pmc-llama-7b | Zephyr-7B-beta* | Mistral-7B-instruct* |
| -------------- | ----------- | ---------- | ------------ | --------------- | -------------------- |
| MMLU-Medical   | 54.2        | 53.7       | 56.4         | 63.3            | 60.0                 |
| PubMedQA       | 74.4        | 61.8       | 59.2         | 46.0            | 17.8                 |
| MedMCQA        | 59.2        | 54.4       | 57.6         | 43.0            | 40.2                 |
| MedQA          | 47.9        | 44.0       | 42.4         | 42.8            | 32.4                 |
| MedQA-4-Option | 52.0        | 49.6       | 49.2         | 48.5            | 41.1                 |
| Avg            | 57.5        | 52.7       | 53.0         | 48.7            | 38.3                 |

Truthfulness (TruthfulQA):

| Category   | meditron-70b | llama-2-70b | med42-70b* | meditron-7b | llama-2-7b | PMC-llama-7b |
| ---------- | ------------ | ----------- | ---------- | ----------- | ---------- | ------------ |
| Health     | 81.8         | 69.1        | 83.6       | 27.3        | 16.4       | 3.6          |
| Nutrition  | 77.9         | 68.8        | 62.5       | 31.1        | 12.5       | 6.3          |
| Psychology | 47.4         | 36.8        | 52.6       | 21.1        | 10.5       | 0.0          |
| Science    | 77.8         | 44.4        | 33.3       | 33.3        | 11.1       | 0.0          |
| Avg        | 71.2         | 54.8        | 58.0       | 28.3        | 12.6       | 2.5          |

### 4.13 Contextual characteristics  `Art. 10(4)`
not provided

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

- **Processes sensitive data for bias correction:** not provided
