# Annex IV Normalization — Article 10 Data Governance
<!-- Copy this file to normalized/<model_id>_annex_iv.md and fill in each field.
     Leave a field blank if the source card contains no relevant information.
     Do NOT invent content — only restructure what is actually in the raw card. -->

## Document metadata
- **HuggingFace ID:** allenai/biomed_roberta_base
- **Source card file:** `raw/allenai__biomed_roberta_base.md`
- **Normalized by:** Claude
- **Date normalized:** 2026-05-17
- **Second annotator:**
- **Date second-annotated:**

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** BioMed-RoBERTa-base
- **Intended purpose / task:** Domain-adaptive language model pre-trained for biomedical NLP tasks including text classification, relation extraction, and named entity recognition.
- **High-risk category (Annex III ref.):**  Not addressed in model card.
- **Intended users / deployers:** NLP researchers and practitioners working in the biomedical domain.
- **Geographic / regulatory scope:** Not addressed in model card.

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
> Why was this dataset chosen for this purpose? Selection criteria, intended coverage, scope.

The model was adapted to the biomedical domain using 2.68 million scientific papers from the Semantic Scholar corpus. Full text of papers (not just abstracts) was used. The dataset was selected to provide broad biomedical domain coverage for continued pretraining of RoBERTa-base. Details of selection criteria are referred to Gururangan et al., 2020.

### 2.2 Provenance  `Art. 10(2)(b)`
> Origin of the data — where it came from, how collected, institutions involved, legal/consent basis.

The training data consists of 2.68 million scientific papers from the Semantic Scholar corpus (Allen Institute for AI). The dataset amounts to 7.55B tokens and 47GB of data. No further information on collection methodology, legal basis, or consent is provided in the model card.

### 2.3 Preprocessing  `Art. 10(2)(c)`
> Cleaning, filtering, annotation, labelling, augmentation, and other transformations applied.

The model card states that details of the adaptive pretraining procedure can be found in Gururangan et al., 2020. No preprocessing steps are described in the model card itself beyond the use of full paper text rather than abstracts only.

### 2.4 Assumptions  `Art. 10(2)(d)`
> What does the dataset claim to represent? Stated limitations of that representation.

Not addressed in model card.

### 2.5 Suitability  `Art. 10(2)(e)`
> Size, coverage, and any explicit fitness-for-purpose assessment.

The corpus consists of 2.68 million scientific papers, 7.55B tokens, 47GB of data. The model achieves competitive performance compared to state-of-the-art models on several biomedical NLP tasks (RCT-180K, ChemProt, JNLPBA, BC5CDR, NCBI-Disease), which is offered as implicit evidence of suitability. No explicit fitness-for-purpose statement is made.

### 2.6 Bias examination  `Art. 10(2)(f)`
> Protected attributes examined, methodology used, findings reported.

Not addressed in model card.

### 2.7 Bias mitigation  `Art. 10(2)(g)`
> Measures taken (resampling, re-weighting, etc.) — or documented decision not to mitigate.

Not addressed in model card.

### 2.8 Data gaps  `Art. 10(2)(h)`
> Known shortcomings, coverage gaps, how they were addressed or acknowledged.

Not addressed in model card.

### 2.9 Relevance  `Art. 10(3)`
> Fitness-for-purpose statement — why this dataset is appropriate for the intended task.

The model card implicitly asserts relevance through the domain match: biomedical scientific papers from Semantic Scholar are used to adapt a general language model to the biomedical domain. No explicit relevance statement is made.

### 2.10 Representativeness  `Art. 10(3)`
> Subgroup coverage — demographic, geographic, clinical, or other relevant breakdowns.

Not addressed in model card.

### 2.11 Statistical properties  `Art. 10(3)`
> Class distribution, variance, inter-class correlation, or other quantitative characteristics.

The dataset comprises 2.68 million papers, 7.55B tokens, 47GB. No further breakdown of content distribution or statistical properties is provided.

### 2.12 Quality metrics  `Art. 10(3)`
> Completeness, error rates, annotation consistency, or other quality measures.

Not addressed in model card.

### 2.13 Contextual characteristics  `Art. 10(4)`
> Deployment environment — geographic scope, clinical setting, equipment, patient population.

Not addressed in model card.

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
Five downstream NLP benchmark datasets are used for evaluation: RCT-180K (text classification), ChemProt (relation extraction), JNLPBA (NER), BC5CDR (NER), and NCBI-Disease (NER). These represent standard biomedical NLP benchmarks.

