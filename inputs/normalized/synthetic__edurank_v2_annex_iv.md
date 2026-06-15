# Annex IV Normalization — Article 10 Data Governance
<!-- Synthetic model card for diversity testing — bias fields present but inadequate. -->

## Document metadata
- **System ID:** edurank-v2
- **Organisation:** LearnPath Technologies SL, Barcelona, Spain
- **System type:** High-risk AI system (EU AI Act Annex III, §3(b) — education and vocational training)
- **Intended purpose:** Automated scoring and ranking of student coursework submissions in EU higher education institutions to support grading and scholarship allocation decisions.
- **Version:** 2.1.0
- **Date:** March 2026
- **Normalized by:** Synthetic (compliance testing)
- **Date normalized:** 2026-06-15

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** EduRank v2, version 2.1.0
- **Intended purpose / task:** NLP-based automated assessment system that evaluates written coursework submissions and produces a quality score (0–100) and a performance band (fail/pass/merit/distinction). Outputs are provided to academic staff as a grading support tool; final grade assignment requires human educator sign-off.
- **High-risk category (Annex III ref.):** Annex III §3(b) — AI systems intended to be used for the purpose of determining access to educational and vocational training institutions or to evaluate persons within these institutions.
- **Intended users / deployers:** Academic staff and assessment coordinators at EU universities and higher education institutions.
- **Geographic / regulatory scope:** EU deployment. Training data from Spanish, Italian, and French universities.

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
The training dataset was designed to cover all four performance bands (fail/pass/merit/distinction) across eight academic disciplines (engineering, social sciences, law, medicine, humanities, natural sciences, business, and education). Selection criteria required (a) institutional provenance from accredited EU universities, (b) expert human grader annotations with inter-rater reliability verification, (c) balanced representation of performance bands within each discipline, and (d) student-level separation from validation and test splits to prevent data leakage. Data collection coordinated by the EduRank Academic Partnership Consortium (reference: EAPC-2025-001).

### 2.2 Provenance  `Art. 10(2)(b)`
Training data was collected from eight partner universities: Universitat de Barcelona, Universitat Autònoma de Barcelona, Università di Bologna, Sapienza Università di Roma, Université Paris 1 Panthéon-Sorbonne, Université de Lyon 2, Universitat Politècnica de Catalunya, and Scuola Normale Superiore. All submissions collected under student data consent frameworks compliant with GDPR Article 6(1)(a) and institutional ethical review. Submissions pseudonymised prior to data transfer; student identifiers retained only by originating institutions under the data processing agreements. Data collection period: 2020–2025. IRB approvals on file: EAPC-2025-001, Annex A.

### 2.3 Preprocessing  `Art. 10(2)(c)`
Submissions normalised to UTF-8 encoding. Language detection applied; non-target-language submissions (< 0.2% of data) excluded. Text tokenised using multilingual BERT tokeniser (bert-base-multilingual-cased). Submissions truncated to 4,096 tokens. Expert grader annotations provided by minimum two graders per submission, with a third grader arbitrating disagreements exceeding 10 band points. Inter-rater reliability: Quadratic Weighted Kappa (QWK) = 0.83 across the annotator pool. Preprocessing pipeline documented in EduRank Technical Report ERTR-2025-002.

### 2.4 Assumptions  `Art. 10(2)(d)`
The dataset assumes that expert human grades from participating institutions represent a fair and consistent standard of academic assessment for the target disciplines. This assumption may not hold where institutional grading norms differ substantially across EU countries. The model is not intended for primary school or secondary education contexts; all training submissions are from tertiary-level students (age ≥ 18). The dataset further assumes that pseudonymised submissions do not contain personally identifiable information beyond what is unavoidable in the content of academic work.

### 2.5 Suitability  `Art. 10(2)(e)`
The training dataset comprises 1,240,000 graded submissions from 78,000 unique students across eight disciplines. Statistical power analysis (β = 0.8, α = 0.05) confirms this volume is sufficient for four-class ordinal classification across all disciplines and demographic subgroups. Per-discipline dataset sizes verified to exceed minimum sufficiency thresholds (minimum 80,000 submissions per discipline). Dataset sufficiency review: ERTR-2025-002, Section 3.

### 2.6 Bias examination  `Art. 10(2)(f)`
The dataset was examined for potential bias. Analysis was conducted across student gender and nationality. No formal protected attribute analysis or statistical disparity testing was performed; the team reviewed score distributions visually and did not observe obvious patterns. No audit report was produced.

### 2.7 Bias mitigation  `Art. 10(2)(g)`
Fairness considerations were incorporated during model development. The team applied standard regularisation techniques and reviewed model outputs for fairness during internal testing. No formal bias mitigation methodology (e.g., re-weighting, adversarial debiasing, or fairness constraints) was applied, and no documentation of specific mitigation measures exists.

### 2.8 Data gaps  `Art. 10(2)(h)`
The primary identified gap is underrepresentation of submissions from students at institutions outside the eight partner universities. A secondary gap is limited coverage of STEM disciplines in languages other than Spanish and Italian. The gap in postgraduate versus undergraduate submission mix is noted but not quantified. Full gap documentation: ERDG-2025-003.

### 2.9 Relevance  `Art. 10(3)`
The training dataset directly represents the academic assessment task, covering all eight target disciplines and four performance bands. Validated against a held-out benchmark of externally graded submissions (QWK = 0.81, ERTR-2025-002, Section 6).

### 2.10 Representativeness  `Art. 10(3)`
Stratified sampling applied across discipline, performance band, and institutional source. Training set distribution compared against EAPC partner university enrolment statistics. Chi-squared tests confirm no statistically significant deviation for discipline or performance band distributions (p > 0.05). Gender and nationality distributions not formally verified against population estimates.

