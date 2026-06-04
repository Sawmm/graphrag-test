# Annex IV Normalization — Article 10 Data Governance
<!-- Copy this file to normalized/<model_id>_annex_iv.md and fill in each field.
     Leave a field blank if the source card contains no relevant information.
     Do NOT invent content — only restructure what is actually in the raw card. -->

## Document metadata
- **HuggingFace ID:** emilyalsentzer/Bio_ClinicalBERT
- **Source card file:** `raw/emilyalsentzer__Bio_ClinicalBERT.md`
- **Normalized by:** Claude
- **Date normalized:** 2026-05-17
- **Second annotator:**
- **Date second-annotated:**

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** Bio_ClinicalBERT (Bio + Clinical BERT Model)
- **Intended purpose / task:** Masked language model (fill-mask) for clinical and biomedical NLP tasks. Specifically, the Bio+Clinical BERT variant is initialized from BioBERT and trained on all MIMIC III clinical notes.
- **High-risk category (Annex III ref.):**  Annex III §5 — AI in medical devices / clinical NLP (implicit, given training on clinical EHR data from ICU patients)
- **Intended users / deployers:** NLP researchers and practitioners working in clinical and biomedical domains.
- **Geographic / regulatory scope:** Not explicitly addressed. Training data is from Beth Israel Deaconess Medical Center ICU (Boston, MA, USA).

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
> Why was this dataset chosen for this purpose? Selection criteria, intended coverage, scope.

The model was trained on all notes from MIMIC III, a database containing electronic health records from ICU patients at Beth Israel Deaconess Medical Center in Boston, MA. All notes from the NOTEEVENTS table were included (~880M words). The selection covers all note types rather than a subset (e.g., only discharge summaries), to maximize clinical language coverage. This variant is explicitly distinguished from a discharge-summary-only variant described in the same paper.

### 2.2 Provenance  `Art. 10(2)(b)`
> Origin of the data — where it came from, how collected, institutions involved, legal/consent basis.

Training data: MIMIC III (Medical Information Mart for Intensive Care III) database, containing electronic health records from ICU patients at Beth Israel Deaconess Medical Center, Boston, MA. Published in Nature Scientific Data (Goldberger et al.). Access to MIMIC requires credentialed access through PhysioNet. No further legal/consent information is provided in the model card beyond the MIMIC citation.

Model initialization: BioBERT (BioBERT-Base v1.0 + PubMed 200K + PMC 270K).

### 2.3 Preprocessing  `Art. 10(2)(c)`
> Cleaning, filtering, annotation, labelling, augmentation, and other transformations applied.

Two-step preprocessing is described:
1. Each MIMIC note was split into sections using a rules-based section splitter (e.g., discharge summary notes split into "History of Present Illness," "Family History," "Brief Hospital Course," etc.).
2. Each section was then split into sentences using SciSpacy (`en_core_sci_md` tokenizer).

No further filtering, annotation, or augmentation steps are described in the model card.

### 2.4 Assumptions  `Art. 10(2)(d)`
> What does the dataset claim to represent? Stated limitations of that representation.

The dataset is assumed to represent clinical language as used in ICU settings at a single US academic medical center (Beth Israel Deaconess Medical Center). No explicit statement of limitations (e.g., single-center, US-centric, ICU-specific) is made in the model card.

### 2.5 Suitability  `Art. 10(2)(e)`
> Size, coverage, and any explicit fitness-for-purpose assessment.

The dataset contains approximately 880 million words. All note types from the MIMIC NOTEEVENTS table are included. The card references the original paper (Publicly Available Clinical BERT Embeddings, NAACL 2019) for performance on NLI and NER tasks as implicit evidence of suitability, but no explicit fitness-for-purpose assessment is stated in the card.

### 2.6 Bias examination  `Art. 10(2)(f)`
> Protected attributes examined, methodology used, findings reported.

Not addressed in model card.

### 2.7 Bias mitigation  `Art. 10(2)(g)`
> Measures taken (resampling, re-weighting, etc.) — or documented decision not to mitigate.

Not addressed in model card.

### 2.8 Data gaps  `Art. 10(2)(h)`
> Known shortcomings, coverage gaps, how they were addressed or acknowledged.

Not addressed in model card. The model card does not discuss the single-center limitation, ICU-only population, or English-only coverage as data gaps.

