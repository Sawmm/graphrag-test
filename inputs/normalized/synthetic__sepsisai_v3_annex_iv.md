# Annex IV Normalization — Article 10 Data Governance
<!-- Synthetic model card for diversity testing — uniform middle-range compliance (~55% adequate across all sections). -->

## Document metadata
- **System ID:** sepsisai-v3
- **Organisation:** CriticalPath Medical GmbH, Vienna, Austria
- **System type:** High-risk AI system (EU AI Act Annex III, §5(a) — medical device)
- **Intended purpose:** Early warning prediction of sepsis onset in adult ICU patients based on continuous vital sign monitoring and laboratory results.
- **Version:** 3.2.0
- **Date:** May 2026
- **Normalized by:** Synthetic (compliance testing)
- **Date normalized:** 2026-06-15

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** SepsisAI v3, version 3.2.0
- **Intended purpose / task:** LSTM-based early warning system that continuously processes ICU patient vital sign streams (heart rate, blood pressure, respiratory rate, SpO2, temperature) and laboratory results (lactate, WBC, CRP, procalcitonin) to produce a sepsis onset risk score (0–1) and a binary alert (low risk / high risk) updated every 30 minutes. Intended as a clinical decision-support alert for ICU nursing and physician teams; clinical intervention decisions require human clinical sign-off.
- **High-risk category (Annex III ref.):** Annex III §5(a) — AI systems intended to be used as safety components in medical devices or as medical devices themselves.
- **Intended users / deployers:** ICU nursing staff and intensivists at EU secondary and tertiary care hospitals. Requires integration with hospital ICU information systems (Philips IntelliVue, Dräger Infinity).
- **Geographic / regulatory scope:** EU deployment. Training data from ICU units in Austria, Czech Republic, and Hungary. Regulatory submission under MDR 2017/745 as a Class IIb medical device.

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
The training dataset was designed to cover both sepsis onset (positive class) and non-sepsis ICU stays (negative class) across a representative range of patient demographics and admission diagnoses. Selection criteria required (a) institutional provenance from regulated EU ICU environments, (b) confirmed sepsis labels derived from Sepsis-3 clinical consensus criteria (Singer et al. 2016), (c) minimum 24-hour ICU stay per patient to capture time-series dynamics, and (d) patient-level separation from validation and test splits to prevent leakage. Data collection was governed by the CriticalPath Data Governance Committee (reference: CPDGC-2025-001).

### 2.2 Provenance  `Art. 10(2)(b)`
Training data was collected from ICU units at four hospitals: Allgemeines Krankenhaus Wien (AKH Vienna, Austria), Medizinische Universität Innsbruck (Austria), Fakultní nemocnice Brno (Czech Republic), and Semmelweis Egyetem (Hungary). Data collection period: January 2019 – December 2024. All records processed under GDPR Article 9(2)(h) derogation for medical care purposes, with institutional review board approval at each centre (IRB-AKH-2025-007, IRB-INNSBRUCK-2025-003, IRB-BRNO-2025-011, IRB-SEMMELWEIS-2025-005). Patient identifiers removed using de-identification pipeline compliant with ISO 29101. Data coordinated by CPDGC-2025-001.

### 2.3 Preprocessing  `Art. 10(2)(c)`
Vital sign time series resampled to 5-minute intervals using forward-fill interpolation. Missing vital signs with gaps exceeding 60 minutes treated as missing and flagged with a missingness indicator feature. Laboratory values aligned to the nearest prior measurement within a 6-hour window. Sepsis-3 labels derived from retrospective clinical record review by two board-certified intensivists per case; disagreements resolved by a third senior intensivist arbitrator (Cohen κ = 0.79, substantial agreement). ICU stays with irreconcilable label disagreements excluded (1.1%). Feature engineering documented in CriticalPath Technical Report CPTR-2025-002.

### 2.4 Assumptions  `Art. 10(2)(d)`
The dataset assumes that Sepsis-3 criteria applied retrospectively to clinical records provide a valid ground truth for the prospective early warning task. This assumption may not hold for patients with atypical sepsis presentations or comorbidities that mask standard inflammatory markers. The model is intended for adult patients only (age ≥ 18); paediatric ICU patients are explicitly excluded. The dataset further assumes continuous vital sign monitoring using clinical-grade ICU equipment; degraded or intermittent monitoring conditions may reduce model reliability.

### 2.5 Suitability  `Art. 10(2)(e)`
The training dataset comprises 48,000 ICU patient stays (14,200 sepsis-positive, 33,800 sepsis-negative) from the four contributing hospitals. Statistical power analysis (β = 0.8, α = 0.05) confirms this is sufficient for binary classification of sepsis onset across major admission diagnosis categories. Dataset sufficiency review documented in CPTR-2025-002, Section 3.

### 2.6 Bias examination  `Art. 10(2)(f)`
A review of the training data distribution was conducted. Patient age and sex distributions were inspected visually. Male patients represent 58.4% of the training cohort and female patients 41.6%. Age distribution skews toward older patients (median age 64 years). No formal protected attribute analysis or statistical disparity testing was performed across demographic subgroups. No audit report was produced.

### 2.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 2.8 Data gaps  `Art. 10(2)(h)`
The primary identified data gap is limited representation of patients from Hungarian and Czech hospital sites relative to the Austrian sites (25% combined vs. 75% Austrian). A secondary gap is underrepresentation of immunocompromised patients (solid organ transplant, haematological malignancy) who have atypical sepsis presentations. Gap documentation: CPDG-2025-003.