### 4.2 Provenance  `Art. 10(2)(b)`
The card names the five benchmark datasets but provides no repository links, paper citations, or further provenance information for the evaluation sets.

### 4.3 Preprocessing  `Art. 10(2)(c)`
Not addressed in model card.

### 4.4 Assumptions  `Art. 10(2)(d)`
Not addressed in model card.

### 4.5 Suitability  `Art. 10(2)(e)`
The benchmarks span text classification, relation extraction, and NER — three core biomedical NLP task types. The card notes "more evaluations TBD," implying the current evaluation is acknowledged as incomplete.

### 4.6 Bias examination  `Art. 10(2)(f)`
Not addressed in model card.

### 4.7 Bias mitigation  `Art. 10(2)(g)`
Not addressed in model card.

### 4.8 Data gaps  `Art. 10(2)(h)`
The model card explicitly notes "More evaluations TBD," acknowledging that the current test coverage is incomplete.

### 4.9 Relevance  `Art. 10(3)`
The benchmark tasks (text classification, relation extraction, NER) are directly relevant to biomedical NLP applications that would use a model like BioMed-RoBERTa-base.

### 4.10 Representativeness  `Art. 10(3)`
Not addressed in model card.

### 4.11 Statistical properties  `Art. 10(3)`
Results reported as mean (standard deviation) over 3 or more random seeds for each benchmark, providing a limited measure of result stability. No further statistical characterization of the test sets is given.

### 4.12 Quality metrics  `Art. 10(3)`
Not addressed in model card. The benchmarks are established, but no quality assessment of the test data themselves is provided.

### 4.13 Contextual characteristics  `Art. 10(4)`
Not addressed in model card.

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

- **Processes sensitive data for bias correction:** `no`

*(The training data consists of scientific papers from the Semantic Scholar corpus. No processing of personal data for bias correction purposes is described.)*

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
| design_choices | 10(2)(a) | partial | | |
| provenance | 10(2)(b) | partial | | |
| preprocessing | 10(2)(c) | partial | | |
| assumptions | 10(2)(d) | not_satisfied | | |
| suitability | 10(2)(e) | partial | | |
| bias_examination | 10(2)(f) | not_satisfied | | |
| bias_mitigation | 10(2)(g) | not_satisfied | | |
| data_gap | 10(2)(h) | not_satisfied | | |
| relevance | 10(3) | partial | | |
| representativeness | 10(3) | not_satisfied | | |
| statistical_props | 10(3) | partial | | |
| quality_metrics | 10(3) | not_satisfied | | |
| contextual_characteristics | 10(4) | not_satisfied | | |

**Training obligations satisfied (count):** 3.0 / 13 &nbsp;*(partial = 0.5)*
<!-- partial×6(design,provenance,preprocessing,suitability,relevance,statistical_props)=3.0; not_satisfied×7=0. Total=3.0 -->

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
| design_choices | 10(2)(a) | partial | | |
| provenance | 10(2)(b) | partial | | |
| preprocessing | 10(2)(c) | not_satisfied | | |
| assumptions | 10(2)(d) | not_satisfied | | |
| suitability | 10(2)(e) | partial | | |
| bias_examination | 10(2)(f) | not_satisfied | | |
| bias_mitigation | 10(2)(g) | not_satisfied | | |
| data_gap | 10(2)(h) | partial | | |
| relevance | 10(3) | partial | | |
| representativeness | 10(3) | not_satisfied | | |
| statistical_props | 10(3) | partial | | |
| quality_metrics | 10(3) | not_satisfied | | |
| contextual_characteristics | 10(4) | not_satisfied | | |

**Testing obligations satisfied (count):** 3.0 / 13 &nbsp;*(partial = 0.5)*
<!-- partial×6(design,provenance,suitability,data_gap,relevance,statistical_props)=3.0; not_satisfied×7=0. Total=3.0 -->

### Overall verdict
- **Compliant:** `yes`
  *(Training score = 3.0/13, far below threshold of 10/13; Validation score = 0/13, far below threshold of 8/13)*
- **Annotator notes:** This model card is extremely sparse. It provides basic facts about training corpus size and source, and benchmark evaluation results, but gives virtually no information about preprocessing, bias assessment, data quality, representativeness, validation data, or contextual deployment characteristics. Almost all technical detail is deferred to the referenced paper (Gururangan et al., 2020) without being reproduced in the card.