### 2.11 Statistical properties  `Art. 10(3)`
Performance band distribution: fail 11.2%, pass 34.8%, merit 38.4%, distinction 15.6%. Per-discipline label distributions documented in ERTR-2025-002, Table 4. Class imbalance addressed using class-weight adjustment during training.

### 2.12 Quality metrics  `Art. 10(3)`
Inter-rater QWK = 0.83 across annotator pool. Annotation exclusion rate: 0.6% (irreconcilable disagreements). Dataset completeness: 99.2% of submissions passed all quality checks. Full quality metrics: ERQR-2025-004.

### 2.13 Contextual characteristics  `Art. 10(4)`
Training data originates from tertiary educational institutions in Spain, Italy, and France. Academic assessment conventions, language, and disciplinary norms reflect Western European higher education contexts. Non-EU academic norms are not represented.

---

## Section 3 — Validation Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 3.1 Design choices  `Art. 10(2)(a)`
A held-out validation split (12% of unique students, stratified by discipline and performance band) was reserved prior to any model training. Student-level splitting used to prevent leakage.

### 3.2 Provenance  `Art. 10(2)(b)`
Validation set originates from the same eight partner universities as training data, using submissions from 2024–2025 academic year.

### 3.3 Preprocessing  `Art. 10(2)(c)`
Identical preprocessing pipeline applied independently. Tokenisation and normalisation parameters inherited from training data.

### 3.4 Assumptions  `Art. 10(2)(d)`
The validation set is assumed to reflect the same academic assessment distribution as the training data, drawn from the same institutions and overlapping academic standards.

### 3.5 Suitability  `Art. 10(2)(e)`
The validation dataset comprises 148,800 submissions from 9,360 unique students, sufficient for stable hyperparameter tuning and model selection.

### 3.6 Bias examination  `Art. 10(2)(f)`
Informal review of validation set score distributions by gender and nationality was performed. No significant patterns were observed. No formal statistical analysis or disparity testing was conducted on the validation split.

### 3.7 Bias mitigation  `Art. 10(2)(g)`
Validation set used for evaluation only. No bias mitigation applied to preserve evaluation integrity.

### 3.8 Data gaps  `Art. 10(2)(h)`
Same gaps as training set apply. No additional gaps introduced by the validation split procedure.

### 3.9 Relevance  `Art. 10(3)`
Covers the same discipline and performance band scope as the training set.

### 3.10 Representativeness  `Art. 10(3)`
Stratification confirmed the validation set follows the same performance band distribution as training within 2% tolerance. Macro-averaged QWK on validation: 0.82. Per-discipline performance consistent (QWK 0.79–0.85). ERTR-2025-002, Table 6.

### 3.11 Statistical properties  `Art. 10(3)`
Performance band distribution: fail 11.5%, pass 34.3%, merit 38.9%, distinction 15.3%. Distribution matches training within 1% for all classes. ERTR-2025-002, Table 5.

### 3.12 Quality metrics  `Art. 10(3)`
Inter-rater QWK = 0.82; annotation exclusion rate 0.5%; dataset completeness 99.4%. ERQR-2025-004, Section 4.

### 3.13 Contextual characteristics  `Art. 10(4)`
Same institutional and national context as training data. All submissions from Spanish, Italian, and French universities.

---

## Section 4 — Testing Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 4.1 Design choices  `Art. 10(2)(a)`
An independent test set was constructed from two universities not contributing to training or validation: Vrije Universiteit Amsterdam (Netherlands) and Lund University (Sweden). Provides institutional and national context independence.

### 4.2 Provenance  `Art. 10(2)(b)`
Data from VU Amsterdam (IRB-VUA-2025-004) and Lund University (IRB-LU-2025-011). Submissions from 2024–2025. No overlap with training or validation institutions.

### 4.3 Preprocessing  `Art. 10(2)(c)`
Identical preprocessing pipeline applied by a separate data engineer with no access to training data. Multilingual BERT tokeniser applied using same configuration.

### 4.4 Assumptions  `Art. 10(2)(d)`
The test set is intended to represent unseen deployment conditions, including variation in academic tradition, grading conventions, and submission language (Dutch and Swedish in addition to Spanish, Italian, French).

### 4.5 Suitability  `Art. 10(2)(e)`
The test dataset comprises 41,000 submissions from 2,600 unique students. Statistical power analysis confirms this is sufficient for detecting QWK differences of ≥ 2% at β = 0.8.

### 4.6 Bias examination  `Art. 10(2)(f)`
Informal review of test set score distributions by gender was performed. No formal statistical disparity analysis was conducted across protected attributes.

### 4.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 4.8 Data gaps  `Art. 10(2)(h)`
not provided

### 4.9 Relevance  `Art. 10(3)`
Covers the same eight disciplines under independent institutional and national acquisition conditions.

### 4.10 Representativeness  `Art. 10(3)`
System QWK on test set: 0.80 (95% CI: 0.78–0.82). Dutch and Swedish submissions show slightly lower performance (QWK 0.78) than Spanish/Italian/French baseline. ERTR-2025-002, Appendix D.

### 4.11 Statistical properties  `Art. 10(3)`
Performance band distribution on test set: fail 12.1%, pass 35.6%, merit 37.8%, distinction 14.5%. ERTR-2025-002, Table 8.

### 4.12 Quality metrics  `Art. 10(3)`
Inter-rater QWK = 0.81; annotation exclusion rate 0.4%; dataset completeness 99.5%. ERQR-2025-004, Section 5.

### 4.13 Contextual characteristics  `Art. 10(4)`
Test data spans Netherlands and Sweden, introducing academic traditions distinct from the Spanish/Italian/French training context. Dutch and Swedish submission languages tested for multilingual generalisation.