### 2.9 Relevance  `Art. 10(3)`
The training dataset directly represents the sepsis early warning task in ICU environments consistent with the intended deployment context. Sepsis-3 labels reflect the clinical standard applied in the target EU deployment hospitals. Validated against MIMIC-IV public benchmark (AUROC 0.87 on held-out MIMIC-IV sepsis cohort, CPTR-2025-002, Section 6).

### 2.10 Representativeness  `Art. 10(3)`
not provided

### 2.11 Statistical properties  `Art. 10(3)`
Label distribution: sepsis-positive 29.6%, sepsis-negative 70.4%. Class imbalance addressed using focal loss (γ = 2.0). Per-admission-category label breakdowns and time-to-sepsis distribution statistics summarised briefly in CPTR-2025-002 but not fully documented.

### 2.12 Quality metrics  `Art. 10(3)`
not provided

### 2.13 Contextual characteristics  `Art. 10(4)`
Training data originates from medical and surgical ICU units in Austria, Czech Republic, and Hungary, reflecting Central European tertiary care contexts. Equipment spans Philips IntelliVue MX800 and Dräger Infinity monitors, consistent with the intended deployment infrastructure. Non-EU ICU protocols are not represented.

---

## Section 3 — Validation Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 3.1 Design choices  `Art. 10(2)(a)`
A held-out validation split (15% of unique patients, stratified by sepsis outcome and hospital site) was reserved prior to any model training. Patient-level splitting used to prevent leakage.

### 3.2 Provenance  `Art. 10(2)(b)`
Validation set drawn from the same four contributing hospitals as the training data, using ICU stays from 2023–2024 to ensure temporal separation from the bulk of training data.

### 3.3 Preprocessing  `Art. 10(2)(c)`
Same preprocessing pipeline applied. Feature engineering and resampling parameters inherited from training data.

### 3.4 Assumptions  `Art. 10(2)(d)`
The validation set is assumed to reflect a similar clinical distribution to the training data. Temporal separation may introduce distribution shift from 2023–2024 clinical practice changes.

### 3.5 Suitability  `Art. 10(2)(e)`
The validation dataset comprises 7,200 patient stays (2,130 sepsis-positive, 5,070 sepsis-negative). Sufficient for hyperparameter tuning and model selection.

### 3.6 Bias examination  `Art. 10(2)(f)`
not provided

### 3.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 3.8 Data gaps  `Art. 10(2)(h)`
Same gaps as training set apply. Austrian hospital sites remain overrepresented in validation.

### 3.9 Relevance  `Art. 10(3)`
Covers the same sepsis detection task and ICU clinical context as the training set.

### 3.10 Representativeness  `Art. 10(3)`
Stratification confirmed validation set follows the same sepsis outcome distribution as training within 3% tolerance. No formal demographic representativeness analysis performed.

### 3.11 Statistical properties  `Art. 10(3)`
Label distribution: sepsis-positive 29.6%, sepsis-negative 70.4%. Matches training distribution.

### 3.12 Quality metrics  `Art. 10(3)`
not provided

### 3.13 Contextual characteristics  `Art. 10(4)`
Same institutional and clinical context as training data. All records from Austrian, Czech, and Hungarian ICU environments.

---

## Section 4 — Testing Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 4.1 Design choices  `Art. 10(2)(a)`
An independent test set was constructed from two hospitals not contributing to training or validation: Universitätsklinikum Graz (Austria) and Nemocnice Na Bulovce (Czech Republic). Provides institutional independence from training distribution.

### 4.2 Provenance  `Art. 10(2)(b)`
Data from Universitätsklinikum Graz (IRB-GRAZ-2025-014) and Nemocnice Na Bulovce (IRB-NNB-2025-008). Records cover 2024. No overlap with training or validation institutions.

### 4.3 Preprocessing  `Art. 10(2)(c)`
Same preprocessing pipeline applied. Resampling and feature engineering parameters inherited from training configuration.

### 4.4 Assumptions  `Art. 10(2)(d)`
not provided

### 4.5 Suitability  `Art. 10(2)(e)`
The test dataset comprises 4,800 patient stays (1,390 sepsis-positive, 3,410 sepsis-negative). Statistical power analysis confirms sufficient for detecting AUROC differences of ≥ 2% at β = 0.8.

### 4.6 Bias examination  `Art. 10(2)(f)`
AUROC was computed separately for male and female patient subgroups. Male subgroup AUROC: 0.86; female subgroup AUROC: 0.84. Age subgroup analysis not performed. No formal protected attribute audit report produced.

### 4.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 4.8 Data gaps  `Art. 10(2)(h)`
not provided

### 4.9 Relevance  `Art. 10(3)`
Covers the same sepsis detection task under independent institutional conditions. Graz and Prague hospital sites reflect deployment contexts distinct from training institutions.

### 4.10 Representativeness  `Art. 10(3)`
System AUROC on test set: 0.86 (95% CI: 0.84–0.88). Graz and Prague subsets show consistent performance (AUROC 0.87 and 0.85 respectively). Full evaluation: CPTR-2025-002.

### 4.11 Statistical properties  `Art. 10(3)`
Label distribution: sepsis-positive 29.0%, sepsis-negative 71.0%. Distribution consistent with training and validation sets.

### 4.12 Quality metrics  `Art. 10(3)`
Label disagreement rate: 1.3% (higher than training due to single-annotator review at test sites). Dataset completeness: 97.8%.

### 4.13 Contextual characteristics  `Art. 10(4)`
Test data from Austrian and Czech ICU environments. Graz hospital uses Philips IntelliVue equipment consistent with training; Prague site uses GE Carescape monitors, introducing minor equipment-context variation not seen in training.
