# Annex IV Normalization — Article 10 Data Governance
<!-- Synthetic model card for diversity testing — fully compliant profile. -->

## Document metadata
- **System ID:** druginteract-v1
- **Organisation:** PharmaSafe AI BV, Utrecht, Netherlands
- **System type:** High-risk AI system (EU AI Act Annex III, §5(a) — medical device)
- **Intended purpose:** Prediction of clinically significant drug-drug interactions for polypharmacy patients in hospital dispensary workflows.
- **Version:** 1.0.0
- **Date:** April 2026
- **Normalized by:** Synthetic (compliance testing)
- **Date normalized:** 2026-06-15

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** DrugInteract v1, version 1.0.0
- **Intended purpose / task:** Supervised transformer-based classification system trained to predict the presence and severity of drug-drug interactions (DDIs) for pairs of medications co-prescribed to polypharmacy patients (≥5 concurrent medications). Outputs a severity class (minor/moderate/major/contraindicated) and confidence score per drug pair. Intended as a decision-support alert for hospital pharmacists; clinical override is documented and audited.
- **High-risk category (Annex III ref.):** Annex III §5(a) — AI systems intended to be used as safety components in medical devices or as medical devices themselves.
- **Intended users / deployers:** Hospital pharmacists and clinical pharmacology units at EU secondary and tertiary care hospitals. Requires integration with hospital electronic prescribing systems.
- **Geographic / regulatory scope:** EU deployment. Training data from hospital pharmacies in Netherlands, Germany, and France. Regulatory submission prepared under MDR 2017/745 as a Class IIa medical device.

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
The training dataset was designed to cover all four DDI severity categories (minor, moderate, major, contraindicated) across a representative range of drug classes, patient age groups, and comorbidity profiles. Selection criteria required (a) institutional provenance from regulated EU hospital pharmacies, (b) confirmed clinical DDI outcomes from adverse event reporting systems, (c) structured drug coding using ATC classification (WHO 2024), and (d) patient-level separation from validation and test splits to prevent data leakage. Coverage was extended to polypharmacy patients aged 65+ following a pre-training gap analysis identifying age-related underrepresentation. Data collection was governed by the PharmaSafe Data Governance Board (reference: PSDGB-2025-001).

### 2.2 Provenance  `Art. 10(2)(b)`
Training data was collected from electronic prescribing and adverse event systems at eight EU hospitals: Amsterdam UMC, Radboudumc, Charité Berlin, Universitätsklinikum Freiburg, Hôpital Lariboisière Paris, Hôpital Pitié-Salpêtrière Paris, Erasmus MC, and LUMC. Data collection period: January 2019 – December 2024. All records processed under GDPR Article 9 data processing agreements with explicit institutional review board approval at each centre (IRB references on file: PSDGB-2025-001, Annex B). Drug records pseudonymised using EMA EudraVigilance encoding. Patient identifiers removed using ISO 29101-compliant de-identification pipeline. Data collection coordinated by PharmaSafe Data Governance Board.

### 2.3 Preprocessing  `Art. 10(2)(c)`
Drug names standardised to ATC fifth-level codes using WHO ATC Index 2024. Co-prescription pairs extracted from dispensing records with a 30-day co-occurrence window. DDI labels derived from validated clinical pharmacology databases (DrugBank v5.1, SIDER 4.1, EU SmPC annotations) and confirmed against hospital adverse event reports. Multi-source label reconciliation performed using majority-vote across three clinical pharmacologists per disputed pair (Fleiss κ = 0.84, strong agreement). Pairs with irreconcilable labels excluded (0.3%). Features include molecular fingerprints (Morgan, radius 2, 2048 bits), drug target interaction profiles from ChEMBL 33, and patient comorbidity vectors (ICD-11 encoded). Preprocessing pipeline fully documented in PharmaSafe Technical Report PSTR-2025-003.

### 2.4 Assumptions  `Art. 10(2)(d)`
The dataset assumes that DDI labels from reference databases and adverse event reports represent the clinically relevant interaction profile under standard EU hospital prescribing conditions. This assumption may not hold for newly approved drugs not yet represented in DrugBank or SPC annotations. The model is not intended for paediatric dosing; all training patients are adults (≥18 years). Post-market surveillance plan includes annual DDI label update cycle to address database currency. Key limitation: rare drug combinations (< 10 co-prescriptions in training data) are excluded from training and flagged with a low-confidence alert in deployment.

### 2.5 Suitability  `Art. 10(2)(e)`
The training dataset comprises 2,180,000 drug pair co-prescription events from 94,000 unique polypharmacy patients. Statistical power analysis (β = 0.8, α = 0.05) confirms this is sufficient for four-class DDI classification across all major ATC drug classes. Class sufficiency was verified per severity category: minor (n = 840,000), moderate (n = 760,000), major (n = 420,000), contraindicated (n = 160,000). Dataset sufficiency review: PSTR-2025-003, Section 3.

