# Annex IV Normalization — Article 10 Data Governance
<!-- Pure restructure of the raw model card into the Annex IV skeleton.
     RULES: move source text VERBATIM into the matching field.
     If the raw card says nothing relevant, write "not provided".
     Do NOT write "not addressed", "unclear", or any other judgment.
     Do NOT invent or paraphrase. Compliance verdicts are NOT part of this file.
     Bibtex abstract included because it is the model's own paper. -->

## Document metadata
- **HuggingFace ID:** sultan/BioM-ELECTRA-Large-SQuAD2
- **Source card file:** `raw/sultan__BioM-ELECTRA-Large-SQuAD2.md`
- **Normalized by:** Claude (verbatim restructure)
- **Date normalized:** 2026-06-07

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** BioM-ELECTRA-Large-SQuAD2
- **Intended purpose / task:** We fine-tuned BioM-ELECTRA-Large, which was pre-trained on PubMed Abstracts, on the SQuAD2.0 dataset. Fine-tuning the biomedical language model on the SQuAD dataset helps improve the score on the BioASQ challenge. If you plan to work with BioASQ or biomedical QA tasks, it's better to use this model over BioM-ELECTRA-Large.
- **High-risk category (Annex III ref.):** not provided
- **Intended users / deployers:** not provided
- **Geographic / regulatory scope:** not provided

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
We empirically study biomedical domain adaptation with large transformer models using different design choices. Our findings highlight the significant effect of design choices on improving the performance of biomedical language models. We fine-tuned BioM-ELECTRA-Large, which was pre-trained on PubMed Abstracts, on the SQuAD2.0 dataset.

### 2.2 Provenance  `Art. 10(2)(b)`
Pre-trained on PubMed Abstracts; fine-tuned on the SQuAD2.0 dataset.

### 2.3 Preprocessing  `Art. 10(2)(c)`
not provided

### 2.4 Assumptions  `Art. 10(2)(d)`
not provided

### 2.5 Suitability  `Art. 10(2)(e)`
not provided

### 2.6 Bias examination  `Art. 10(2)(f)`
not provided

### 2.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 2.8 Data gaps  `Art. 10(2)(h)`
not provided

### 2.9 Relevance  `Art. 10(3)`
not provided

### 2.10 Representativeness  `Art. 10(3)`
not provided

### 2.11 Statistical properties  `Art. 10(3)`
not provided

### 2.12 Quality metrics  `Art. 10(3)`
not provided

### 2.13 Contextual characteristics  `Art. 10(4)`
not provided

---

## Section 3 — Validation Dataset
*(same 13 fields as Section 2)*

### 3.1 Design choices  `Art. 10(2)(a)`
not provided

### 3.2 Provenance  `Art. 10(2)(b)`
not provided

### 3.3 Preprocessing  `Art. 10(2)(c)`
not provided

### 3.4 Assumptions  `Art. 10(2)(d)`
not provided

### 3.5 Suitability  `Art. 10(2)(e)`
not provided

### 3.6 Bias examination  `Art. 10(2)(f)`
not provided

### 3.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 3.8 Data gaps  `Art. 10(2)(h)`
not provided

### 3.9 Relevance  `Art. 10(3)`
not provided

### 3.10 Representativeness  `Art. 10(3)`
not provided

### 3.11 Statistical properties  `Art. 10(3)`
not provided

### 3.12 Quality metrics  `Art. 10(3)`
not provided

### 3.13 Contextual characteristics  `Art. 10(4)`
not provided

---

## Section 4 — Testing Dataset
*(same 13 fields; if no independent test set exists, write "not provided")*

### 4.1 Design choices  `Art. 10(2)(a)`
Evaluation results on SQuAD2.0 Dev Dataset. This model (TensorFlow version) took the lead in the BioASQ9b-Factoid challenge (Batch 5) under the name of (UDEL-LAB2).

### 4.2 Provenance  `Art. 10(2)(b)`
SQuAD2.0 Dev Dataset; BioASQ9b-Factoid challenge (Batch 5).

### 4.3 Preprocessing  `Art. 10(2)(c)`
not provided

### 4.4 Assumptions  `Art. 10(2)(d)`
not provided

### 4.5 Suitability  `Art. 10(2)(e)`
not provided

### 4.6 Bias examination  `Art. 10(2)(f)`
not provided

### 4.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 4.8 Data gaps  `Art. 10(2)(h)`
Huggingface library doesn't implement Layer-Wise decay feature, which affects the performance on SQuAD task. The reported result of BioM-ELECTRA-SQuAD in our paper is 88.3 (F1) since we use ELECTRA open-source code with TF checkpoint, which uses Layer-Wise decay.

### 4.9 Relevance  `Art. 10(3)`
not provided

### 4.10 Representativeness  `Art. 10(3)`
not provided

### 4.11 Statistical properties  `Art. 10(3)`
total = 11873; HasAns_total = 5928; NoAns_total = 5945.

### 4.12 Quality metrics  `Art. 10(3)`
exact = 84.33420365535248; f1 = 87.49354241889522; HasAns_exact = 80.43184885290148; HasAns_f1 = 86.75958656200127; NoAns_exact = 88.22539949537426; NoAns_f1 = 88.22539949537426; best_exact = 84.33420365535248; best_f1 = 87.49354241889522. We achieve 88.22 score in SQuAD2.0 since Tensor Flow code has Layer-wise decay feature.

### 4.13 Contextual characteristics  `Art. 10(4)`
not provided

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

- **Processes sensitive data for bias correction:** not provided
