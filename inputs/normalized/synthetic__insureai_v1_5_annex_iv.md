# Annex IV Normalization — Article 10 Data Governance
<!-- Synthetic model card for diversity testing — training solid, val partial, test minimal. -->

## Document metadata
- **System ID:** insureai-v1.5
- **Organisation:** Aequitas Risk Solutions OÜ, Tallinn, Estonia
- **System type:** High-risk AI system (EU AI Act Annex III, §5(c) — insurance risk assessment)
- **Intended purpose:** Automated mortality risk scoring for life insurance underwriting decisions at EU insurance providers.
- **Version:** 1.5.2
- **Date:** January 2026
- **Normalized by:** Synthetic (compliance testing)
- **Date normalized:** 2026-06-15

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** InsureAI v1.5, version 1.5.2
- **Intended purpose / task:** Gradient-boosted tree model that processes applicant health and lifestyle data to produce a 5-year mortality risk score (0–1) and a risk band (standard/rated/declined) for life insurance underwriting. Output is provided to underwriters as a decision-support tool; final underwriting decisions require human sign-off.
- **High-risk category (Annex III ref.):** Annex III §5(c) — AI systems intended to be used to evaluate health risks and health insurance premiums for natural persons.
- **Intended users / deployers:** Underwriters and actuarial teams at EU life insurance providers.
- **Geographic / regulatory scope:** EU deployment. Training data from insurance providers in Estonia, Finland, and Denmark.

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
The training dataset was designed to cover all three risk bands (standard/rated/declined) across a representative range of applicant demographics including age group (18–80), sex, and health status categories. Selection criteria required (a) institutional provenance from regulated EU insurance providers, (b) minimum 5-year longitudinal follow-up outcome data per applicant, (c) balanced representation of risk bands within each age group, and (d) applicant-level separation from validation and test splits. Data collection governed by the Aequitas Data Governance Council (reference: ADGC-2024-001).

### 2.2 Provenance  `Art. 10(2)(b)`
Training data was collected from three EU life insurance providers: LHV Kindlustus (Estonia), Mandatum Life (Finland), and PFA Pension (Denmark). Data collection period: 2015–2023. All records processed under GDPR Article 9(2)(j) derogation for actuarial research, with explicit data processing agreements at each provider (DUA-ADGC-2024-001, Annex B). Records pseudonymised using ISO 29101-compliant de-identification. Actuarial data ethics review completed by the Estonian Financial Supervision Authority (FSA review reference: FSA-2024-023).

### 2.3 Preprocessing  `Art. 10(2)(c)`
Health and lifestyle features standardised using a common actuarial data schema. Continuous features (BMI, blood pressure, cholesterol) normalised using z-score standardisation computed on training data only. Categorical features (smoking status, occupational hazard class) one-hot encoded. Missing values imputed using multiple imputation by chained equations (MICE, 10 imputations). Five-year all-cause mortality labels verified against national population registries (Estonian Population Register, Finnish Population Register Centre, Danish Civil Registration System). Inter-provider label reconciliation: 0.2% of records excluded due to registry linkage failures. Preprocessing documented in InsureAI Technical Report IATR-2024-004.

### 2.4 Assumptions  `Art. 10(2)(d)`
The dataset assumes that 5-year all-cause mortality outcomes from national population registries are a valid proxy for the mortality risk assessment task. This assumption may be weakened for very long-duration policies (> 20 years) where current 5-year risk patterns may not extrapolate. The model is not intended for applicants under 18. Key limitation: applicants with significant pre-existing conditions (cancer, end-stage renal disease) are underrepresented relative to the general population due to self-selection in the insurance application pool; this is documented as a known limitation in IATR-2024-004, Section 5.

### 2.5 Suitability  `Art. 10(2)(e)`
The training dataset comprises 980,000 applicant records from 490,000 unique individuals (two applications per individual on average). Statistical power analysis (β = 0.8, α = 0.05) confirms this is sufficient for three-class risk band classification across all age groups. Dataset sufficiency review: IATR-2024-004, Section 3. Per-age-group minimum sufficiency thresholds verified (minimum 60,000 records per 10-year age band).

### 2.6 Bias examination  `Art. 10(2)(f)`
A pre-training bias audit was conducted across protected attributes: age group (18–30, 31–50, 51–65, 65–80), sex (male/female/non-binary), and nationality (Estonian, Finnish, Danish, other EU, non-EU). The audit identified underrepresentation of non-EU nationality applicants (1.8% of training data vs. 4.2% estimated share of target population) and applicants aged 65–80 with pre-existing conditions (6.1% vs. 9.4% estimated). Bias audit report: IABA-2024-003. Risk band outcome disparities by sex and age documented in IABA-2024-003, Table 5.

