# RadAssist v2.1 — Article 10 Compliant Data Governance Documentation

## Document metadata
- **System ID:** radassist-v2.1
- **Organisation:** MedTech Solutions BV, Amsterdam, Netherlands
- **System type:** High-risk AI system (EU AI Act Annex III, §5(a) — medical device)
- **Intended purpose:** Computer-aided detection and classification of pulmonary nodules in thoracic CT scans to support radiologist triage decisions.
- **Version:** 2.1.0
- **Date:** March 2026
- **Purpose:** Compliance verification test — verify pipeline reports COMPLIANT

---

## Section 1 — System Overview

- **System name and version:** RadAssist v2.1, version 2.1.0
- **Intended purpose / task:** Supervised deep learning system for detection and classification of pulmonary nodules (solid, sub-solid, ground-glass) in thoracic CT scans. Produces bounding box coordinates, nodule category labels, and a malignancy risk score (0–1). Decision-support tool; radiologist sign-off is required for all clinical decisions.
- **High-risk category (Annex III ref.):** Annex III §5(a) — AI systems intended to be used as safety components in medical devices or as medical devices themselves.
- **Intended users / deployers:** Radiologists and radiology departments in EU hospitals. Requires integration with PACS systems and radiologist oversight.
- **Geographic / regulatory scope:** EU deployment. Training data from 14 EU hospital radiology departments. Equipment: Siemens, Philips, and GE CT scanner models common in EU tertiary care.

---

## Section 2 — Training Dataset

### 2.1 Design choices  `Art. 10(2)(a)`

The training dataset was designed to cover all major pulmonary nodule categories (solid, sub-solid, part-solid, ground-glass) across a representative range of patient demographics including age groups (18–90), sex (male/female/non-binary), and body habitus. Coverage was deliberately extended to underrepresented populations following a pre-training bias audit (see §2.6). Selection criteria required (a) institutional provenance enabling data lineage traceability, (b) clinical relevance to the target pulmonary nodule detection task, (c) sufficient class diversity across nodule categories, and (d) patient-level separation from validation and test splits. Data collection was coordinated by the RadAssist Data Governance Committee (reference: DGC-2024-001).

### 2.2 Provenance  `Art. 10(2)(b)`

Training data was collected from 14 EU hospital radiology departments between January 2018 and December 2023 under data processing agreements compliant with GDPR Article 9 and EU AI Act Article 10. Each contributing institution provided institutional review board (IRB) approval. Scans are de-identified using the DICOM Anonymization standard (DICOM PS 3.15 Appendix E). Data collection was coordinated by the RadAssist Data Governance Committee (reference: DGC-2024-001).

### 2.3 Preprocessing  `Art. 10(2)(c)`

Raw DICOM files were converted to PNG using a fixed-window Hounsfield unit mapping (window centre −600 HU, window width 1500 HU). Slice thickness was normalised to 1.0 mm using linear interpolation. Ground-truth annotations were provided by three board-certified radiologists per scan, with Fleiss kappa inter-annotator agreement of κ = 0.81 (substantial agreement). Annotations underwent a two-stage quality review: automated outlier detection followed by radiologist arbitration for disagreements.

### 2.4 Assumptions  `Art. 10(2)(d)`

The dataset assumes that input scans are acquired on clinical-grade CT scanners (≥16-slice) with standard acquisition protocols. Scans from low-dose screening programs may show reduced sensitivity. Non-contrast scans are assumed as the default; contrast-enhanced scans are handled by a separate model branch. The dataset is assumed to represent clinical imaging conditions as produced in routine EU hospital settings. Key limitation: low-dose protocol coverage is insufficient for national screening programmes outside the Netherlands and Germany.

### 2.5 Suitability  `Art. 10(2)(e)`