### 2.9 Relevance  `Art. 10(3)`
> Fitness-for-purpose statement — why this dataset is appropriate for the intended task.

The training corpus (MIMIC III clinical notes) is directly relevant to clinical NLP tasks. Using clinical EHR text for pretraining a clinical language model is the stated rationale for the work. The card notes the model is intended to produce clinical BERT embeddings.

### 2.10 Representativeness  `Art. 10(3)`
> Subgroup coverage — demographic, geographic, clinical, or other relevant breakdowns.

Not addressed in model card. No demographic, geographic, or clinical subgroup breakdown of the MIMIC training notes is provided.

### 2.11 Statistical properties  `Art. 10(3)`
> Class distribution, variance, inter-class correlation, or other quantitative characteristics.

The training dataset contains approximately 880 million words from all note types in the MIMIC NOTEEVENTS table. No further breakdown by note type, department, or other category is provided.

### 2.12 Quality metrics  `Art. 10(3)`
> Completeness, error rates, annotation consistency, or other quality measures.

Not addressed in model card. No quality metrics for the MIMIC notes used in training are reported.

### 2.13 Contextual characteristics  `Art. 10(4)`
> Deployment environment — geographic scope, clinical setting, equipment, patient population.

The training data is from ICU patients at Beth Israel Deaconess Medical Center (Boston, MA, USA). The clinical context is ICU / in-patient care. No broader deployment contextual characteristics are described.

---

## Section 3 — Validation Dataset
*(same 13 fields as Section 2)*

### 3.1 Design choices  `Art. 10(2)(a)`
Not addressed in model card.

### 3.2 Provenance  `Art. 10(2)(b)`
Not addressed in model card.

### 3.3 Preprocessing  `Art. 10(2)(c)`
Not addressed in model card.

### 3.4 Assumptions  `Art. 10(2)(d)`
Not addressed in model card.

### 3.5 Suitability  `Art. 10(2)(e)`
Not addressed in model card.

### 3.6 Bias examination  `Art. 10(2)(f)`
Not addressed in model card.

### 3.7 Bias mitigation  `Art. 10(2)(g)`
Not addressed in model card.

### 3.8 Data gaps  `Art. 10(2)(h)`
Not addressed in model card.

### 3.9 Relevance  `Art. 10(3)`
Not addressed in model card.

### 3.10 Representativeness  `Art. 10(3)`
Not addressed in model card.

### 3.11 Statistical properties  `Art. 10(3)`
Not addressed in model card.

### 3.12 Quality metrics  `Art. 10(3)`
Not addressed in model card.

### 3.13 Contextual characteristics  `Art. 10(4)`
Not addressed in model card.

---

## Section 4 — Testing Dataset
*(same 13 fields; if no independent test set exists, mark all N/A and note why)*

The model card does not describe any test datasets. It refers readers to the original paper (Publicly Available Clinical BERT Embeddings, NAACL Clinical NLP Workshop 2019) for performance results on NLI and NER tasks. No benchmark names, scores, or evaluation details are included in the card itself.

### 4.1 Design choices  `Art. 10(2)(a)`
Not addressed in model card. (Referred to original paper.)

### 4.2 Provenance  `Art. 10(2)(b)`
Not addressed in model card. (Referred to original paper.)

### 4.3 Preprocessing  `Art. 10(2)(c)`
Not addressed in model card.

### 4.4 Assumptions  `Art. 10(2)(d)`
Not addressed in model card.

### 4.5 Suitability  `Art. 10(2)(e)`
Not addressed in model card.

### 4.6 Bias examination  `Art. 10(2)(f)`
Not addressed in model card.

### 4.7 Bias mitigation  `Art. 10(2)(g)`
Not addressed in model card.

### 4.8 Data gaps  `Art. 10(2)(h)`
Not addressed in model card.

### 4.9 Relevance  `Art. 10(3)`
Not addressed in model card.

### 4.10 Representativeness  `Art. 10(3)`
Not addressed in model card.

### 4.11 Statistical properties  `Art. 10(3)`
Not addressed in model card.

### 4.12 Quality metrics  `Art. 10(3)`
Not addressed in model card.

### 4.13 Contextual characteristics  `Art. 10(4)`
Not addressed in model card.

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

- **Processes sensitive data for bias correction:** `unclear`

