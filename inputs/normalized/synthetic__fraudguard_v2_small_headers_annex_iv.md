# Annex IV Normalization — Article 10 Data Governance
<!-- Synthetic model card — small text size, WITH section headers. All fields present and adequate. -->

## Document metadata
- **System ID:** fraudguard-v2
- **Organisation:** PayShield Analytics BV, Rotterdam, Netherlands
- **System type:** High-risk AI system (EU AI Act Annex III, §5(b) — creditworthiness / financial)
- **Intended purpose:** Real-time detection of fraudulent payment transactions for EU retail banking clients.
- **Version:** 2.0.0
- **Date:** April 2026
- **Normalized by:** Synthetic (compliance testing)
- **Date normalized:** 2026-06-15

---

## Section 1 — System Overview

- **System name and version:** FraudGuard v2, version 2.0.0
- **Intended purpose / task:** Gradient-boosted ensemble that scores individual payment transactions (0–1 fraud probability) in real time; flags above threshold 0.7 for human analyst review.
- **High-risk category (Annex III ref.):** Annex III §5(b) — creditworthiness and financial risk.
- **Intended users / deployers:** Fraud operations analysts at EU retail banks.
- **Geographic / regulatory scope:** EU deployment; training data from Dutch and Belgian banks under PSD2 and GDPR frameworks.

---

## Section 2 — Training Dataset

### 2.1 Design choices  `Art. 10(2)(a)`
Dataset selected to cover all major payment channels (card-present, card-not-present, SEPA credit transfer) across retail and business accounts from two Dutch and one Belgian bank, using transactions from 2020–2024 with confirmed fraud labels from dispute resolution records.

### 2.2 Provenance  `Art. 10(2)(b)`
Data sourced from ING Netherlands, Rabobank, and BNP Paribas Fortis under GDPR Article 6(1)(c) data processing agreements; each institution provided IRB-equivalent data ethics approval (IRB-ING-2025-001, IRB-RABO-2025-002, IRB-BNP-2025-003); records pseudonymised under ISO 29101.

### 2.3 Preprocessing  `Art. 10(2)(c)`
Transaction features standardised to a common schema; continuous fields z-score normalised on training data; fraud labels verified against confirmed chargeback records with two-analyst reconciliation (Cohen κ = 0.91); 0.3% of records excluded due to irreconcilable label disputes.

### 2.4 Assumptions  `Art. 10(2)(d)`
Dataset assumes that confirmed chargebacks are a valid proxy for fraud ground truth and that 2020–2024 fraud patterns are representative of current attack vectors; known limitation: synthetic fraud patterns introduced post-2024 are not represented.

### 2.5 Suitability  `Art. 10(2)(e)`
Training set contains 4,200,000 transactions (210,000 fraud-positive); statistical power analysis (β = 0.8, α = 0.05) confirms sufficient volume for binary classification across all payment channels; documented in TR-2025-007.

### 2.6 Bias examination  `Art. 10(2)(f)`
Pre-training bias audit conducted across account holder age group, sex, and nationality; audit identified underrepresentation of non-EU nationals (2.1% vs. 5.8% estimated deployment population); no significant imbalance detected for age or sex; audit report BA-2025-002.

### 2.7 Bias mitigation  `Art. 10(2)(g)`
Importance re-weighting applied inversely proportional to nationality group frequency; post-mitigation false-positive rate parity confirmed within ±1.5% across all nationality groups; documented in BM-2025-003.

### 2.8 Data gaps  `Art. 10(2)(h)`
Primary gap is limited coverage of crypto-linked payment fraud (1.2% of training vs. 4.1% estimated current prevalence); addressed via quarterly label refresh from updated chargeback records; documented in DG-2025-004.

### 2.9 Relevance  `Art. 10(3)`
Dataset directly represents all target payment channels and fraud types in the intended EU retail banking deployment scope; validated against ECB payment fraud statistics 2024 (recall 0.91 on ECB benchmark subset).

### 2.10 Representativeness  `Art. 10(3)`
Stratified sampling applied across payment channel and account type; post-mitigation distributions compared against ECB payment statistics 2024; chi-squared tests confirm no significant deviation (p > 0.05) for channel or nationality distributions.

### 2.11 Statistical properties  `Art. 10(3)`
Label distribution: fraud 5.0%, non-fraud 95.0%; class imbalance addressed with focal loss (γ = 2.0) and post-hoc threshold calibration; per-channel class distributions in TR-2025-007, Table 3.

### 2.12 Quality metrics  `Art. 10(3)`
Label disagreement rate 0.3% (post-arbitration exclusions); transaction encoding error rate 0.1%; dataset completeness 99.8%; full quality report QR-2025-005.

### 2.13 Contextual characteristics  `Art. 10(4)`
Training data originates from Dutch and Belgian retail banking environments operating under PSD2, EBA fraud reporting guidelines, and national central bank supervision; non-EU payment network patterns are not represented.