### 2.6 Bias examination  `Art. 10(2)(f)`
A pre-training bias audit was conducted across protected attributes: patient age group (18–50, 51–65, 65–80, 80+), sex (male/female/non-binary), nationality (Dutch, German, French, other EU, non-EU), and hospital type (academic/non-academic). The audit identified underrepresentation of patients aged 80+ (4.1% training vs. 9.8% target population estimate) and non-EU nationality patients (2.3% vs. 6.1%). No statistically significant underrepresentation was found for sex-based categories. Bias audit report: PSBA-2025-002. Interaction severity distribution across demographic subgroups documented in PSBA-2025-002, Table 4.

### 2.7 Bias mitigation  `Art. 10(2)(g)`
Three mitigation strategies applied. First, class-conditional oversampling (SMOTE) for patients aged 80+ to reach 8% of final training distribution. Second, importance re-weighting inversely proportional to nationality group frequency for non-EU patients. Third, a fairness-aware training objective (demographic parity regularisation, λ = 0.05) applied to prevent severity-class disparities by age and nationality. Post-mitigation audit confirmed sensitivity parity for major/contraindicated DDI classes within ±2% across all demographic subgroups. Full mitigation documentation: PSBM-2025-004.

### 2.8 Data gaps  `Art. 10(2)(h)`
Two primary gaps identified. First, insufficient coverage of drugs approved by EMA after January 2024 (48 drugs excluded). This gap is addressed via quarterly label updates from DrugBank API and EMA product database. Second, limited paediatric data (patients < 18, explicitly outside intended use scope). A tertiary gap is limited coverage of off-label prescribing patterns, documented in PSDG-2025-005. Gap documentation: PSDG-2025-005.

### 2.9 Relevance  `Art. 10(3)`
The training dataset directly represents all four DDI severity categories targeted by DrugInteract v1. Drug class coverage spans 87% of ATC fifth-level codes appearing in the intended deployment formularies. Validated against DDInter 2.0 benchmark (F1-macro = 0.88 on held-out DDInter test set, PSTR-2025-003, Section 6).

### 2.10 Representativeness  `Art. 10(3)`
Stratified sampling was applied across DDI severity class, patient age group, and ATC drug class. Post-mitigation training distribution compared against EMA EudraVigilance 2023 annual report population estimates. Chi-squared tests confirm no statistically significant deviation for severity class or age group distributions (p > 0.05). Nationality distribution remains residually underrepresented for non-EU patients (2.3% vs. 6.1% target) after mitigation; documented as a known limitation.

### 2.11 Statistical properties  `Art. 10(3)`
Severity class distribution: minor 38.5%, moderate 34.9%, major 19.3%, contraindicated 7.3%. Per-class feature distributions and inter-class correlation matrix documented in PSTR-2025-003, Table 5. Class imbalance for contraindicated category addressed via focal loss (γ = 2.5) and post-hoc threshold calibration.

### 2.12 Quality metrics  `Art. 10(3)`
Post-annotation quality review: label disagreement rate (pre-arbitration) 4.2%; post-arbitration exclusion rate 0.3%. Drug encoding error rate (ATC standardisation failures) 0.8%, corrected manually. Dataset completeness: 99.1% of co-prescription events passed all quality checks. Full quality metrics: PSQR-2025-006.

### 2.13 Contextual characteristics  `Art. 10(4)`
Training data originates from academic and non-academic EU hospital pharmacy environments across three EU member states (NL, DE, FR). Prescribing practices reflect EU hospital polypharmacy norms, primarily oncology, cardiology, and geriatric care settings. Non-EU prescribing patterns are not represented. Equipment and formulary differences across institutions captured via institution-level feature encoding.

---

## Section 3 — Validation Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 3.1 Design choices  `Art. 10(2)(a)`
A held-out validation split (12% of unique patients, stratified by DDI severity class and patient age group) was reserved prior to any model training. Patient-level splitting used to prevent leakage.

### 3.2 Provenance  `Art. 10(2)(b)`
Validation set originates from the same eight contributing hospitals as the training data, using records from 2023–2024 only (temporally separated from majority of training data).

### 3.3 Preprocessing  `Art. 10(2)(c)`
Identical preprocessing pipeline applied independently. ATC standardisation, feature extraction, and label reconciliation applied using training-set-derived parameters only.

### 3.4 Assumptions  `Art. 10(2)(d)`
The validation set is assumed to reflect the same clinical DDI distribution as the training data, as it is drawn from the same institutions and overlapping time window. Temporal generalisation is assessed separately on the independent test set.

### 3.5 Suitability  `Art. 10(2)(e)`
The validation dataset comprises 210,000 drug pair events from 11,280 unique patients. Sufficient for stable hyperparameter tuning and model architecture selection across all four severity classes.

### 3.6 Bias examination  `Art. 10(2)(f)`
Bias profile verified to match training set post-mitigation. Kolmogorov-Smirnov tests confirm demographic distributions are not significantly different from training (p > 0.1 for all attributes). Age and sex subgroup sensitivity scores verified in PSBA-2025-002, Appendix D.