### 2.7 Bias mitigation  `Art. 10(2)(g)`
Two mitigation strategies applied. First, importance re-weighting inversely proportional to demographic group frequency for non-EU nationality applicants and applicants aged 65–80 with pre-existing conditions. Second, a fairness constraint (demographic parity regularisation) applied to prevent risk band assignment disparities exceeding ±4% across sex and age subgroups. Post-mitigation audit confirmed risk band parity within ±3.5% across all sex and age subgroups. Full mitigation documentation: IABM-2024-005.

### 2.8 Data gaps  `Art. 10(2)(h)`
The main gap is limited coverage of high-risk occupational categories (mining, offshore work), which represent approximately 2% of applicants but are underrepresented in the training data from the three partner providers. No formal gap analysis report was produced; this gap was noted informally in IATR-2024-004, Section 5.

### 2.9 Relevance  `Art. 10(3)`
The training dataset directly represents the mortality risk scoring task, covering all three risk bands and all target demographic segments within the intended deployment scope. Labels verified against national population registry records.

### 2.10 Representativeness  `Art. 10(3)`
Stratified sampling applied across risk band, age group, and sex. Post-mitigation distributions compared against Eurostat 2022 life table data for Estonia, Finland, and Denmark. Chi-squared tests confirm no statistically significant deviation for risk band or age group distributions (p > 0.05 after mitigation). Nationality distribution remains residually underrepresented for non-EU applicants; documented in IABA-2024-003.

### 2.11 Statistical properties  `Art. 10(3)`
Risk band distribution: standard 74.2%, rated 19.1%, declined 6.7%. Per-feature correlation matrix and per-class variance statistics documented in IATR-2024-004, Table 4. Class imbalance for declined category addressed using class-weight adjustment (weight = 3.5× for declined class).

### 2.12 Quality metrics  `Art. 10(3)`
not provided

### 2.13 Contextual characteristics  `Art. 10(4)`
Training data originates from life insurance providers in Estonia, Finland, and Denmark, operating under Solvency II and national insurance regulatory frameworks. Applicant demographics and actuarial risk profiles reflect Northern European life insurance markets.

---

## Section 3 — Validation Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 3.1 Design choices  `Art. 10(2)(a)`
A held-out validation split (15% of unique applicants, stratified by risk band and age group) was reserved prior to any model training. Applicant-level splitting used to prevent leakage.

### 3.2 Provenance  `Art. 10(2)(b)`
Validation set originates from the same three contributing insurance providers as the training data, using records from 2022–2023.

### 3.3 Preprocessing  `Art. 10(2)(c)`
Same preprocessing pipeline applied. Normalisation statistics inherited from training data.

### 3.4 Assumptions  `Art. 10(2)(d)`
not provided

### 3.5 Suitability  `Art. 10(2)(e)`
The validation dataset comprises 147,000 applicant records from 73,500 unique individuals. Sufficient for stable hyperparameter tuning and model selection.

### 3.6 Bias examination  `Art. 10(2)(f)`
Informal review of validation set risk band distributions by age and sex was conducted. No significant differences from training set distributions were observed. No formal disparity analysis was performed.

### 3.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 3.8 Data gaps  `Art. 10(2)(h)`
not provided

### 3.9 Relevance  `Art. 10(3)`
Covers the same risk band scope and demographic distribution as the training set.

### 3.10 Representativeness  `Art. 10(3)`
not provided

### 3.11 Statistical properties  `Art. 10(3)`
Risk band distribution: standard 74.5%, rated 18.8%, declined 6.7%. Distribution approximately matches training.

### 3.12 Quality metrics  `Art. 10(3)`
not provided

### 3.13 Contextual characteristics  `Art. 10(4)`
Same institutional and regulatory context as training data. Records from Estonian, Finnish, and Danish insurance providers.

---

## Section 4 — Testing Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 4.1 Design choices  `Art. 10(2)(a)`
An independent test set was constructed from one insurance provider not contributing to training or validation: Tryg Forsikring (Denmark/Norway). Provides institutional independence.

### 4.2 Provenance  `Art. 10(2)(b)`
Data from Tryg Forsikring under DUA-ADGC-2025-002. Records cover 2023–2024.

### 4.3 Preprocessing  `Art. 10(2)(c)`
not provided

### 4.4 Assumptions  `Art. 10(2)(d)`
not provided

### 4.5 Suitability  `Art. 10(2)(e)`
The test dataset comprises 42,000 applicant records from 21,000 unique individuals. Sufficient for primary performance evaluation.

### 4.6 Bias examination  `Art. 10(2)(f)`
not provided

### 4.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 4.8 Data gaps  `Art. 10(2)(h)`
not provided

### 4.9 Relevance  `Art. 10(3)`
Covers the same risk assessment task under independent institutional conditions.

### 4.10 Representativeness  `Art. 10(3)`
not provided

### 4.11 Statistical properties  `Art. 10(3)`
not provided

### 4.12 Quality metrics  `Art. 10(3)`
not provided

### 4.13 Contextual characteristics  `Art. 10(4)`
not provided
