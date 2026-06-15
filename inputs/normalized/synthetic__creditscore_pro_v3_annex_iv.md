# Annex IV Normalization — Article 10 Data Governance
<!-- Synthetic model card for diversity testing. -->

## Document metadata
- **System ID:** creditscore-pro-v3
- **Organisation:** FinRisk Analytics NV, Brussels, Belgium
- **System type:** High-risk AI system (EU AI Act Annex III, §5(b) — creditworthiness assessment)
- **Intended purpose:** Automated creditworthiness scoring for retail loan applications at EU financial institutions.
- **Version:** 3.0.1
- **Date:** February 2026
- **Normalized by:** Synthetic (compliance testing)
- **Date normalized:** 2026-06-15

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** CreditScore Pro v3, version 3.0.1
- **Intended purpose / task:** Gradient-boosted ensemble model that processes applicant financial history, income data, and behavioural features to produce a creditworthiness score (0–1000) and a binary approve/decline recommendation for retail loan applications. Output is provided to credit analysts as a decision-support tool; final credit decisions require human sign-off.
- **High-risk category (Annex III ref.):** Annex III §5(b) — AI systems intended to be used to evaluate the creditworthiness of natural persons or establish their credit score.
- **Intended users / deployers:** Credit analysts and retail banking teams at EU financial institutions. Deployed in Belgium, Netherlands, and Luxembourg.
- **Geographic / regulatory scope:** EU deployment. Training data from three Belgian and two Dutch retail banks.

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
The training dataset was designed to cover all major loan product categories (personal loans, mortgage pre-screening, revolving credit) across applicants in Belgium and the Netherlands. Selection criteria required (a) institutional provenance from regulated EU financial institutions, (b) minimum 5 years of longitudinal repayment outcome data per applicant, (c) balanced representation of approved and declined applications, and (d) inclusion of applicants from both urban and rural postcodes. Data collection was governed by the FinRisk Data Governance Committee (reference: FRDGC-2024-002).

### 2.2 Provenance  `Art. 10(2)(b)`
Training data was collected from three Belgian banks (KBC, Belfius, Argenta) and two Dutch banks (Rabobank, Triodos) under data processing agreements compliant with GDPR Article 6(1)(b) and EU AI Act Article 10. Each institution provided data covering 2017–2023. All records are pseudonymised using the ISO/IEC 29101 privacy framework. IRB-equivalent data ethics review completed at each institution (FRDGC-2024-002, Annex A).

### 2.3 Preprocessing  `Art. 10(2)(c)`
Raw data was standardised across institutions using a common schema. Categorical features (employment status, loan product type) were one-hot encoded. Continuous financial features (income, outstanding debt) were normalised using z-score standardisation computed on training data only. Missing values were imputed using median imputation per feature, with missingness indicators added as binary features. Ground-truth labels (default within 24 months: yes/no) were verified against national credit registry records (BNB/Kredietcentrale for Belgium, BKR for Netherlands). Inter-institution label reconciliation performed to resolve coding discrepancies; 0.4% of records excluded due to irreconcilable disagreements.

### 2.4 Assumptions  `Art. 10(2)(d)`
The dataset assumes that historical repayment outcomes from 2017–2023 are representative of creditworthiness patterns under current economic conditions. This assumption may be weakened by post-pandemic economic shifts and rising interest rates in 2022–2023.

### 2.5 Suitability  `Art. 10(2)(e)`
The training dataset comprises 1,840,000 application records from 620,000 unique applicants. Statistical power analysis (β = 0.8, α = 0.05) confirms this volume is sufficient for the intended binary classification task across all five loan product categories and target demographic subgroups. Dataset sufficiency review documented in technical report TR-2025-011.

### 2.6 Bias examination  `Art. 10(2)(f)`
A pre-training bias audit was conducted across protected attributes: age group (18–30, 31–50, 51–65, 65+), sex (male/female/non-binary), nationality (Belgian, Dutch, other EU, non-EU), and postcode deprivation quintile. The audit identified statistically significant underrepresentation of non-EU nationals (3.1% of training data vs. 7.4% estimated share of target population) and applicants in the highest deprivation quintile (8.2% vs. 14.1%). Bias audit report: BA-2025-004. Approval rate disparities by nationality and deprivation quintile documented in BA-2025-004, Table 3.

### 2.7 Bias mitigation  `Art. 10(2)(g)`
Two mitigation strategies applied. First, importance re-weighting inversely proportional to demographic group frequency for non-EU nationals and high-deprivation-quintile applicants. Second, a fairness constraint (equalised odds) was imposed during training using the Fairlearn library (v0.10). Post-mitigation disparity analysis confirmed approval rate parity within ±3% across all nationality and deprivation groups. Full mitigation documentation: BM-2025-006.

### 2.8 Data gaps  `Art. 10(2)(h)`
The main data gap is limited coverage of self-employed applicants with irregular income streams, who represent approximately 9% of the target population but only 4.3% of the training data. No systematic gap analysis report was produced; this gap was identified informally during model development.

