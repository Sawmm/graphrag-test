# Annex IV Normalization — Article 10 Data Governance
<!-- Synthetic model card for diversity testing — sparse compliance profile. -->

## Document metadata
- **System ID:** faceid-law-v2
- **Organisation:** SecureVision Systems GmbH, Munich, Germany
- **System type:** High-risk AI system (EU AI Act Annex III, §1(a) — biometric identification)
- **Intended purpose:** Real-time facial recognition for suspect identification in law enforcement video surveillance feeds.
- **Version:** 2.0.3
- **Date:** November 2025
- **Normalized by:** Synthetic (compliance testing)
- **Date normalized:** 2026-06-15

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** FaceID-Law v2, version 2.0.3
- **Intended purpose / task:** Deep learning facial recognition system for real-time identification of persons of interest in law enforcement CCTV footage. Produces a match confidence score and ranked list of candidate identities from a reference database of known suspects.
- **High-risk category (Annex III ref.):** Annex III §1(a) — AI systems intended to be used by competent authorities for the real-time and post-remote biometric identification of natural persons.
- **Intended users / deployers:** German federal and state police agencies. Deployed under coordination of Bundeskriminalamt (BKA).
- **Geographic / regulatory scope:** Germany. Training data sourced from partner law enforcement agencies and commercial data providers.

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
The training dataset was assembled from facial image collections provided by partner law enforcement agencies and licensed from commercial image providers.

### 2.2 Provenance  `Art. 10(2)(b)`
Training data was sourced from three components: (1) BKA criminal justice image database (access granted under §81b StPO legal basis, 2.4 million images), (2) licensed subset of VGGFace2 dataset (University of Oxford, academic licence), and (3) CASIA-WebFace public dataset. Data was assembled under a formal data use agreement with BKA (DUA-BKA-2024-017). All commercial licences documented in internal records DUA-2024-017, Annex C.

### 2.3 Preprocessing  `Art. 10(2)(c)`
Facial images were normalised to 112×112 pixels using MTCNN face detection and alignment. Pixel values normalised to [0, 1]. Data augmentation applied: random horizontal flip, brightness jitter (±15%), and Gaussian blur (σ ∈ [0.5, 1.5]). Augmentation parameters documented in internal technical note TN-2024-009.

### 2.4 Assumptions  `Art. 10(2)(d)`
not provided

### 2.5 Suitability  `Art. 10(2)(e)`
The training dataset contains approximately 3.1 million facial images from 89,000 unique identities. This was considered sufficient for training a production-grade face recognition model based on internal benchmarking.

### 2.6 Bias examination  `Art. 10(2)(f)`
not provided

### 2.7 Bias mitigation  `Art. 10(2)(g)`
not provided

### 2.8 Data gaps  `Art. 10(2)(h)`
not provided

### 2.9 Relevance  `Art. 10(3)`
The training data includes images from law enforcement databases relevant to the suspect identification task.

### 2.10 Representativeness  `Art. 10(3)`
not provided

### 2.11 Statistical properties  `Art. 10(3)`
not provided

### 2.12 Quality metrics  `Art. 10(3)`
Images with face detection confidence below 0.9 were excluded from training.

### 2.13 Contextual characteristics  `Art. 10(4)`
Training data originates from European law enforcement and academic facial recognition datasets, reflecting the operational context of German police surveillance environments.

---

## Section 3 — Validation Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 3.1 Design choices  `Art. 10(2)(a)`
A held-out validation split was reserved from the BKA database component prior to training.

### 3.2 Provenance  `Art. 10(2)(b)`
Subset of BKA criminal justice image database, same legal basis as training data.

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
Validation data drawn from the same law enforcement image database as training.

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
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 4.1 Design choices  `Art. 10(2)(a)`
not provided

### 4.2 Provenance  `Art. 10(2)(b)`
not provided

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
not provided

### 4.9 Relevance  `Art. 10(3)`
not provided

### 4.10 Representativeness  `Art. 10(3)`
not provided

### 4.11 Statistical properties  `Art. 10(3)`
not provided

### 4.12 Quality metrics  `Art. 10(3)`
not provided

### 4.13 Contextual characteristics  `Art. 10(4)`
not provided