The training dataset comprises 2,340,000 annotated CT slices from 87,000 distinct patients. Statistical power analysis (β = 0.8, α = 0.05) confirms this is sufficient for the intended classification task across all four nodule categories. Dataset sufficiency review documented in internal report TR-2024-008. Modality coverage spans all target nodule types and the full intended patient demographic range. Fitness-for-purpose assessment concluded the dataset is suitable for training a decision-support system within the specified intended use scope.

### 2.6 Bias examination  `Art. 10(2)(f)`

A pre-training bias audit was conducted across the following protected attributes: age group (18–40, 41–60, 61–80, 81+), sex, and ethnicity (8 categories). The audit identified a statistically significant underrepresentation of patients aged 81+ (2.1% of training data vs. an estimated 6.3% of the target EU deployment population) and patients of South Asian ethnicity (1.8% vs. estimated 4.1%). No bias was detected for sex-based categories. Bias audit report: BA-2024-003.

### 2.7 Bias mitigation  `Art. 10(2)(g)`

Two mitigation strategies were applied. First, class-conditional oversampling was used to increase representation of patients aged 81+ to 5% of the final training distribution. Second, importance re-weighting was applied during training with weights inversely proportional to class frequency for the underrepresented ethnicity categories. Post-mitigation audit confirmed AUC parity within 0.02 across all demographic groups. Mitigation documentation: BM-2024-007.

### 2.8 Data gaps  `Art. 10(2)(h)`

The primary identified gap is insufficient coverage of low-dose CT protocols used in national screening programmes outside the Netherlands and Germany. A secondary gap is limited coverage of paediatric patients (age < 18), who are explicitly excluded from the system's intended use scope. The low-dose protocol gap is partially addressed through synthetic data augmentation (Gaussian noise injection at σ ∈ [10, 30] HU). Full gap documentation: DG-2024-002.

### 2.9 Relevance  `Art. 10(3)`

The dataset directly represents the pathologies, patient populations, and imaging conditions targeted by RadAssist v2.1. All nodule categories in the intended use scope are represented. The dataset was validated against the LUNA16 public benchmark (sensitivity 0.93 at 1 FP/scan).

### 2.10 Representativeness  `Art. 10(3)`

Stratified sampling was applied across age group, sex, and diagnosis category. The training set distribution was compared against a population-level estimate of pulmonary nodule prevalence in the EU (Netherlands Cancer Institute, 2022 report). Chi-squared tests confirm no statistically significant deviation for any demographic category (p > 0.05 after mitigation).

### 2.11 Statistical properties  `Art. 10(3)`

Class distribution: solid nodules 61.2%, sub-solid 22.1%, ground-glass 10.4%, benign/calcified 6.3%. Inter-class correlation matrix and per-class variance statistics are documented in technical report TR-2024-008. Class imbalance was addressed during training via focal loss (γ = 2.0).

### 2.12 Quality metrics  `Art. 10(3)`

Post-annotation quality review confirmed an annotation error rate of 0.38% (disagreements not resolved after arbitration, excluded from training). Dataset completeness: 98.7% of slices passed all quality checks. Full quality metrics: QR-2024-004.

### 2.13 Contextual characteristics  `Art. 10(4)`

The training data originates from EU hospital radiology departments using standard clinical imaging workflows. Equipment spans Siemens, Philips, and GE CT scanner models common in EU tertiary care. All data is from the EU deployment context; non-EU clinical protocols are not represented.

---

## Section 3 — Validation Dataset

### 3.1 Design choices  `Art. 10(2)(a)`

A held-out validation split (10% of unique patients, stratified by age group and diagnosis category) was reserved prior to any model training. Patient-level splitting was used to prevent data leakage.

### 3.2 Provenance  `Art. 10(2)(b)`

The validation set originates from the same 14 contributing hospitals as the training data, using temporally separated scans from 2022–2023 only (not used in training).

### 3.3 Preprocessing  `Art. 10(2)(c)`

Identical preprocessing pipeline as the training set was applied independently to prevent preprocessing leakage.

### 3.4 Assumptions  `Art. 10(2)(d)`