---

## Section 3 — Validation Dataset

### 3.1 Design choices  `Art. 10(2)(a)`
Held-out 10% patient-level split stratified by payment channel and fraud outcome, reserved prior to any model training to prevent leakage.

### 3.2 Provenance  `Art. 10(2)(b)`
Drawn from same three institutions as training data; temporally separated using 2023–2024 transactions only.

### 3.3 Preprocessing  `Art. 10(2)(c)`
Identical pipeline applied independently; normalisation statistics inherited from training data only.

### 3.4 Assumptions  `Art. 10(2)(d)`
Validation set assumed to reflect same fraud distribution as training; temporal separation may introduce mild distribution shift from evolving fraud patterns in 2023–2024.

### 3.5 Suitability  `Art. 10(2)(e)`
420,000 transactions (21,000 fraud-positive); sufficient for stable threshold calibration and hyperparameter selection across all payment channels.

### 3.6 Bias examination  `Art. 10(2)(f)`
Kolmogorov-Smirnov tests confirm demographic distributions match training post-mitigation (p > 0.1 for all attributes); no additional bias introduced by validation split.

### 3.7 Bias mitigation  `Art. 10(2)(g)`
Validation set inherits training re-weighting; no separate mitigation applied to preserve evaluation integrity.

### 3.8 Data gaps  `Art. 10(2)(h)`
Same gaps as training apply; crypto-linked fraud underrepresentation persists in validation split.

### 3.9 Relevance  `Art. 10(3)`
Covers same payment channels and fraud taxonomy as training set.

### 3.10 Representativeness  `Art. 10(3)`
Channel distribution matches training within 1% tolerance; macro-averaged AUROC on validation 0.96 consistent across demographic subgroups (range 0.95–0.97); TR-2025-007, Table 5.

### 3.11 Statistical properties  `Art. 10(3)`
Label distribution: fraud 5.0%, non-fraud 95.0%; matches training within 0.1%; TR-2025-007, Table 4.

### 3.12 Quality metrics  `Art. 10(3)`
Label error rate 0.2%; completeness 99.9%; QR-2025-005, Section 4.

### 3.13 Contextual characteristics  `Art. 10(4)`
Same Dutch and Belgian retail banking context as training; all records from same three institutions.

---

## Section 4 — Testing Dataset

### 4.1 Design choices  `Art. 10(2)(a)`
Independent test set from two institutions not in training or validation: ABN AMRO Netherlands and KBC Belgium, providing institutional independence.

### 4.2 Provenance  `Art. 10(2)(b)`
Data from ABN AMRO (IRB-ABN-2025-006) and KBC (IRB-KBC-2025-009); records from 2024 only; no overlap with training institutions.

### 4.3 Preprocessing  `Art. 10(2)(c)`
Identical pipeline applied by a separate data engineer with no access to training data; normalisation parameters inherited from training.

### 4.4 Assumptions  `Art. 10(2)(d)`
Test set intended to represent unseen institutional conditions; ABN AMRO and KBC transaction profiles and fraud typology differ slightly from training institutions.

### 4.5 Suitability  `Art. 10(2)(e)`
180,000 transactions (8,700 fraud-positive); power analysis confirms sufficient for detecting AUROC differences ≥ 1% at β = 0.8.

### 4.6 Bias examination  `Art. 10(2)(f)`
Third-party auditor verified false-positive rate parity across age, sex, and nationality subgroups; all subgroup FPR within ±1.8% of overall FPR; report TR-2025-007, Appendix B.

### 4.7 Bias mitigation  `Art. 10(2)(g)`
No mitigation applied to test set to preserve benchmark integrity; deliberate decision documented in TR-2025-007, Appendix B.

### 4.8 Data gaps  `Art. 10(2)(h)`
No additional gaps beyond training; ABN AMRO introduces higher share of SEPA instant payment transactions (18% vs. 11% in training), documented as an additional test condition in DG-2025-004.

### 4.9 Relevance  `Art. 10(3)`
Covers same fraud taxonomy and payment channels under independent institutional conditions.

### 4.10 Representativeness  `Art. 10(3)`
System AUROC on test set 0.95 (95% CI: 0.94–0.96); consistent across all demographic subgroups; TR-2025-007.

### 4.11 Statistical properties  `Art. 10(3)`
Label distribution: fraud 4.8%, non-fraud 95.2%; distribution and variance statistics in TR-2025-007, Table 6.

### 4.12 Quality metrics  `Art. 10(3)`
Label error rate 0.2%; completeness 99.9%; QR-2025-005, Section 5.

### 4.13 Contextual characteristics  `Art. 10(4)`
Test data from Dutch and Belgian retail banks; ABN AMRO introduces higher SEPA instant payment volume, capturing payment network variation not fully represented in training.
