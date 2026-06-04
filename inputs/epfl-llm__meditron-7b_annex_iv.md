# Annex IV Normalization — Article 10 Data Governance
<!-- Copy this file to normalized/<model_id>_annex_iv.md and fill in each field.
     Leave a field blank if the source card contains no relevant information.
     Do NOT invent content — only restructure what is actually in the raw card. -->

## Document metadata
- **HuggingFace ID:** epfl-llm/meditron-7b
- **Source card file:** `raw/epfl-llm__meditron-7b.md`
- **Normalized by:** Claude
- **Date normalized:** 2026-05-17
- **Second annotator:**
- **Date second-annotated:**

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** Meditron-7B v1.0
- **Intended purpose / task:** Medical large language model for clinical decision-making support; use cases include medical exam question answering, supporting differential diagnosis, disease information queries, and general health information queries.
- **High-risk category (Annex III ref.):**  Annex III §5 — AI in medical devices / health applications
- **Intended users / deployers:** Healthcare professionals, researchers; further testing and assessment as AI assistant to enhance clinical decision-making and healthcare access.
- **Geographic / regulatory scope:** Not addressed in model card.

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
> Why was this dataset chosen for this purpose? Selection criteria, intended coverage, scope.

The GAP-Replay corpus was assembled to adapt Llama-2-7B to the medical domain through continued pretraining. It combines four corpora: Clinical Guidelines (internationally-recognized clinical practice guidelines), Medical Paper Abstracts (PubMed/PubMed Central), Medical Papers (full-text PubMed/PubMed Central articles), and general-domain Replay Data (from RedPajama-v1). The corpus totals 48.1B tokens. General-domain replay data (400M tokens) was included to prevent catastrophic forgetting of general language knowledge.

### 2.2 Provenance  `Art. 10(2)(b)`
> Origin of the data — where it came from, how collected, institutions involved, legal/consent basis.

- **Clinical Guidelines:** A new dataset of 46K internationally-recognized clinical practice guidelines from various healthcare-related sources, including hospitals and international organizations (published as `epfl-llm/guidelines` on HuggingFace).
- **Medical Paper Abstracts:** 16.1M abstracts extracted from closed-access PubMed and PubMed Central papers.
- **Medical Papers:** Full-text articles extracted from 5M publicly available PubMed and PubMed Central papers.
- **Replay Data:** 400M tokens sampled from RedPajama-v1 (`togethercomputer/RedPajama-Data-1T`).

Legal/consent basis and collection methodology beyond the sources listed are not addressed in the model card; details referred to the associated paper.

### 2.3 Preprocessing  `Art. 10(2)(c)`
> Cleaning, filtering, annotation, labelling, augmentation, and other transformations applied.

The model card states: "Please see the detailed preprocessing procedure in our paper." No further preprocessing details are provided in the card itself.

### 2.4 Assumptions  `Art. 10(2)(d)`
> What does the dataset claim to represent? Stated limitations of that representation.

The corpus is described as "comprehensively curated" medical training data intended to represent the medical domain. The card notes that the model encodes "medical knowledge from sources of high-quality evidence" but acknowledges the model is "not yet adapted to deliver this knowledge appropriately, safely, or within professional actionable constraints." Knowledge cutoff is August 2023.

### 2.5 Suitability  `Art. 10(2)(e)`
> Size, coverage, and any explicit fitness-for-purpose assessment.

The corpus contains 48.1B tokens across four components. The card notes the model has been evaluated against medical benchmarks (MedQA, MedMCQA, PubMedQA, MMLU-Medical, MedQA-4-Option) and outperforms Llama-2-7B and PMC-Llama on multiple medical reasoning tasks. However, the card explicitly warns against deployment in medical applications without further alignment and testing, indicating the suitability assessment is incomplete.

### 2.6 Bias examination  `Art. 10(2)(f)`
> Protected attributes examined, methodology used, findings reported.

