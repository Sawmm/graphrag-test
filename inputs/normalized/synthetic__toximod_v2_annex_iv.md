# Annex IV Normalization — Article 10 Data Governance
<!-- Synthetic model card for diversity testing — very minimal documentation. -->

## Document metadata
- **System ID:** toximod-v2
- **Organisation:** SafeSpace AI Ltd, Dublin, Ireland
- **System type:** High-risk AI system (EU AI Act Annex III, §8 — online platform content moderation)
- **Intended purpose:** Automated detection and classification of toxic and harmful content in user-generated social media text for platform moderation queues.
- **Version:** 2.0.0
- **Date:** October 2025
- **Normalized by:** Synthetic (compliance testing)
- **Date normalized:** 2026-06-15

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** ToxiMod v2, version 2.0.0
- **Intended purpose / task:** Multi-label text classifier that identifies toxic content categories (hate speech, harassment, explicit content, misinformation, self-harm promotion) in social media posts. Outputs per-category confidence scores and a moderation action recommendation (allow/review/remove). Intended to support human moderation queues.
- **High-risk category (Annex III ref.):** Annex III §8 — AI systems intended to be used for the administration of justice and democratic processes.
- **Intended users / deployers:** Trust and safety teams at EU-based social media platforms.
- **Geographic / regulatory scope:** EU deployment under DSA content moderation obligations.

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
The training dataset was assembled from multiple publicly available toxic content datasets and internally annotated samples collected from partner platform APIs.

### 2.2 Provenance  `Art. 10(2)(b)`
Training data sourced from: Jigsaw Toxic Comment Classification dataset (Kaggle, CC BY 4.0), HatEval 2019 (SemEval shared task, CC BY 4.0), OLID dataset (Zampieri et al. 2019, public release), and 180,000 posts collected via Twitter/X Academic API (2021–2023) annotated internally. Platform API data collected under standard developer terms of service. Internal annotation conducted by a contracted annotation team under a service agreement with SafeSpace AI (contract SSAI-ANN-2023-001).

### 2.3 Preprocessing  `Art. 10(2)(c)`
Text normalised to lowercase. URLs replaced with [URL] token. User mentions replaced with [USER] token. Maximum sequence length 256 tokens (XLM-RoBERTa tokeniser). Posts exceeding length limit truncated.

### 2.4 Assumptions  `Art. 10(2)(d)`
not provided

### 2.5 Suitability  `Art. 10(2)(e)`
The training dataset contains approximately 740,000 labelled posts across five toxicity categories. This was considered sufficient for the intended multi-label classification task based on model performance during development.

### 2.6 Bias examination  `Art. 10(2)(f)`
not provided

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
Training data combines multiple public benchmarks and platform-collected samples from social media environments.

---

## Section 3 — Validation Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 3.1 Design choices  `Art. 10(2)(a)`
A held-out validation split was reserved from the internally annotated Twitter/X dataset prior to training.

### 3.2 Provenance  `Art. 10(2)(b)`
not provided

### 3.3 Preprocessing  `Art. 10(2)(c)`
not provided

### 3.4 Assumptions  `Art. 10(2)(d)`
not provided

### 3.5 Suitability  `Art. 10(2)(e)`
The validation split contains approximately 74,000 posts, used for hyperparameter selection and early stopping.

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
*(Annex IV §2 — development process; Article 10(2)–(4))*

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
System was evaluated against the ToxiGen benchmark and the HatEval 2019 test set as external validation of toxicity detection capability.

### 4.10 Representativeness  `Art. 10(3)`
not provided

### 4.11 Statistical properties  `Art. 10(3)`
not provided

### 4.12 Quality metrics  `Art. 10(3)`
not provided

### 4.13 Contextual characteristics  `Art. 10(4)`
not provided