The validation set is assumed to reflect the same clinical distribution as the training data, as it is drawn from the same institutions and time window.

### 3.5 Suitability  `Art. 10(2)(e)`

The validation dataset comprises 180,000 annotated CT slices from 8,700 patients, sufficient for stable hyperparameter tuning and architecture selection.

### 3.6 Bias examination  `Art. 10(2)(f)`

Bias profile across all protected attributes matches the training set post-mitigation; no additional biases were introduced by the validation split procedure. Kolmogorov-Smirnov test p > 0.1 for all demographic distributions.

### 3.7 Bias mitigation  `Art. 10(2)(g)`

The validation set inherits the same mitigation applied to the training data (class-conditional oversampling, importance re-weighting). No separate mitigation pipeline was applied to the validation set.

### 3.8 Data gaps  `Art. 10(2)(h)`

Same gaps as the training set apply. No additional gaps were introduced by the validation split.

### 3.9 Relevance  `Art. 10(3)`

Covers the same nodule pathology scope and demographic distribution as the training set.

### 3.10 Representativeness  `Art. 10(3)`

Macro-averaged F1 score of 0.91 across all nodule categories. Performance is consistent across demographic subgroups (AUC range: 0.91–0.94 across age × sex combinations).

### 3.11 Statistical properties  `Art. 10(3)`

Class distribution matches the training set within 2% tolerance for all categories. Full distribution statistics: TR-2024-008.

### 3.12 Quality metrics  `Art. 10(3)`

Annotation error rate: 0.31%; dataset completeness: 99.1%.

### 3.13 Contextual characteristics  `Art. 10(4)`

Same clinical context as the training set. All data originates from EU hospital environments.

---

## Section 4 — Testing Dataset

### 4.1 Design choices  `Art. 10(2)(a)`

An independent test set was constructed from three hospitals not contributing to training or validation (Amsterdam UMC, Charité Berlin, and Hôpital Lariboisière Paris), providing geographic and institutional independence from the training distribution.

### 4.2 Provenance  `Art. 10(2)(b)`

Data from three independent EU hospitals; separate IRB approvals are on file for each institution (IRB-AMC-2024-012, IRB-CHA-2024-008, IRB-LAR-2024-019). No overlap with training or validation institutions.

### 4.3 Preprocessing  `Art. 10(2)(c)`

The identical preprocessing pipeline was applied by a separate data engineer with no access to training data to prevent unconscious preprocessing leakage.

### 4.4 Assumptions  `Art. 10(2)(d)`

The test set is intended to represent unseen real-world deployment conditions, including variation in scanner manufacturer, acquisition protocol, and regional clinical practice.

### 4.5 Suitability  `Art. 10(2)(e)`

The test dataset comprises 45,000 annotated CT slices from 1,800 patients. Statistical power analysis confirms this is sufficient for detecting performance differences of ≥ 2% AUC at β = 0.8.

### 4.6 Bias examination  `Art. 10(2)(f)`

Bias profile independently verified by a third-party clinical data auditor. Across all demographic subgroups, AUC ≥ 0.92. Full bias verification report: TR-2024-008, Appendix C.

### 4.7 Bias mitigation  `Art. 10(2)(g)`

The test set is used for evaluation only; no bias mitigation techniques were applied to preserve benchmark integrity. This is a deliberate decision documented here and in TR-2024-008, Appendix C.

### 4.8 Data gaps  `Art. 10(2)(h)`

No additional gaps beyond those identified in the training set. The test set introduces regional protocol variation (Charité uses 0.6 mm slice thickness; Hôpital Lariboisière uses a distinct scout protocol) which is documented as an additional test condition rather than a gap.

### 4.9 Relevance  `Art. 10(3)`

Covers the same pathology scope as training and validation under independent acquisition conditions.

### 4.10 Representativeness  `Art. 10(3)`

System AUC on the test set: 0.944 (95% CI: 0.937–0.951). Performance is consistent across all demographic subgroups. Full evaluation: TR-2024-008.