The card states: "Significant research is still required to fully explore potential bias, fairness, and safety issues with this language model. Please recognize that our evaluation on Meditron-7B's helpfulness, risk, and bias are highly limited." No specific bias examination methodology or findings are reported for the training data.

### 2.7 Bias mitigation  `Art. 10(2)(g)`
> Measures taken (resampling, re-weighting, etc.) — or documented decision not to mitigate.

Not addressed in model card. The card only acknowledges that bias has not been sufficiently examined.

### 2.8 Data gaps  `Art. 10(2)(h)`
> Known shortcomings, coverage gaps, how they were addressed or acknowledged.

The card notes the model is "not yet adapted to deliver this knowledge appropriately, safely, or within professional actionable constraints" and that bias, fairness, and safety issues remain underexplored. The Replay Data component (general domain) is included specifically to address catastrophic forgetting, implying awareness of coverage limitations from domain-specific training. No specific data gaps in the medical corpus are enumerated.

### 2.9 Relevance  `Art. 10(3)`
> Fitness-for-purpose statement — why this dataset is appropriate for the intended task.

The corpus is designed specifically to support medical domain adaptation. The inclusion of clinical guidelines, PubMed abstracts, and full-text medical papers is described as targeting medical knowledge required for clinical decision-support use cases.

### 2.10 Representativeness  `Art. 10(3)`
> Subgroup coverage — demographic, geographic, clinical, or other relevant breakdowns.

Not addressed in model card. No information on demographic, geographic, or clinical subgroup coverage of the training corpus.

### 2.11 Statistical properties  `Art. 10(3)`
> Class distribution, variance, inter-class correlation, or other quantitative characteristics.

Total token count: 48.1B. Component breakdown: Clinical Guidelines (~46K documents), Medical Paper Abstracts (16.1M abstracts), Medical Papers (5M full-text articles), Replay Data (400M tokens). No further statistical distribution or balance information is provided.

### 2.12 Quality metrics  `Art. 10(3)`
> Completeness, error rates, annotation consistency, or other quality measures.

The clinical guidelines dataset is described as "internationally-recognized" and the medical papers as sourced from PubMed/PubMed Central. No formal quality metrics (completeness, error rates, annotation consistency) are reported; details referred to the paper.

### 2.13 Contextual characteristics  `Art. 10(4)`
> Deployment environment — geographic scope, clinical setting, equipment, patient population.

Not addressed in model card with respect to training data context. The model is intended for English-language medical use. The training data includes international clinical guidelines and US/global PubMed literature, but no specific contextual deployment characteristics are described for the training set.

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

### 4.1 Design choices  `Art. 10(2)(a)`
The testing benchmarks were selected to evaluate medical reasoning performance. Five benchmarks are used: MedQA (USMLE), MedMCQA, PubMedQA, MMLU-Medical, and MedQA-4-Option. These are standard, publicly available medical NLP benchmarks.

### 4.2 Provenance  `Art. 10(2)(b)`
- MedQA (USMLE): `bigbio/med_qa` on HuggingFace
- MedMCQA: `medmcqa` on HuggingFace
- PubMedQA: `bigbio/pubmed_qa` on HuggingFace
- MMLU-Medical: `lukaemon/mmlu` on HuggingFace
- MedQA-4-Option: `GBaker/MedQA-USMLE-4-options` on HuggingFace

### 4.3 Preprocessing  `Art. 10(2)(c)`
Not addressed in model card beyond the use of "top token selection as the inference mode" for finetuned evaluation and in-context learning with k=3 or 5 demonstrations for few-shot evaluation. One-shot evaluation used for 7B models on TruthfulQA; zero-shot for 70B models.

### 4.4 Assumptions  `Art. 10(2)(d)`
The benchmarks are used as proxies for medical reasoning ability. MMLU-Medical evaluation uses models finetuned on MedMCQA; MedQA-4-Option uses models finetuned on MedQA. The TruthfulQA evaluation focuses on categories relevant to the medical domain (Health, Nutrition, Psychology, Science).

