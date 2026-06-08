# Model Card — RadAssist v2.1
## Medical Imaging AI System

**Organisation:** MedTech Solutions BV, Amsterdam, Netherlands
**System type:** High-risk AI system (EU AI Act Annex III, §5(a) — medical device)
**Intended purpose:** Computer-aided detection and classification of pulmonary nodules in thoracic CT scans to support radiologist triage decisions.
**Version:** 2.1.0
**Date:** March 2026

---

## 1. System Overview

RadAssist v2.1 is a supervised deep learning system trained to detect and classify pulmonary nodules (solid, sub-solid, and ground-glass) in thoracic CT scans. The system produces bounding box coordinates, nodule category labels, and a malignancy risk score (0–1). It is intended as a decision-support tool; radiologist sign-off is required for all clinical decisions.

The system uses supervised training techniques including convolutional neural networks trained on labelled CT scan data. It does not process sensitive personal data for the specific purpose of bias correction; standard demographic data is collected during annotation but is not used as a training signal.

---

## 2. Training Dataset

### Design choices
The training dataset was designed to cover all major pulmonary nodule categories (solid, sub-solid, part-solid, ground-glass) across a representative range of patient demographics including age groups (18–90), sex (male/female/non-binary), and body habitus. Coverage was deliberately extended to underrepresented populations following a pre-training bias audit (see §2.6).

### Provenance and data collection
Training data was collected from 14 EU hospital radiology departments between January 2018 and December 2023 under data processing agreements compliant with GDPR Article 9 and EU AI Act Article 10. Each contributing institution provided institutional review board (IRB) approval. Scans are de-identified using the DICOM Anonymization standard (DICOM PS 3.15 Appendix E). Data collection was coordinated by the RadAssist Data Governance Committee (reference: DGC-2024-001).

### Data preparation and preprocessing
Raw DICOM files were converted to PNG using a fixed-window Hounsfield unit mapping (window centre −600 HU, window width 1500 HU). Slice thickness was normalised to 1.0 mm using linear interpolation. Ground-truth annotations were provided by three board-certified radiologists per scan, with Fleiss kappa inter-annotator agreement of κ = 0.81 (substantial agreement). Annotations underwent a two-stage quality review: automated outlier detection followed by radiologist arbitration for disagreements.

### Assumptions
The dataset assumes that input scans are acquired on clinical-grade CT scanners (≥16-slice) with standard acquisition protocols. Scans from low-dose screening programs may show reduced sensitivity. Non-contrast scans are assumed as the default; contrast-enhanced scans are handled by a separate model branch.

### Suitability assessment
The training dataset comprises 2,340,000 annotated CT slices from 87,000 distinct patients. Statistical power analysis (β = 0.8, α = 0.05) confirms this is sufficient for the intended classification task. Dataset sufficiency review was documented in internal report TR-2024-008.

### Bias examination
A pre-training bias audit was conducted across the following protected attributes: age group (18–40, 41–60, 61–80, 81+), sex, and ethnicity (8 categories). The audit identified a statistically significant underrepresentation of patients aged 81+ (2.1% of training data vs. an estimated 6.3% of the target EU deployment population) and patients of South Asian ethnicity (1.8% vs. estimated 4.1%). No bias was detected for sex-based categories. Bias audit report: BA-2024-003.

### Bias mitigation measures
Two mitigation strategies were applied. First, class-conditional oversampling was used to increase representation of patients aged 81+ to 5% of the final training distribution. Second, importance re-weighting was applied during training with weights inversely proportional to class frequency for the underrepresented ethnicity categories. Post-mitigation audit confirmed AUC parity within 0.02 across all demographic groups. Mitigation documentation: BM-2024-007.

### Data gaps
The primary identified gap is insufficient coverage of low-dose CT protocols used in national screening programmes outside the Netherlands and Germany. A secondary gap is limited coverage of paediatric patients (age < 18), who are explicitly excluded from the system's intended use scope. The low-dose protocol gap is partially addressed through synthetic data augmentation (Gaussian noise injection at σ ∈ [10, 30] HU). Full gap documentation: DG-2024-002.

### Relevance
The dataset directly represents the pathologies, patient populations, and imaging conditions targeted by RadAssist v2.1. All nodule categories in the intended use scope are represented. The dataset was validated against the LUNA16 public benchmark (sensitivity 0.93 at 1 FP/scan).

### Representativeness
Stratified sampling was applied across age group, sex, and diagnosis category. The training set distribution was compared against a population-level estimate of pulmonary nodule prevalence in the EU (Netherlands Cancer Institute, 2022 report). Chi-squared tests confirm no statistically significant deviation for any demographic category (p > 0.05 after mitigation).

### Statistical properties
no statistical propertie measurements were done

### Quality metrics
Post-annotation quality review confirmed an annotation error rate of 0.38% (disagreements not resolved after arbitration, excluded from training). Dataset completeness: 98.7% of slices passed all quality checks. Full quality metrics: QR-2024-004.