### 4.11 Statistical properties  `Art. 10(3)`

Class distribution: solid 59.8%, sub-solid 23.4%, ground-glass 11.2%, benign/calcified 5.6%. Distribution and variance statistics: TR-2024-008.

### 4.12 Quality metrics  `Art. 10(3)`

Annotation error rate: 0.22%; dataset completeness: 99.5%.

### 4.13 Contextual characteristics  `Art. 10(4)`

Test data spans hospitals in the Netherlands, Germany, and France, capturing significant regional variation in acquisition protocol, scanner generation, and clinical workflow. This provides evidence of generalisation beyond the training distribution.

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

RadAssist v2.1 does not process special category personal data (as defined in GDPR Article 9) for the specific purpose of bias detection or correction. De-identified demographic metadata collected during annotation is used for stratified sampling and bias auditing but does not constitute special category processing under the relevant legal basis.

### 5.1 Security measures

Training conducted on isolated on-premises infrastructure with access restricted to the RadAssist development team. All datasets stored in encrypted storage with organisation-level access controls. De-identification pipeline validated against DICOM PS 3.15 Appendix E.

### 5.2 Access controls

Access to training datasets restricted to named team members under data use agreements with each contributing institution. Access logs maintained. No external sharing of raw training data.

---

## Compliance Annotation

### Training dataset obligations
| Obligation | §ref | Status |
|---|---|---|
| design_choices | 10(2)(a) | satisfied |
| provenance | 10(2)(b) | satisfied |
| preprocessing | 10(2)(c) | satisfied |
| assumptions | 10(2)(d) | satisfied |
| suitability | 10(2)(e) | satisfied |
| bias_examination | 10(2)(f) | satisfied |
| bias_mitigation | 10(2)(g) | satisfied |
| data_gaps | 10(2)(h) | satisfied |
| relevance | 10(3) | satisfied |
| representativeness | 10(3) | satisfied |
| statistical_props | 10(3) | satisfied |
| quality_metrics | 10(3) | satisfied |
| contextual_characteristics | 10(4) | satisfied |

**Training obligations satisfied (count):** 13 / 13

### Validation dataset obligations
| Obligation | §ref | Status |
|---|---|---|
| design_choices | 10(2)(a) | satisfied |
| provenance | 10(2)(b) | satisfied |
| preprocessing | 10(2)(c) | satisfied |
| assumptions | 10(2)(d) | satisfied |
| suitability | 10(2)(e) | satisfied |
| bias_examination | 10(2)(f) | satisfied |
| bias_mitigation | 10(2)(g) | satisfied |
| data_gaps | 10(2)(h) | satisfied |
| relevance | 10(3) | satisfied |
| representativeness | 10(3) | satisfied |
| statistical_props | 10(3) | satisfied |
| quality_metrics | 10(3) | satisfied |
| contextual_characteristics | 10(4) | satisfied |

**Validation obligations satisfied (count):** 13 / 13

### Testing dataset obligations
| Obligation | §ref | Status |
|---|---|---|
| design_choices | 10(2)(a) | satisfied |
| provenance | 10(2)(b) | satisfied |
| preprocessing | 10(2)(c) | satisfied |
| assumptions | 10(2)(d) | satisfied |
| suitability | 10(2)(e) | satisfied |
| bias_examination | 10(2)(f) | satisfied |
| bias_mitigation | 10(2)(g) | satisfied |
| data_gaps | 10(2)(h) | satisfied |
| relevance | 10(3) | satisfied |
| representativeness | 10(3) | satisfied |
| statistical_props | 10(3) | satisfied |
| quality_metrics | 10(3) | satisfied |
| contextual_characteristics | 10(4) | satisfied |

**Testing obligations satisfied (count):** 13 / 13

### Overall verdict
- **Expected compliance:** `yes`
  *(training 13/13, validation 13/13, testing 13/13 — all above thresholds)*
