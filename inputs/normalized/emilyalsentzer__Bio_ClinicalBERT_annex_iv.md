# Annex IV Normalization — Article 10 Data Governance
<!-- Pure restructure of the raw model card into the Annex IV skeleton.
     RULES: move source text VERBATIM into the matching field.
     If the raw card says nothing relevant, write "not provided".
     Do NOT write "not addressed", "unclear", or any other judgment.
     Do NOT invent or paraphrase. Compliance verdicts are NOT part of this file. -->

## Document metadata
- **HuggingFace ID:** emilyalsentzer/Bio_ClinicalBERT
- **Source card file:** `raw/emilyalsentzer__Bio_ClinicalBERT.md`
- **Normalized by:** Claude (verbatim restructure)
- **Date normalized:** 2026-06-07

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** Bio_ClinicalBERT (Bio + Clinical BERT Model)
- **Intended purpose / task:** This model card describes the Bio+Clinical BERT model, which was initialized from BioBERT & trained on all MIMIC notes.
- **High-risk category (Annex III ref.):** not provided
- **Intended users / deployers:** not provided
- **Geographic / regulatory scope:** not provided

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
The Publicly Available Clinical BERT Embeddings paper contains four unique clinicalBERT models: initialized with BERT-Base (`cased_L-12_H-768_A-12`) or BioBERT (`BioBERT-Base v1.0 + PubMed 200K + PMC 270K`) & trained on either all MIMIC notes or only discharge summaries. This model card describes the Bio+Clinical BERT model, which was initialized from BioBERT & trained on all MIMIC notes. Model parameters were initialized with BioBERT (`BioBERT-Base v1.0 + PubMed 200K + PMC 270K`).

### 2.2 Provenance  `Art. 10(2)(b)`
The `Bio_ClinicalBERT` model was trained on all notes from MIMIC III, a database containing electronic health records from ICU patients at the Beth Israel Hospital in Boston, MA. All notes from the `NOTEEVENTS` table were included (~880M words).

### 2.3 Preprocessing  `Art. 10(2)(c)`
Each note in MIMIC was first split into sections using a rules-based section splitter (e.g. discharge summary notes were split into "History of Present Illness", "Family History", "Brief Hospital Course", etc. sections). Then each section was split into sentences using SciSpacy (`en core sci md` tokenizer).

### 2.4 Assumptions  `Art. 10(2)(d)`
not provided

### 2.5 Suitability  `Art. 10(2)(e)`
All notes from the `NOTEEVENTS` table were included (~880M words).

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
A database containing electronic health records from ICU patients at the Beth Israel Hospital in Boston, MA.

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
