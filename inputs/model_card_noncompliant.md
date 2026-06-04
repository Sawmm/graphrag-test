# HireScore v1.0 — Non-Compliant Data Governance Documentation

## Document metadata
- **System ID:** hirescore-v1.0
- **Organisation:** TalentPro Analytics GmbH, Berlin, Germany
- **System type:** High-risk AI system (EU AI Act Annex III, §4 — employment and workers management)
- **Intended purpose:** Automated ranking and shortlisting of job applicants based on CV text, work history, and assessment scores.
- **Version:** 1.0.0
- **Date:** January 2026
- **Purpose:** Compliance verification test — verify pipeline reports NON-COMPLIANT

---

## Section 1 — System Overview

- **System name and version:** HireScore v1.0, version 1.0.0
- **Intended purpose / task:** Machine learning system that processes structured and unstructured applicant data (CV text, work history, assessment responses) and produces a ranked shortlist and a suitability score (0–100) for each applicant. Output is provided to HR managers as a decision-support tool.
- **High-risk category (Annex III ref.):** Annex III §4 — AI systems intended to be used for recruitment or selection of natural persons, in particular for advertising vacancies, screening or filtering applications.
- **Intended users / deployers:** HR managers and recruitment teams at EU client organisations. Intended for EU clients in finance, logistics, and retail sectors.
- **Geographic / regulatory scope:** EU deployment. Training data from five German-based client organisations.

---

## Section 2 — Training Dataset

### 2.1 Design choices  `Art. 10(2)(a)`

The training dataset was compiled from historical hiring records across five client organisations collected over a five-year period (2018–2022). Records include structured fields (education level, years of experience, assessment scores) and unstructured text (CV summaries).

### 2.2 Provenance  `Art. 10(2)(b)`

Data was collected from internal HR systems of five participating client organisations under data processing agreements. Collection methodology and consent procedures are documented in internal records but not published here for commercial confidentiality reasons.

### 2.3 Preprocessing  `Art. 10(2)(c)`

CV text was tokenised using a pre-trained tokeniser. Assessment scores were normalised to a 0–1 scale. Missing values in structured fields were imputed using column means.

### 2.4 Assumptions  `Art. 10(2)(d)`

The dataset assumes that historical hiring decisions by the participating organisations are reasonable proxies for candidate suitability. This assumption may not hold if historical hiring practices contained systematic biases.

### 2.5 Suitability  `Art. 10(2)(e)`

The training dataset contains 95,000 application records across 12 job categories. The dataset was considered sufficient for the initial product release based on internal review.

*Bias examination:* No formal bias examination was performed on the training data prior to model deployment. No protected attribute analysis was conducted and no audit report exists.

*Bias mitigation:* No bias mitigation measures were applied to the training dataset. The training labels directly reflect historical hiring decisions without adjustment for potential discriminatory patterns.

*Data gaps:* No systematic data gap analysis was performed. The training data is limited to five German-based organisations.

### 2.6 Relevance  `Art. 10(3)`

The dataset is relevant to the intended task of candidate ranking as it directly consists of real hiring outcomes for comparable job roles.

### 2.7 Statistical properties  `Art. 10(3)`

Class distribution (hired vs. not hired): 18% positive (hired), 82% negative. Distribution statistics were computed during preprocessing but are not included in this model card.

### 2.8 Quality metrics  `Art. 10(3)`

Data completeness: approximately 91% of records have all structured fields populated. Annotation quality review not performed.

### 2.9 Contextual characteristics  `Art. 10(4)`

All training data originates from German-based organisations operating in sectors including finance, logistics, and retail. Deployment is intended for EU clients in comparable sectors.

---

## Section 3 — Validation Dataset

### 3.1 Design choices  `Art. 10(2)(a)`

A 20% random split of the training data was used as the validation set. No patient-level or time-based splitting was applied.

### 3.2 Provenance  `Art. 10(2)(b)`

Same source organisations as training data.

### 3.3 Preprocessing  `Art. 10(2)(c)`

Same preprocessing pipeline as training data.

### 3.4 Assumptions  `Art. 10(2)(d)`

The validation set is assumed to be representative of the deployment distribution. The validity of this assumption is uncertain given the random split methodology.

### 3.5 Suitability  `Art. 10(2)(e)`

18,000 records were used for validation. This was considered sufficient for monitoring model convergence during training.

*Bias examination:* No formal bias examination was performed on the validation dataset prior to model deployment.

*Bias mitigation:* No bias mitigation measures were applied to the validation dataset.

*Data gaps:* No systematic data gap analysis was performed on the validation dataset.

### 3.6 Relevance  `Art. 10(3)`

Same scope as training data.

*Representativeness:* No formal representativeness analysis was performed on the validation dataset.

### 3.7 Contextual characteristics  `Art. 10(4)`

Same contextual characteristics as training data.

---

## Section 4 — Performance Evaluation

No independent testing dataset was constructed prior to deployment. Model performance was assessed using cross-validation on the training data only. No held-out test set from separate organisations or time periods was used.

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

The system processes demographic data including applicant names, ages, and location data, which may constitute or serve as proxies for special category personal data under GDPR Article 9 (e.g., ethnic origin may be inferred from names). The provider acknowledges that processing this data for bias analysis may be necessary to detect and correct potential discriminatory outputs.

The system's bias correction capability is under development. At the time of this model card, no specific measures have been implemented for the detection or correction of bias in relation to protected characteristics.

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
| bias_examination | 10(2)(f) | not satisfied |
| bias_mitigation | 10(2)(g) | not satisfied |
| data_gaps | 10(2)(h) | not satisfied |
| relevance | 10(3) | satisfied |
| representativeness | 10(3) | not satisfied |
| statistical_props | 10(3) | satisfied |
| quality_metrics | 10(3) | satisfied |
| contextual_characteristics | 10(4) | satisfied |

**Training obligations satisfied (count):** 9 / 13

### Validation dataset obligations
| Obligation | §ref | Status |
|---|---|---|
| design_choices | 10(2)(a) | satisfied |
| provenance | 10(2)(b) | satisfied |
| preprocessing | 10(2)(c) | satisfied |
| assumptions | 10(2)(d) | satisfied |
| suitability | 10(2)(e) | satisfied |
| bias_examination | 10(2)(f) | not satisfied |
| bias_mitigation | 10(2)(g) | not satisfied |
| data_gaps | 10(2)(h) | not satisfied |
| relevance | 10(3) | satisfied |
| representativeness | 10(3) | not satisfied |
| statistical_props | 10(3) | not satisfied |
| quality_metrics | 10(3) | not satisfied |
| contextual_characteristics | 10(4) | satisfied |

**Validation obligations satisfied (count):** 7 / 13

### Testing dataset obligations
| Obligation | §ref | Status |
|---|---|---|
| (all) | 10(1)–10(4) | not satisfied — no testing dataset |

**Testing obligations satisfied (count):** 0 / 13

### Overall verdict
- **Expected compliance:** `no`
  *(training 9/13, validation 7/13, testing 0/13 — missing bias examination, bias mitigation, data gaps, representativeness; no independent testing dataset)*
