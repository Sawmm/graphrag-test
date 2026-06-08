# Annex IV Normalization — Article 10 Data Governance
<!-- Pure restructure of the raw model card into the Annex IV skeleton.
     RULES: move source text VERBATIM into the matching field.
     If the raw card says nothing relevant, write "not provided".
     Do NOT write "not addressed", "unclear", or any other judgment.
     Do NOT invent or paraphrase. Compliance verdicts are NOT part of this file. -->

## Document metadata
- **HuggingFace ID:** allenai/biomed_roberta_base
- **Source card file:** `raw/allenai__biomed_roberta_base.md`
- **Normalized by:** Claude (verbatim restructure)
- **Date normalized:** 2026-06-07

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** BioMed-RoBERTa-base
- **Intended purpose / task:** BioMed-RoBERTa-base is a language model based on the RoBERTa-base (Liu et. al, 2019) architecture. We adapt RoBERTa-base to 2.68 million scientific papers from the Semantic Scholar corpus via continued pretraining.
- **High-risk category (Annex III ref.):** not provided
- **Intended users / deployers:** not provided
- **Geographic / regulatory scope:** not provided

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
We adapt RoBERTa-base to 2.68 million scientific papers from the Semantic Scholar corpus via continued pretraining. We use the full text of the papers in training, not just abstracts.

### 2.2 Provenance  `Art. 10(2)(b)`
2.68 million scientific papers from the [Semantic Scholar](https://www.semanticscholar.org) corpus.

### 2.3 Preprocessing  `Art. 10(2)(c)`
Specific details of the adaptive pretraining procedure can be found in Gururangan et. al, 2020.

### 2.4 Assumptions  `Art. 10(2)(d)`
not provided

### 2.5 Suitability  `Art. 10(2)(e)`
This amounts to 7.55B tokens and 47GB of data.

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
BioMed-RoBERTa achieves competitive performance to state of the art models on a number of NLP tasks in the biomedical domain.

| Task         | Task Type           | RoBERTa-base | BioMed-RoBERTa-base |
|--------------|---------------------|--------------|---------------------|
| RCT-180K     | Text Classification | 86.4 (0.3)   | 86.9 (0.2)          |
| ChemProt     | Relation Extraction | 81.1 (1.1)   | 83.0 (0.7)          |
| JNLPBA       | NER                 | 74.3 (0.2)   | 75.2 (0.1)          |
| BC5CDR       | NER                 | 85.6 (0.1)   | 87.8 (0.1)          |
| NCBI-Disease | NER                 | 86.6 (0.3)   | 87.1 (0.8)          |

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
More evaluations TBD.

### 4.9 Relevance  `Art. 10(3)`
not provided

### 4.10 Representativeness  `Art. 10(3)`
not provided

### 4.11 Statistical properties  `Art. 10(3)`
Numbers are mean (standard deviation) over 3+ random seeds.

### 4.12 Quality metrics  `Art. 10(3)`
not provided

### 4.13 Contextual characteristics  `Art. 10(4)`
not provided

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

- **Processes sensitive data for bias correction:** not provided
