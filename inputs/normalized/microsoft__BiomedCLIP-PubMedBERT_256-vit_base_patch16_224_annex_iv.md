# Annex IV Normalization — Article 10 Data Governance
<!-- Pure restructure of the raw model card into the Annex IV skeleton.
     RULES: move source text VERBATIM into the matching field.
     If the raw card says nothing relevant, write "not provided".
     Do NOT write "not addressed", "unclear", or any other judgment.
     Do NOT invent or paraphrase. Compliance verdicts are NOT part of this file. -->

## Document metadata
- **HuggingFace ID:** microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224
- **Source card file:** `raw/microsoft__BiomedCLIP-PubMedBERT_256-vit_base_patch16_224.md`
- **Normalized by:** Claude (verbatim restructure)
- **Date normalized:** 2026-06-07

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** BiomedCLIP-PubMedBERT_256-vit_base_patch16_224
- **Intended purpose / task:** BiomedCLIP is a biomedical vision-language foundation model that is pretrained on PMC-15M, a dataset of 15 million figure-caption pairs extracted from biomedical research articles in PubMed Central, using contrastive learning. It uses PubMedBERT as the text encoder and Vision Transformer as the image encoder, with domain-specific adaptations. It can perform various vision-language processing (VLP) tasks such as cross-modal retrieval, image classification, and visual question answering.
- **High-risk category (Annex III ref.):** not provided
- **Intended users / deployers:** This model is intended to be used solely for (I) future research on visual-language processing and (II) reproducibility of the experimental results reported in the reference paper. The primary intended use is to support AI researchers building on top of this work. BiomedCLIP and its associated models should be helpful for exploring various biomedical VLP research questions, especially in the radiology domain. Out-of-Scope Use: Any deployed use case of the model — commercial or otherwise — is currently out of scope. The models and evaluations are not intended for deployed use cases.
- **Geographic / regulatory scope:** not provided

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
BiomedCLIP is pretrained on PMC-15M using contrastive learning. It uses PubMedBERT as the text encoder and Vision Transformer as the image encoder, with domain-specific adaptations.

### 2.2 Provenance  `Art. 10(2)(b)`
PMC-15M, a dataset of 15 million figure-caption pairs extracted from biomedical research articles in PubMed Central. We have released BiomedCLIP Data Pipeline (https://github.com/microsoft/BiomedCLIP_data_pipeline), which automatically downloads and processes a set of articles from the PubMed Central Open Access dataset.

### 2.3 Preprocessing  `Art. 10(2)(c)`
The BiomedCLIP Data Pipeline automatically downloads and processes a set of articles from the PubMed Central Open Access dataset.

### 2.4 Assumptions  `Art. 10(2)(d)`
not provided

### 2.5 Suitability  `Art. 10(2)(e)`
It contains 15 million figure-caption pairs extracted from biomedical research articles in PubMed Central.

### 2.6 Bias examination  `Art. 10(2)(f)`
not provided

### 2.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 2.8 Data gaps  `Art. 10(2)(h)`
This model was developed using English corpora, and thus can be considered English-only.

### 2.9 Relevance  `Art. 10(3)`
not provided

### 2.10 Representativeness  `Art. 10(3)`
Covers a diverse range of biomedical image types, such as microscopy, radiography, histology, and more.

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
Although we evaluated the models using a broad set of publicly-available research benchmarks, the models and evaluations are not intended for deployed use cases. BiomedCLIP establishes new state of the art in a wide range of standard datasets.

### 4.2 Provenance  `Art. 10(2)(b)`
A broad set of publicly-available research benchmarks.

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
BiomedCLIP establishes new state of the art in a wide range of standard datasets, and substantially outperforms prior VLP approaches.

### 4.13 Contextual characteristics  `Art. 10(4)`
not provided

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

- **Processes sensitive data for bias correction:** not provided