### Contextual characteristics
The training data originates from EU hospital radiology departments using standard clinical imaging workflows. Equipment spans Siemens, Philips, and GE CT scanner models common in EU tertiary care. All data is from the EU deployment context; non-EU clinical protocols are not represented.

---

## 3. Validation Dataset

### Design choices
A held-out validation split (10% of unique patients, stratified by age group and diagnosis category) was reserved prior to any model training. Patient-level splitting was used to prevent data leakage.

### Provenance
The validation set originates from the same 14 contributing hospitals as the training data, using temporally separated scans from 2022–2023 only (not used in training).

### Preprocessing
Identical preprocessing pipeline as the training set was applied independently to prevent preprocessing leakage.

### Assumptions
The validation set is assumed to reflect the same clinical distribution as the training data, as it is drawn from the same institutions and time window.

### Suitability
The validation dataset comprises 180,000 annotated CT slices from 8,700 patients, sufficient for stable hyperparameter tuning and architecture selection.

### Bias examination
Bias profile across all protected attributes matches the training set post-mitigation; no additional biases were introduced by the validation split procedure. Kolmogorov-Smirnov test p > 0.1 for all demographic distributions.

### Bias mitigation
The validation set inherits the same mitigation applied to the training data (class-conditional oversampling, importance re-weighting). No separate mitigation pipeline was applied to the validation set.

### Data gaps
Same gaps as the training set apply. No additional gaps were introduced by the validation split.

### Relevance
Covers the same nodule pathology scope and demographic distribution as the training set.

### Representativeness
Macro-averaged F1 score of 0.91 across all nodule categories. Performance is consistent across demographic subgroups (AUC range: 0.91–0.94 across age × sex combinations).

### Statistical properties
Class distribution matches the training set within 2% tolerance for all categories. Full distribution statistics: TR-2024-008.

### Quality metrics
Annotation error rate: 0.31%; dataset completeness: 99.1%.

### Contextual characteristics
Same clinical context as the training set. All data originates from EU hospital environments.

---

## 4. Testing Dataset

### Design choices
An independent test set was constructed from three hospitals not contributing to training or validation (Amsterdam UMC, Charité Berlin, and Hôpital Lariboisière Paris), providing geographic and institutional independence from the training distribution.

### Provenance
Data from three independent EU hospitals; separate IRB approvals are on file for each institution (IRB-AMC-2024-012, IRB-CHA-2024-008, IRB-LAR-2024-019). No overlap with training or validation institutions.

### Preprocessing
The identical preprocessing pipeline was applied by a separate data engineer with no access to training data to prevent unconscious preprocessing leakage.

### Assumptions
The test set is intended to represent unseen real-world deployment conditions, including variation in scanner manufacturer, acquisition protocol, and regional clinical practice.

### Suitability
The test dataset comprises 45,000 annotated CT slices from 1,800 patients. Statistical power analysis confirms this is sufficient for detecting performance differences of ≥ 2% AUC at β = 0.8.

### Bias examination
Bias profile independently verified by a third-party clinical data auditor. Across all demographic subgroups, AUC ≥ 0.92. Full bias verification report: TR-2024-008, Appendix C.

### Bias mitigation
The test set inherits the same bias mitigation applied during training (class-conditional oversampling, importance re-weighting). No separate mitigation pipeline was applied to the test set — it is used for evaluation only, preserving benchmark integrity.


### Data gaps
No additional gaps beyond those identified in the training set. The test set introduces regional protocol variation (Charité uses 0.6 mm slice thickness; Hôpital Lariboisière uses a distinct scout protocol) which is documented as an additional test condition rather than a gap.

### Relevance
Covers the same pathology scope as training and validation under independent acquisition conditions.

### Representativeness
System AUC on the test set: 0.944 (95% CI: 0.937–0.951). Performance is consistent across all demographic subgroups. Full evaluation: TR-2024-008.

### Statistical properties
Class distribution: solid 59.8%, sub-solid 23.4%, ground-glass 11.2%, benign/calcified 5.6%. Distribution and variance statistics: TR-2024-008.

### Quality metrics
Annotation error rate: 0.22%; dataset completeness: 99.5%.

### Contextual characteristics
Test data spans hospitals in the Netherlands, Germany, and France, capturing significant regional variation in acquisition protocol, scanner generation, and clinical workflow. This provides evidence of generalisation beyond the training distribution.

---

## 5. Sensitive Data

RadAssist v2.1 does not process special category personal data (as defined in GDPR Article 9) for the specific purpose of bias detection or correction. De-identified demographic metadata collected during annotation is used for stratified sampling and bias auditing but does not constitute special category processing under the relevant legal basis.

---

## 6. Regulatory Compliance Summary

This model card has been prepared in accordance with EU AI Act Article 10 (Data and data governance). All documentation requirements for training, validation, and testing datasets have been addressed. The system provider maintains this documentation as part of the technical documentation required under Article 11.

Contact for data governance queries: data-governance@medtech-solutions.nl
