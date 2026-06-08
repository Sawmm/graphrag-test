# Annex IV Normalization — Article 10 Data Governance
<!-- Pure restructure of the raw model card into the Annex IV skeleton.
     RULES: move source text VERBATIM into the matching field.
     If the raw card says nothing relevant, write "not provided".
     Do NOT write "not addressed", "unclear", or any other judgment.
     Do NOT invent or paraphrase. Compliance verdicts are NOT part of this file. -->

## Document metadata
- **HuggingFace ID:** microsoft/BiomedVLP-CXR-BERT-specialized
- **Source card file:** `raw/microsoft__BiomedVLP-CXR-BERT-specialized.md`
- **Normalized by:** Claude (verbatim restructure)
- **Date normalized:** 2026-06-07

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** CXR-BERT-specialized (BiomedVLP-CXR-BERT-specialized)
- **Intended purpose / task:** CXR-BERT is a chest X-ray (CXR) domain-specific language model that makes use of an improved vocabulary, novel pretraining procedure, weight regularization, and text augmentations. The resulting model demonstrates improved performance on radiology natural language inference, radiology masked language model token prediction, and downstream vision-language processing tasks such as zero-shot phrase grounding and image classification.
- **High-risk category (Annex III ref.):** not provided
- **Intended users / deployers:** This model is intended to be used solely for (I) future research on visual-language processing and (II) reproducibility of the experimental results reported in the reference paper. The primary intended use is to support AI researchers building on top of this work. CXR-BERT and its associated models should be helpful for exploring various clinical NLP & VLP research questions, especially in the radiology domain. Out-of-Scope Use: Any deployed use case of the model — commercial or otherwise — is currently out of scope. The models and evaluations are not intended for deployed use cases.
- **Geographic / regulatory scope:** not provided

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
First, we pretrain CXR-BERT-general from a randomly initialized BERT model via Masked Language Modeling (MLM) on abstracts PubMed and clinical notes from the publicly-available MIMIC-III and MIMIC-CXR. CXR-BERT-specialized is continually pretrained from CXR-BERT-general to further specialize in the chest X-ray domain. At the final stage, CXR-BERT is trained in a multi-modal contrastive learning framework, similar to the CLIP framework. CXR-BERT-specialized is jointly trained with a ResNet-50 image model in a multi-modal contrastive learning framework. Prior to multi-modal learning, the image model is pre-trained on the same set of images in MIMIC-CXR using SimCLR.

### 2.2 Provenance  `Art. 10(2)(b)`
This model builds upon existing publicly-available datasets: PubMed, MIMIC-III, MIMIC-CXR.

### 2.3 Preprocessing  `Art. 10(2)(c)`
Makes use of an improved vocabulary, novel pretraining procedure, weight regularization, and text augmentations.

### 2.4 Assumptions  `Art. 10(2)(d)`
not provided

### 2.5 Suitability  `Art. 10(2)(e)`
not provided

### 2.6 Bias examination  `Art. 10(2)(f)`
not provided

### 2.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 2.8 Data gaps  `Art. 10(2)(h)`
This model was developed using English corpora, and thus can be considered English-only.

### 2.9 Relevance  `Art. 10(3)`
not provided

### 2.10 Representativeness  `Art. 10(3)`
These datasets reflect a broad variety of sources ranging from biomedical abstracts to intensive care unit notes to chest X-ray radiology notes.

### 2.11 Statistical properties  `Art. 10(3)`
not provided

### 2.12 Quality metrics  `Art. 10(3)`
not provided

### 2.13 Contextual characteristics  `Art. 10(4)`
The radiology notes are accompanied with their associated chest x-ray DICOM images in MIMIC-CXR dataset; intensive care unit notes; chest X-ray radiology notes.

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
We demonstrate that this language model achieves state-of-the-art results in radiology natural language inference through its improved vocabulary and novel language pretraining objective leveraging semantics and discourse characteristics in radiology reports. Below is the zero-shot phrase grounding performance on the MS-CXR dataset, which evaluates the quality of image-text latent representations.

### 4.2 Provenance  `Art. 10(2)(b)`
RadNLI (MedNLI transfer); MS-CXR dataset (https://physionet.org/content/ms-cxr/0.1/).

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
|                                                 | RadNLI accuracy (MedNLI transfer) | Mask prediction accuracy | Avg. # tokens after tokenization | Vocabulary size |
| ----------------------------------------------- | :-------------------------------: | :----------------------: | :------------------------------: | :-------------: |
| RadNLI baseline                                 |               53.30               |            -             |                -                 |        -        |
| ClinicalBERT                                    |               47.67               |          39.84           |         78.98 (+38.15%)          |     28,996      |
| PubMedBERT                                      |               57.71               |          35.24           |         63.55 (+11.16%)          |     28,895      |
| CXR-BERT (after Phase-III)                      |               60.46               |          77.72           |          58.07 (+1.59%)          |     30,522      |
| **CXR-BERT (after Phase-III + Joint Training)** |             **65.21**             |        **81.58**         |        **58.07 (+1.59%)**        |     30,522      |

| Vision–Language Pretraining Method | Text Encoder | MS-CXR Phrase Grounding (Avg. CNR Score) |
| ---------------------------------- | ------------ | :--------------------------------------: |
| Baseline                           | ClinicalBERT |                  0.769                   |
| Baseline                           | PubMedBERT   |                  0.773                   |
| ConVIRT                            | ClinicalBERT |                  0.818                   |
| GLoRIA                             | ClinicalBERT |                  0.930                   |
| **BioViL**                         | **CXR-BERT** |                **1.027**                 |
| **BioViL-L**                       | **CXR-BERT** |                **1.142**                 |

### 4.13 Contextual characteristics  `Art. 10(4)`
not provided

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

- **Processes sensitive data for bias correction:** not provided