*(The model is trained on MIMIC III electronic health records, which are sensitive personal health data. However, MIMIC is a de-identified dataset provided for research under credentialed access. The model card does not describe whether sensitive data processing was performed specifically for bias correction purposes. Given that training on EHR data inherently involves sensitive health information, the following fields capture what the card states.)*

### 5.1 Necessity
Not addressed in model card.

### 5.2 Security measures
Not addressed in model card. MIMIC access requires credentialed registration via PhysioNet, but this is a data access control rather than a technical safeguard described in the model card.

### 5.3 Access controls
Not addressed in model card. MIMIC III requires credentialed access through PhysioNet, but the model card does not describe access controls applied by the model developers.

### 5.4 Transfer prohibition
Not addressed in model card.

### 5.5 Deletion procedure
Not addressed in model card.

### 5.6 Processing record
Not addressed in model card. The card references the published paper and GitHub repository but does not document the legal basis for processing MIMIC data or any safeguards applied.

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
| design_choices | 10(2)(a) | satisfied | | |
| provenance | 10(2)(b) | satisfied | | |
| preprocessing | 10(2)(c) | satisfied | | |
| assumptions | 10(2)(d) | partial | | |
| suitability | 10(2)(e) | partial | | |
| bias_examination | 10(2)(f) | not_satisfied | | |
| bias_mitigation | 10(2)(g) | not_satisfied | | |
| data_gap | 10(2)(h) | not_satisfied | | |
| relevance | 10(3) | partial | | |
| representativeness | 10(3) | not_satisfied | | |
| statistical_props | 10(3) | partial | | |
| quality_metrics | 10(3) | not_satisfied | | |
| contextual_characteristics | 10(4) | partial | | |

**Training obligations satisfied (count):** 5.5 / 13 &nbsp;*(partial = 0.5)*

### Validation dataset obligations
| Obligation | §ref | Annotator 1 | Annotator 2 | Final |
|---|---|---|---|---|
| design_choices | 10(2)(a) | not_satisfied | | |
| provenance | 10(2)(b) | not_satisfied | | |
| preprocessing | 10(2)(c) | not_satisfied | | |
| assumptions | 10(2)(d) | not_satisfied | | |
| suitability | 10(2)(e) | not_satisfied | | |
| bias_examination | 10(2)(f) | not_satisfied | | |
| bias_mitigation | 10(2)(g) | not_satisfied | | |
| data_gap | 10(2)(h) | not_satisfied | | |
| relevance | 10(3) | not_satisfied | | |
| representativeness | 10(3) | not_satisfied | | |
| statistical_props | 10(3) | not_satisfied | | |
| quality_metrics | 10(3) | not_satisfied | | |
| contextual_characteristics | 10(4) | not_satisfied | | |

**Validation obligations satisfied (count):** 0 / 13

### Testing dataset obligations
| Obligation | §ref | Annotator 1 | Annotator 2 | Final |
|---|---|---|---|---|
| design_choices | 10(2)(a) | not_satisfied | | |
| provenance | 10(2)(b) | not_satisfied | | |
| preprocessing | 10(2)(c) | not_satisfied | | |
| assumptions | 10(2)(d) | not_satisfied | | |
| suitability | 10(2)(e) | not_satisfied | | |
| bias_examination | 10(2)(f) | not_satisfied | | |
| bias_mitigation | 10(2)(g) | not_satisfied | | |
| data_gap | 10(2)(h) | not_satisfied | | |
| relevance | 10(3) | not_satisfied | | |
| representativeness | 10(3) | not_satisfied | | |
| statistical_props | 10(3) | not_satisfied | | |
| quality_metrics | 10(3) | not_satisfied | | |
| contextual_characteristics | 10(4) | not_satisfied | | |

**Testing obligations satisfied (count):** 0 / 13 &nbsp;*(all evaluation details deferred to original paper; no test data described in the model card)*

### Overall verdict
- **Compliant:** `no`
  *(Training score = 5.5/13, below threshold of 10/13; Validation score = 0/13, far below threshold of 8/13)*
- **Annotator notes:** The model card provides good coverage of training data provenance and preprocessing (MIMIC III source, section-splitting, SciSpacy tokenization) but is almost entirely silent on bias, data quality, validation data, and testing data. Evaluation details are deferred entirely to the original 2019 NAACL paper. Given the sensitive nature of the training data (ICU EHRs), the absence of any discussion of privacy safeguards, data governance, or bias assessment is a notable gap relative to Article 10 obligations.
