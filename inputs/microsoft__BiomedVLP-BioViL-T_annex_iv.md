# Annex IV Normalization — Article 10 Data Governance
<!-- Copy this file to normalized/<model_id>_annex_iv.md and fill in each field.
     Leave a field blank if the source card contains no relevant information.
     Do NOT invent content — only restructure what is actually in the raw card. -->

## Document metadata
- **HuggingFace ID:** microsoft/BiomedVLP-BioViL-T
- **Source card file:** `raw/microsoft__BiomedVLP-BioViL-T.md`
- **Normalized by:** Claude
- **Date normalized:** 2026-05-17
- **Second annotator:**
- **Date second-annotated:**

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** BioViL-T (microsoft/BiomedVLP-BioViL-T)
- **Intended purpose / task:** Domain-specific vision-language model for analyzing chest X-rays (CXRs) and radiology reports. Supports natural language inference, phrase-grounding, image/text classification, and language decoding. Designed for both single- and multi-image downstream applications using temporal structure between data points. Intended solely for (I) future research on visual-language processing and (II) reproducibility of experimental results reported in the reference paper.
- **High-risk category (Annex III ref.):** Potentially Annex III §5 — AI in medical devices / safety components of medical devices, though the card explicitly states the model is not intended for deployed use or automated diagnosis.
- **Intended users / deployers:** AI researchers building on top of this work; researchers in clinical NLP and VLP, especially in the radiology domain.
- **Geographic / regulatory scope:** Not addressed in model card. Model trained on English corpora; data sourced from US-based repositories (PhysioNet/MIMIC).

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
> Why was this dataset chosen for this purpose? Selection criteria, intended coverage, scope.

Three publicly available datasets were used: PubMed abstracts (biomedical literature), MIMIC-III clinical notes (ICU clinical notes), and MIMIC-CXR (radiology reports accompanied by chest X-ray DICOM images). These were selected to cover a broad variety of sources ranging from biomedical abstracts to intensive care unit notes to chest X-ray radiology notes. The same training dataset as the predecessor model BioViL was used; BioViL-T extends it with a temporal multi-modal pre-training procedure. MIMIC-CXR was specifically chosen because it contains paired sequential CXR images and radiology reports enabling temporal learning.

### 2.2 Provenance  `Art. 10(2)(b)`
> Origin of the data — where it came from, how collected, institutions involved, legal/consent basis.