### 4.5 Suitability  `Art. 10(2)(e)`
Five benchmarks are used to measure multiple aspects of medical performance. The card notes that for a "more detailed performance analysis, please see our paper," indicating the card provides only a summary. Results show Meditron-7B achieves 57.5% average accuracy across benchmarks, outperforming Llama-2-7B (52.7%) and PMC-LLaMA (53.0%).

### 4.6 Bias examination  `Art. 10(2)(f)`
TruthfulQA evaluation is performed across health-relevant categories (Health, Nutrition, Psychology, Science) as a form of truthfulness assessment. No systematic bias examination of the test sets themselves is reported.

### 4.7 Bias mitigation  `Art. 10(2)(g)`
Not addressed in model card.

### 4.8 Data gaps  `Art. 10(2)(h)`
Not addressed in model card. The card does not discuss what aspects of medical performance are not covered by the selected benchmarks.

### 4.9 Relevance  `Art. 10(3)`
The benchmarks are standard medical NLP evaluation datasets directly relevant to the intended use cases (medical question answering, clinical reasoning). They are described as measuring "medical reasoning tasks."

### 4.10 Representativeness  `Art. 10(3)`
Not addressed in model card. No discussion of demographic or clinical subgroup coverage within the test sets.

### 4.11 Statistical properties  `Art. 10(3)`
Accuracy metric used across all benchmarks. Results reported as single accuracy values per dataset/model combination.

### 4.12 Quality metrics  `Art. 10(3)`
Benchmarks are publicly established datasets. No independent quality assessment of the test data is reported.

### 4.13 Contextual characteristics  `Art. 10(4)`
The test benchmarks are primarily US-centric (USMLE-based) with some biomedical literature-based tasks (PubMedQA). No contextual deployment characteristics are discussed.

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

- **Processes sensitive data for bias correction:** `no`

*(The training data consists of published medical literature, clinical guidelines, and general web text. No processing of personal health data for bias correction purposes is described.)*

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
| provenance | 10(2)(b) | partial | | |
| preprocessing | 10(2)(c) | partial | | |
| assumptions | 10(2)(d) | partial | | |
| suitability | 10(2)(e) | partial | | |
| bias_examination | 10(2)(f) | not_satisfied | | |
| bias_mitigation | 10(2)(g) | not_satisfied | | |
| data_gap | 10(2)(h) | partial | | |
| relevance | 10(3) | partial | | |
| representativeness | 10(3) | not_satisfied | | |
| statistical_props | 10(3) | partial | | |
| quality_metrics | 10(3) | partial | | |
| contextual_characteristics | 10(4) | not_satisfied | | |

**Training obligations satisfied (count):** 5.0 / 13 &nbsp;*(partial = 0.5)*

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
| design_choices | 10(2)(a) | satisfied | | |
| provenance | 10(2)(b) | satisfied | | |
| preprocessing | 10(2)(c) | partial | | |
| assumptions | 10(2)(d) | partial | | |
| suitability | 10(2)(e) | partial | | |
| bias_examination | 10(2)(f) | partial | | |
| bias_mitigation | 10(2)(g) | not_satisfied | | |
| data_gap | 10(2)(h) | not_satisfied | | |
| relevance | 10(3) | satisfied | | |
| representativeness | 10(3) | not_satisfied | | |
| statistical_props | 10(3) | partial | | |
| quality_metrics | 10(3) | partial | | |
| contextual_characteristics | 10(4) | partial | | |

**Testing obligations satisfied (count):** 6.5 / 13 &nbsp;*(partial = 0.5)*

### Overall verdict
- **Compliant:** `no`
  *(Training score = 5.0/13, below threshold of 10/13; Validation score = 0/13, below threshold of 8/13)*
- **Annotator notes:** The model card is strong on training data composition and test benchmark citation, but provides minimal information about validation data, bias assessment, preprocessing details, and data quality metrics. Many details are deferred to the associated paper rather than addressed in the card itself.