### 2.9 Relevance  `Art. 10(3)`
The training dataset directly represents the creditworthiness assessment task, covering all five loan product categories within the intended deployment scope. Labels reflect verified 24-month default outcomes from national credit registries.

### 2.10 Representativeness  `Art. 10(3)`
The training set was compared against population estimates from Eurostat 2023 EU-SILC data for Belgium and Netherlands. Post-mitigation distributions for age and sex show no statistically significant deviation (chi-squared, p > 0.05). Nationality and deprivation distributions remain underrepresented for non-EU nationals after mitigation; residual gap documented in BA-2025-004.

### 2.11 Statistical properties  `Art. 10(3)`
Label distribution: default (positive class) 12.4%, no default (negative class) 87.6%. Class imbalance addressed using focal loss (γ = 2.0) and post-hoc threshold calibration. Per-feature distribution statistics and correlation matrix documented in TR-2025-011, Section 4.

### 2.12 Quality metrics  `Art. 10(3)`
not provided

### 2.13 Contextual characteristics  `Art. 10(4)`
Training data originates from retail banking environments in Belgium and the Netherlands, operating under ECB prudential regulation and national consumer credit legislation. Loan products and applicant demographic profiles reflect Western European retail banking conditions.

---

## Section 3 — Validation Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 3.1 Design choices  `Art. 10(2)(a)`
A held-out validation split (15% of unique applicants, stratified by loan product category and nationality) was reserved prior to any model training. Applicant-level splitting used to prevent leakage.

### 3.2 Provenance  `Art. 10(2)(b)`
The validation set originates from the same five contributing institutions as the training data, using records from 2022–2023 only to ensure temporal separation.

### 3.3 Preprocessing  `Art. 10(2)(c)`
Identical preprocessing pipeline applied independently. Normalisation statistics (mean, standard deviation) computed on training data only and applied to the validation set to prevent preprocessing leakage.

### 3.4 Assumptions  `Art. 10(2)(d)`
not provided

### 3.5 Suitability  `Art. 10(2)(e)`
The validation dataset comprises 276,000 application records from 93,000 unique applicants, sufficient for stable hyperparameter selection and threshold calibration.

### 3.6 Bias examination  `Art. 10(2)(f)`
Bias profile checked informally; distributions across age and sex groups appeared similar to the training set. No formal statistical analysis was performed on the validation split.

### 3.7 Bias mitigation  `Art. 10(2)(g)`
Validation set inherits training data demographics. No separate mitigation applied; validation used for evaluation only.

### 3.8 Data gaps  `Art. 10(2)(h)`
not provided

### 3.9 Relevance  `Art. 10(3)`
Covers the same loan product scope and demographic distribution as the training set.

### 3.10 Representativeness  `Art. 10(3)`
Stratification confirmed the validation set follows the same product category distribution as training within 3% tolerance. No demographic stratification analysis performed.

### 3.11 Statistical properties  `Art. 10(3)`
Label distribution: default 12.7%, no default 87.3%. Distribution matches training within 0.5%.

### 3.12 Quality metrics  `Art. 10(3)`
not provided

### 3.13 Contextual characteristics  `Art. 10(4)`
Same institutional and regulatory context as training data. All records from Belgian and Dutch retail banking environments.

---

## Section 4 — Testing Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 4.1 Design choices  `Art. 10(2)(a)`
An independent test set was constructed from two institutions not contributing to training or validation: ING Belgium and ABN AMRO Netherlands. Provides institutional independence from training distribution.

### 4.2 Provenance  `Art. 10(2)(b)`
Data from ING Belgium (IRB-ING-2025-003) and ABN AMRO Netherlands (IRB-ABN-2025-007). Records cover 2023 only. No overlap with training or validation institutions.

### 4.3 Preprocessing  `Art. 10(2)(c)`
Same preprocessing pipeline applied. Normalisation statistics inherited from training data.

### 4.4 Assumptions  `Art. 10(2)(d)`
not provided

### 4.5 Suitability  `Art. 10(2)(e)`
The test dataset comprises 88,000 application records from 29,000 unique applicants. Sufficient for detecting AUC differences of ≥ 2% at β = 0.8.

### 4.6 Bias examination  `Art. 10(2)(f)`
not provided

### 4.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 4.8 Data gaps  `Art. 10(2)(h)`
not provided

### 4.9 Relevance  `Art. 10(3)`
Covers the same loan product categories under independent institutional acquisition conditions.

### 4.10 Representativeness  `Art. 10(3)`
not provided

### 4.11 Statistical properties  `Art. 10(3)`
Default rate on test set: 13.1%. Distribution statistics not separately documented.

### 4.12 Quality metrics  `Art. 10(3)`
not provided

### 4.13 Contextual characteristics  `Art. 10(4)`
not provided