- **PubMed:** publicly available biomedical literature abstracts from the National Library of Medicine (https://pubmed.ncbi.nlm.nih.gov/).
- **MIMIC-III:** publicly available de-identified ICU clinical notes from PhysioNet (https://physionet.org/content/mimiciii/1.4/), sourced from Beth Israel Deaconess Medical Center.
- **MIMIC-CXR:** publicly available de-identified chest X-ray images and radiology reports from PhysioNet (https://physionet.org/content/mimic-cxr/), sourced from Beth Israel Deaconess Medical Center.

Legal/consent basis, IRB approvals, and data use agreement details are not described in the model card beyond characterizing the datasets as "publicly-available."

### 2.3 Preprocessing  `Art. 10(2)(c)`
> Cleaning, filtering, annotation, labelling, augmentation, and other transformations applied.

Training is described as a two-stage procedure: (1) CXR-BERT-general is pretrained from a randomly initialized BERT model via Masked Language Modeling (MLM) on PubMed abstracts, MIMIC-III clinical notes, and MIMIC-CXR radiology reports; (2) BioViL-T is continually pretrained from CXR-BERT-general using a multi-modal pre-training procedure utilizing radiology reports and sequences of chest X-rays. The [CLS] token's latent representation is used to align text and image embeddings. No further detail on data cleaning, filtering, tokenization beyond standard BERT-style processing, or image preprocessing is provided in the model card.

### 2.4 Assumptions  `Art. 10(2)(d)`
> What does the dataset claim to represent? Stated limitations of that representation.

The datasets are stated to "reflect a broad variety of sources ranging from biomedical abstracts to intensive care unit notes to chest X-ray radiology notes." The model card acknowledges that the training dataset contains only medical images and reports acquired from an ICU, where longitudinal images are often collected within a range of hours or at most a few days. No further representational assumptions (e.g. patient demographics, geographic distribution, equipment type) are stated.

### 2.5 Suitability  `Art. 10(2)(e)`
> Size, coverage, and any explicit fitness-for-purpose assessment.

The card does not state the size (number of samples) of any training split. Coverage is described qualitatively as ranging from biomedical abstracts to ICU notes to CXR reports with paired DICOM images. No explicit fitness-for-purpose assessment is provided beyond noting state-of-the-art benchmark results.

### 2.6 Bias examination  `Art. 10(2)(f)`
> Protected attributes examined, methodology used, findings reported.

Not addressed in model card.

### 2.7 Bias mitigation  `Art. 10(2)(g)`
> Measures taken (resampling, re-weighting, etc.) — or documented decision not to mitigate.

Not addressed in model card.

### 2.8 Data gaps  `Art. 10(2)(h)`
> Known shortcomings, coverage gaps, how they were addressed or acknowledged.

The model card notes the following limitations relevant to training data gaps: (1) the model was developed using English corpora only and can be considered English-only; (2) the training dataset contains only ICU-acquired images and reports, where longitudinal images are collected within hours or at most a few days, so the model may show reduced performance for consecutive images acquired over longer periods (e.g. years) where significant anatomical variations occur. No other data gaps are addressed.

### 2.9 Relevance  `Art. 10(3)`
> Fitness-for-purpose statement — why this dataset is appropriate for the intended task.

The card implicitly argues relevance by noting that MIMIC-CXR contains paired chest X-ray DICOM images and radiology reports, and that the multi-modal training procedure exploits temporal structure between sequential CXRs. PubMed and MIMIC-III are used in the first pretraining stage to build a general biomedical language model that is then adapted for the CXR domain. No explicit fitness-for-purpose statement is provided.

### 2.10 Representativeness  `Art. 10(3)`
> Subgroup coverage — demographic, geographic, clinical, or other relevant breakdowns.

Not addressed in model card. No demographic, geographic, or subgroup breakdown of the training data is provided.

### 2.11 Statistical properties  `Art. 10(3)`
> Class distribution, variance, inter-class correlation, or other quantitative characteristics.

Not addressed in model card. No quantitative statistics (dataset size, class distribution, etc.) are reported for the training data.

### 2.12 Quality metrics  `Art. 10(3)`
> Completeness, error rates, annotation consistency, or other quality measures.

Not addressed in model card.

### 2.13 Contextual characteristics  `Art. 10(4)`
> Deployment environment — geographic scope, clinical setting, equipment, patient population.

The training data is sourced from an ICU setting at Beth Israel Deaconess Medical Center (via MIMIC). The model card notes the data reflects longitudinal CXR sequences acquired over hours to days within an ICU context. No information is provided about the imaging equipment, patient demographics, or broader geographic/clinical deployment context.

---

## Section 3 — Validation Dataset
*(same 13 fields as Section 2)*

### 3.1 Design choices  `Art. 10(2)(a)`
The model card does not describe a dedicated validation split. Performance is reported on external benchmarks: RadNLI (static radiology NLI), MS-CXR-T (temporal semantics benchmark), and MS-CXR (phrase grounding benchmark, https://physionet.org/content/ms-cxr/0.1/). These benchmarks are described as publicly available research benchmarks used to evaluate the quality of text embeddings and image-text representations.

### 3.2 Provenance  `Art. 10(2)(b)`
MS-CXR is hosted on PhysioNet (https://physionet.org/content/ms-cxr/0.1/). RadNLI and MS-CXR-T are referenced by name. No further provenance detail (origin institution, collection method, consent basis) is provided in the model card.

### 3.3 Preprocessing  `Art. 10(2)(c)`
Not addressed in model card.

### 3.4 Assumptions  `Art. 10(2)(d)`
Not addressed in model card. The benchmarks are used as-is without discussion of what populations or conditions they represent.

### 3.5 Suitability  `Art. 10(2)(e)`
The model card states that BioViL-T is benchmarked against "other commonly used SOTA domain specific BERT models" and that RadNLI and MS-CXR-T "measure the quality of text embeddings in terms of static and temporal semantics respectively," and that MS-CXR "evaluates the quality of image-text latent representations." This implies the benchmarks are considered suitable for the evaluation task but no formal suitability assessment is provided.

### 3.6 Bias examination  `Art. 10(2)(f)`
Not addressed in model card.

### 3.7 Bias mitigation  `Art. 10(2)(g)`
Not addressed in model card.

### 3.8 Data gaps  `Art. 10(2)(h)`
Not addressed in model card.

### 3.9 Relevance  `Art. 10(3)`
The benchmarks (RadNLI, MS-CXR-T, MS-CXR) are described as measuring the specific capabilities of the model — static semantic quality, temporal semantic sensitivity, and phrase-grounding in the CXR domain — which aligns with the model's intended purpose. No formal relevance statement is provided.

### 3.10 Representativeness  `Art. 10(3)`
Not addressed in model card.

### 3.11 Statistical properties  `Art. 10(3)`
Not addressed in model card. No size or distributional statistics are provided for the benchmark datasets.

### 3.12 Quality metrics  `Art. 10(3)`
Not addressed in model card.

### 3.13 Contextual characteristics  `Art. 10(4)`
Not addressed in model card.

---

## Section 4 — Testing Dataset
*(same 13 fields; if no independent test set exists, mark all N/A and note why)*

### 4.1 Design choices  `Art. 10(2)(a)`
The model card reports test-set performance on RadNLI (2-class: Accuracy 90.52%, ROC-AUC 0.947), MS-CXR-T (Accuracy 87.77%, ROC-AUC 0.933), and MS-CXR phrase grounding (Avg. CNR Score 1.33 ± 0.04, mIoU 0.240 ± 0.005). These are described as publicly-available research benchmarks. It is unclear from the card whether these benchmarks constitute test splits distinct from any development/validation splits; the card does not distinguish between validation and test usage.

### 4.2 Provenance  `Art. 10(2)(b)`
Same as Section 3.2. MS-CXR is hosted on PhysioNet; RadNLI and MS-CXR-T are referenced by name only.

### 4.3 Preprocessing  `Art. 10(2)(c)`
Not addressed in model card.

### 4.4 Assumptions  `Art. 10(2)(d)`
Not addressed in model card.

### 4.5 Suitability  `Art. 10(2)(e)`
The card implies suitability through benchmark selection — RadNLI for static NLI quality, MS-CXR-T for temporal semantics, and MS-CXR for vision-language grounding. No formal assessment is provided.

### 4.6 Bias examination  `Art. 10(2)(f)`
Not addressed in model card.

### 4.7 Bias mitigation  `Art. 10(2)(g)`
Not addressed in model card.

### 4.8 Data gaps  `Art. 10(2)(h)`
Not addressed in model card.

### 4.9 Relevance  `Art. 10(3)`
Not addressed in model card beyond implicit relevance through benchmark naming.

### 4.10 Representativeness  `Art. 10(3)`
Not addressed in model card.

### 4.11 Statistical properties  `Art. 10(3)`
Performance metrics are reported: MS-CXR-T Accuracy 87.77%, ROC-AUC 0.933; RadNLI (2 classes) Accuracy 90.52%, ROC-AUC 0.947; MS-CXR Phrase Grounding Avg. CNR 1.33 ± 0.04, mIoU 0.240 ± 0.005. Dataset size and class distribution statistics are not reported.

### 4.12 Quality metrics  `Art. 10(3)`
Not addressed in model card.

### 4.13 Contextual characteristics  `Art. 10(4)`
Not addressed in model card.

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

- **Processes sensitive data for bias correction:** `unclear`

The model trains on MIMIC-III and MIMIC-CXR, which contain de-identified patient records and medical images (sensitive health data). The card describes these as "publicly-available" but provides no information about whether sensitive data was processed specifically for bias correction purposes or what safeguards govern its use beyond the datasets' own access requirements.

### 5.1 Necessity
Not addressed in model card.

### 5.2 Security measures
Not addressed in model card. The underlying datasets (MIMIC-III, MIMIC-CXR) are de-identified as part of their PhysioNet distribution, but the model card does not describe any additional technical safeguards applied during model training.

### 5.3 Access controls
Not addressed in model card.

### 5.4 Transfer prohibition
Not addressed in model card.

### 5.5 Deletion procedure
Not addressed in model card.

### 5.6 Processing record
Not addressed in model card.

---

## Compliance Annotation
<!-- Fill in AFTER completing all sections above.
     satisfied     = information is present and substantively addresses the obligation
     partial       = information is present but vague, incomplete, or implicit
     not_satisfied = obligation is not addressed at all
     N/A           = genuinely not applicable (e.g. no independent test set) -->

### Training dataset obligations
| Obligation | §ref | Annotator 1 | Annotator 2 | Final |
|---|---|---|---|---|
| design_choices | 10(2)(a) | partial | | |
| provenance | 10(2)(b) | partial | | |
| preprocessing | 10(2)(c) | partial | | |
| assumptions | 10(2)(d) | partial | | |
| suitability | 10(2)(e) | not_satisfied | | |
| bias_examination | 10(2)(f) | not_satisfied | | |
| bias_mitigation | 10(2)(g) | not_satisfied | | |
| data_gap | 10(2)(h) | partial | | |
| relevance | 10(3) | partial | | |
| representativeness | 10(3) | not_satisfied | | |
| statistical_props | 10(3) | not_satisfied | | |
| quality_metrics | 10(3) | not_satisfied | | |
| contextual_characteristics | 10(4) | partial | | |

**Training obligations satisfied (count):** 3.5 / 13 &nbsp;*(partial = 0.5)*

### Validation dataset obligations
| Obligation | §ref | Annotator 1 | Annotator 2 | Final |
|---|---|---|---|---|
| design_choices | 10(2)(a) | partial | | |
| provenance | 10(2)(b) | partial | | |
| preprocessing | 10(2)(c) | not_satisfied | | |
| assumptions | 10(2)(d) | not_satisfied | | |
| suitability | 10(2)(e) | partial | | |
| bias_examination | 10(2)(f) | not_satisfied | | |
| bias_mitigation | 10(2)(g) | not_satisfied | | |
| data_gap | 10(2)(h) | not_satisfied | | |
| relevance | 10(3) | partial | | |
| representativeness | 10(3) | not_satisfied | | |
| statistical_props | 10(3) | not_satisfied | | |
| quality_metrics | 10(3) | not_satisfied | | |
| contextual_characteristics | 10(4) | not_satisfied | | |

**Validation obligations satisfied (count):** 2.0 / 13

### Testing dataset obligations
| Obligation | §ref | Annotator 1 | Annotator 2 | Final |
|---|---|---|---|---|
| design_choices | 10(2)(a) | partial | | |
| provenance | 10(2)(b) | partial | | |
| preprocessing | 10(2)(c) | not_satisfied | | |
| assumptions | 10(2)(d) | not_satisfied | | |
| suitability | 10(2)(e) | partial | | |
| bias_examination | 10(2)(f) | not_satisfied | | |
| bias_mitigation | 10(2)(g) | not_satisfied | | |
| data_gap | 10(2)(h) | not_satisfied | | |
| relevance | 10(3) | not_satisfied | | |
| representativeness | 10(3) | not_satisfied | | |
| statistical_props | 10(3) | partial | | |
| quality_metrics | 10(3) | not_satisfied | | |
| contextual_characteristics | 10(4) | not_satisfied | | |

**Testing obligations satisfied (count):** 2.0 / 13

### Overall verdict
- **Compliant:** `no`
  *(yes = training ≥ 10/13 AND validation ≥ 8/13; partial counts as 0.5)*
- **Annotator notes:** Training score is 3.5/13 (threshold: 10/13); validation score is 2.0/13 (threshold: 8/13). Both thresholds are not met. The card provides only minimal dataset provenance (dataset names and links) and acknowledges two data limitations (English-only, ICU temporal range), but does not address bias examination, bias mitigation, subgroup representativeness, statistical properties, quality metrics, or explicit suitability assessments for any data split.
