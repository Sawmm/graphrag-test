# Annex IV Normalization — Article 10 Data Governance
<!-- Pure restructure of the raw model card into the Annex IV skeleton.
     RULES: move source text VERBATIM into the matching field.
     If the raw card says nothing relevant, write "not provided".
     Do NOT write "not addressed", "unclear", or any other judgment.
     Do NOT invent or paraphrase. Compliance verdicts are NOT part of this file. -->

## Document metadata
- **HuggingFace ID:** microsoft/BiomedVLP-BioViL-T
- **Source card file:** `raw/microsoft__BiomedVLP-BioViL-T.md`
- **Normalized by:** Claude (verbatim restructure)
- **Date normalized:** 2026-06-07

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** BioViL-T (BiomedVLP-BioViL-T)
- **Intended purpose / task:** BioViL-T is a domain-specific vision-language model designed to analyze chest X-rays (CXRs) and radiology reports. It was trained using a temporal multi-modal pre-training procedure, which distinguishes it from its predecessor model (BioViL). The canonical model can be adapted to both single- and multi-image downstream applications including: natural language inference, phrase-grounding, image/text classification, and language decoding.
- **High-risk category (Annex III ref.):** not provided
- **Intended users / deployers:** This model is intended to be used solely for (I) future research on visual-language processing and (II) reproducibility of the experimental results reported in the reference paper. The primary intended use is to support AI researchers building on top of this work. Out-of-Scope Use: Any deployed use case of the model — commercial or otherwise — is currently out of scope. Under unprecedented conditions, the models may make inaccurate predictions and display limitations, which may require additional mitigation strategies. Therefore, we discourage use of the model for automated diagnosis or in a medical device.
- **Geographic / regulatory scope:** not provided

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
It was trained using a temporal multi-modal pre-training procedure. BioViL-T takes advantage of the temporal structure between data points, while using the same training dataset as its predecessor. The corresponding BERT language model is trained in two stages: First, we pretrain CXR-BERT-general from a randomly initialized BERT model via Masked Language Modeling (MLM) on PubMed abstracts and clinical notes from the publicly-available MIMIC-III and MIMIC-CXR. In the second stage, BioViL-T is continually pretrained from CXR-BERT-general using a multi-modal pre-training procedure by utilising radiology reports and sequences of chest X-rays.

### 2.2 Provenance  `Art. 10(2)(b)`
This model builds upon existing publicly-available datasets: PubMed, MIMIC-III, MIMIC-CXR.

### 2.3 Preprocessing  `Art. 10(2)(c)`
not provided

### 2.4 Assumptions  `Art. 10(2)(d)`
not provided

### 2.5 Suitability  `Art. 10(2)(e)`
not provided

### 2.6 Bias examination  `Art. 10(2)(f)`
not provided

### 2.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 2.8 Data gaps  `Art. 10(2)(h)`
This model was developed using English corpora, and thus can be considered English-only. As a result, the models may show reduced performance in analyzing consecutive images acquired over longer periods of time (e.g. years) where significant anatomical variations are observed between the scans.

### 2.9 Relevance  `Art. 10(3)`
not provided

### 2.10 Representativeness  `Art. 10(3)`
These datasets reflect a broad variety of sources ranging from biomedical abstracts to intensive care unit notes to chest X-ray radiology notes.

### 2.11 Statistical properties  `Art. 10(3)`
not provided

### 2.12 Quality metrics  `Art. 10(3)`
not provided

### 2.13 Contextual characteristics  `Art. 10(4)`
The radiology notes are accompanied with their associated chest x-ray DICOM images in MIMIC-CXR dataset. The training dataset contains only medical images and reports acquired from an intensive-care-unit (ICU), where longitudinal images are often collected within range of hours or at most few days.

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
The experiments were performed on the RadNLI and MS-CXR-T benchmarks, which measure the quality of text embeddings in terms of static and temporal semantics respectively. BioViL-T is benchmarked against other commonly used SOTA domain specific BERT models, including PubMedBERT and CXR-BERT. Below is the zero-shot phrase grounding performance obtained on the MS-CXR benchmark dataset, which evaluates the quality of image-text latent representations.

### 4.2 Provenance  `Art. 10(2)(b)`
RadNLI; MS-CXR-T; MS-CXR (https://physionet.org/content/ms-cxr/0.1/).

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
The presented model achieves state-of-the-art results in radiology natural language inference. The results below show that BioViL-T has increased sensitivity of sentence embeddings to temporal content (MS-CXR-T) whilst better capturing the static content (RadNLI).

|                       | MS-CXR-T Accuracy | MS-CXR-T ROC-AUC | RadNLI (2 classes) Accuracy | RadNLI (2 classes) ROC-AUC |
| --------------------- | :---------------: | :--------------: | :-------------------------: | :------------------------: |
| PubMedBERT            |       60.39       |       .542       |            81.38            |            .727            |
| CXR-BERT-General      |       62.60       |       .601       |            87.59            |            .902            |
| CXR-BERT-Specialized  |       78.12       |       .837       |            89.66            |            .932            |
| **BioViL-T**          |     **87.77**     |     **.933**     |          **90.52**          |          **.947**          |

| Vision–Language Pretraining Method | MS-CXR Phrase Grounding (Avg. CNR Score) | MS-CXR Phrase Grounding (mIoU) |
| ---------------------------------- | :--------------------------------------: | :----------------------------: |
| BioViL                             |              1.07 +- 0.04                |        0.229 +- 0.005          |
| BioViL-L                           |              1.21 +- 0.05                |        0.202 +- 0.010          |
| **BioViL-T**                       |            **1.33 +- 0.04**              |      **0.240 +- 0.005**        |

### 4.13 Contextual characteristics  `Art. 10(4)`
not provided

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

- **Processes sensitive data for bias correction:** not provided