### 3.7 Bias mitigation  `Art. 10(2)(g)`
Validation set inherits the same mitigation applied to training data (oversampling for 80+ patients, importance re-weighting for non-EU nationals). No separate mitigation pipeline applied to preserve evaluation integrity.

### 3.8 Data gaps  `Art. 10(2)(h)`
Same gaps as training set apply (EMA post-2024 drugs, off-label combinations). No additional gaps introduced by the validation split procedure.

### 3.9 Relevance  `Art. 10(3)`
Covers the same DDI severity scope, drug class distribution, and demographic range as the training set.

### 3.10 Representativeness  `Art. 10(3)`
Macro-averaged F1 on validation set: 0.88 across all four severity classes. Per-class and per-demographic-subgroup performance consistent with training set estimates (±2% F1 across age × sex combinations). Full statistics: PSTR-2025-003, Table 7.

### 3.11 Statistical properties  `Art. 10(3)`
Severity class distribution: minor 38.1%, moderate 35.4%, major 19.1%, contraindicated 7.4%. Distribution matches training set within 1% tolerance for all classes. PSTR-2025-003, Table 6.

### 3.12 Quality metrics  `Art. 10(3)`
Post-annotation label review: exclusion rate 0.28%; ATC encoding error rate 0.6%; dataset completeness 99.3%. Quality metrics: PSQR-2025-006, Section 4.

### 3.13 Contextual characteristics  `Art. 10(4)`
Same institutional and regulatory context as training data. All records from EU hospital pharmacy environments in NL, DE, and FR.

---

## Section 4 — Testing Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 4.1 Design choices  `Art. 10(2)(a)`
An independent test set was constructed from two hospitals not contributing to training or validation: UZ Leuven (Belgium) and Karolinska Universitetssjukhuset (Sweden). Provides geographic, institutional, and formulary independence from the training distribution.

### 4.2 Provenance  `Art. 10(2)(b)`
Data from UZ Leuven (IRB-UZL-2025-009) and Karolinska Universitetssjukhuset (IRB-KAR-2025-014). Records cover 2024 only. No overlap with training or validation institutions. Swedish data introduces a non-training-country context, assessed for generalisation.

### 4.3 Preprocessing  `Art. 10(2)(c)`
Identical preprocessing pipeline applied by a separate data engineer with no access to training data. ATC standardisation applied using same WHO ATC Index 2024 reference. Normalisation parameters inherited from training data only.

### 4.4 Assumptions  `Art. 10(2)(d)`
The test set is intended to represent unseen real-world deployment conditions, including variation in hospital formulary, national prescribing guidelines (Belgian and Swedish vs. Dutch/German/French training context), and EHR system vendor.

### 4.5 Suitability  `Art. 10(2)(e)`
The test dataset comprises 64,000 drug pair events from 3,100 unique patients. Statistical power analysis confirms this is sufficient for detecting F1-macro differences of ≥ 2% at β = 0.8.

### 4.6 Bias examination  `Art. 10(2)(f)`
Bias profile independently verified by a third-party clinical pharmacology auditor. Per-subgroup sensitivity for major/contraindicated DDI classes: age ≥ 0.85 across all age groups; sex ≥ 0.86 for all categories. Full bias verification report: PSTR-2025-003, Appendix E.

### 4.7 Bias mitigation  `Art. 10(2)(g)`
No bias mitigation applied to test set to preserve benchmark integrity. This is a deliberate decision documented in PSTR-2025-003, Appendix E.

### 4.8 Data gaps  `Art. 10(2)(h)`
Swedish formulary includes three drugs not represented in training data; these pairs are flagged with low-confidence alerts in deployment and excluded from primary performance metrics. Documented as an additional test condition in PSDG-2025-005, Addendum 1.

### 4.9 Relevance  `Art. 10(3)`
Covers the same DDI severity categories under independent institutional and national acquisition conditions. Swedish context provides evidence of cross-national generalisation.

### 4.10 Representativeness  `Art. 10(3)`
System F1-macro on test set: 0.87 (95% CI: 0.85–0.89). Performance consistent across all demographic subgroups. Belgian and Swedish subsets show equivalent performance (F1-macro 0.87 and 0.86 respectively). Full evaluation: PSTR-2025-003.

### 4.11 Statistical properties  `Art. 10(3)`
Severity class distribution: minor 37.4%, moderate 35.8%, major 19.9%, contraindicated 6.9%. Distribution and variance statistics: PSTR-2025-003, Table 8.

### 4.12 Quality metrics  `Art. 10(3)`
Label disagreement rate: 0.19%; ATC encoding error rate: 0.5%; dataset completeness: 99.6%. Quality metrics: PSQR-2025-006, Section 5.

### 4.13 Contextual characteristics  `Art. 10(4)`
Test data spans hospitals in Belgium and Sweden, introducing national prescribing practice variation and a non-training-country EU context. Swedish national formulary (LFN) and Belgian RIZIV reimbursement context differ from training countries, providing evidence of regulatory-context generalisation.
