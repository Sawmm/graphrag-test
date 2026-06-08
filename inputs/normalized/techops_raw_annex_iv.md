# Annex IV Normalization — Article 10 Data Governance
<!-- Pure restructure of the raw model card into the Annex IV skeleton.
     RULES: move source text VERBATIM into the matching field.
     If the raw card says nothing relevant, write "not provided".
     Do NOT write "not addressed", "unclear", or any other judgment.
     Do NOT invent or paraphrase. Compliance verdicts are NOT part of this file.
     NOTE: source is a standalone dataset card; the documented dataset is mapped to Section 2. -->

## Document metadata
- **HuggingFace ID:** techops_raw (Skin Tones Data Documentation)
- **Source card file:** `raw/techops_raw.md`
- **Normalized by:** Claude (verbatim restructure)
- **Date normalized:** 2026-06-07

---

## Section 1 — System Overview
*(Annex IV §1 — general description)*

- **System name and version:** Skin Tones Data Documentation; Document Version 0.5.0; Dataset Owner: George Costanza; Status: Under Preparation (Status Date 27/04/2023).
- **Intended purpose / task:** Post hoc skin tone labels of the faces of customers in the Zalando Voice of Customer (VOC) dataset curated as part of the "Skin Tone Labeling Initiative." The primary purpose of this data is for fairness evaluation purposes: to help ensure data used to train ML/AI systems for Size and Fit is representative of Zalando's customers; to ensure ML/AI systems do not systematically underperform for customers with certain skin tones. Intended Purpose: Fairness Evaluation.
- **High-risk category (Annex III ref.):** Known Usage AI Act Risk: Limited (Size and Fit - On Device Silhouette Extraction; Size and Fit - Body Measurements Pipeline).
- **Intended users / deployers:** Usage Guidelines: This dataset is meant for fairness evaluation purposes only to ensure that models trained on the Zalando VOC dataset, or similar, do not systematically underperform for subjects with certain skin tones. Suitable Use Case: Use to evaluate (un)fairness of any model that should perform well for Zalando VOC type images of humans. Unsuitable Use Case: This data is, in its current form, not vetted for training a skin tone classifier that could be used at scale. Approval Steps: The reason of using this dataset for a particular use case must be described and approved via a DPR process.
- **Geographic / regulatory scope:** Main point of contact: George Steinbrenner; Team: Size and Fit (Zurich); Affiliation: Zalando SE.

---

## Section 2 — Training Dataset
*(Annex IV §2 — development process; Article 10(2)–(4))*

### 2.1 Design choices  `Art. 10(2)(a)`
This data was collected by a team of four Zalando labelers from a mix of teams including Beauty, Size and Fit, and Algorithmic Privacy and Fairness. Labelers followed specific Skin Tone Labeling Instructions, and labeled each image for skin tone based on the 2022 Zalando Beauty skin tone scale. Motivating Factors: Assessing and publishing the distribution of skin tones in the Zalando VOC dataset; Identifying potential sample bias in data that may be used for training computer vision systems at Zalando; Providing a skin tone dataset for fairness evaluation. Data Point Collection Criteria — Data Selection: Filter out images with bad lighting and occlusions (done based on previously existing annotations done on Zalando VOC data); Choose images with >2.5% skin exposure: This threshold gave balance between being able to see skin, and leaving enough images to annotate (~1000) for a fairness evaluation, given the annotation budget.

### 2.2 Provenance  `Art. 10(2)(b)`
Collection Method(s) Used: Taken from other existing datasets; Crowdsourced - Internal Employee. Is this source considered sensitive or high-risk? Yes. Dates of Collection: 2022/12/15 - 2023/03/15. Update Frequency: Static. Source: Zalando VOC Skin Tones Dataset. Collection Cadence: Static — Data was collected once from a single source. Data Integration: Zalando-VOC images were used as input for labeling. These images are not generally included in skin tone dataset, but are identified by image-id to allow for fairness evaluation of systems that use such images.

### 2.3 Preprocessing  `Art. 10(2)(c)`
Transformation(s) Applied: Data Enrichment; Grouping. Method: Skin tone labels have been grouped by image and enriched by calculating other statistics. No loss of raw data has taken place. Platforms, tools, or libraries: Python. Annotation task: Each labeler labeled each image with one or more skin tone labels from the 2022 Zalando Beauty skin tone scale. Labelers were allowed to choose two adjacent labels when unsure, and labelers had a separate label for indicating they were not sure of the correct label. The overall labeling work was broken down into four sequential tasks. Annotation platforms: AWS SageMaker GroundTruth.

### 2.4 Assumptions  `Art. 10(2)(d)`
The skin tones in this dataset are annotations, not customer self-identifications. Skin tone annotation is subjective and the data here represent the best guesses from annotators that is affected a range of factors. Mistakes from labelers may have also occurred.

### 2.5 Suitability  `Art. 10(2)(e)`
Dataset Statistics: Size of Dataset 1009 MB; Number of Data Points 59 calibration + 999 main; Label Classes 6 (5 skin tones, 1 for uncertainty); Type of labels: Multiple labels per data point; Algorithmic Labels 0; Human Labels All. At this time, we do not recommend training models with this data, and therefore, do not have a recommended train-validation-test split.

### 2.6 Bias examination  `Art. 10(2)(f)`
Protected Attribute Type(s): Skin Tone. Research and Problem Space(s): Analysis of bias in human skin tone annotations. Possible Correlations to Protected Attributes: Labeler bias may cause correlations between skin tone labels and attributes of the image not related to skin tone, such as: judgements based on objects in the field of view (i.e. certain objects associated with certain cultures); facial shape and body shape; repeated customers — some customers appear multiple times in separate images and labelers may have consistently given each the same incorrect skin tone; labeler recency bias — seeing a lot of a certain skin color in a row can affect the next label made. Known Correlations to Protected Attributes: None identified at this time.

### 2.7 Bias mitigation  `Art. 10(2)(g)`
Some of the possible correlations have been mitigated by: having multiple labelers from different backgrounds label each image; shuffling the data each labeler labels - reducing the labeler recency bias effect; making two independent labeler calibration rounds to have the chance to debug the labeling process and have discussions about various unconscious labeler biases so each labeler can be mindful and potentially prevent introducing these unwanted correlations.

### 2.8 Data gaps  `Art. 10(2)(h)`
Under Preparation - The dataset is still under active curation and is not yet ready for use due to active "dev" updates. Unrepresenting skin tone groups: Sampling incorrectly risks certain skin tone groups being underrepresented for skin tone based fairness evaluations. Ensure all skin tones are well represented such as to have enough data points to estimate performance on particular skin tones with a low enough level of uncertainty to be able to draw reliable fairness conclusions.

### 2.9 Relevance  `Art. 10(3)`
Use and Utility: Zalando VOC images: Skin tone labels data are intended to be used to evaluate the fairness of ML/AI systems that take Zalando VOC images as an input. Benefit and Value: This data can be used to ensure ML/AI systems that consume Zalando VOC like images do not underperform for certain skin types. These skin tone data also inform others of existing skin tone biases in the Zalando VOC dataset.

### 2.10 Representativeness  `Art. 10(3)`
To help ensure data used to train ML/AI systems for Size and Fit is representative of Zalando's customers. Annotator Languages Spoken: English [100%], German [50%]. Annotator Locations of Upbringing: Canada [25%], Azerbaijan [25%], Germany [25%], Iran [25%]. Annotator Current Locations of Residence: Germany [75%], Switzerland [25%]. Annotator Genders: Male [50%], Female [50%].

### 2.11 Statistical properties  `Art. 10(3)`
skin_tone_mean: count 999; mean 0.670921; std 0.629619; min 0.; 25% 0.25; 50% 0.5; 75% 0.75; max 4.; mode 0.5. Annotation characteristics (based on calibration #2 split, 4 labelers labeling 59 examples): 4 of 4 agreement 12%; 3 of 4 agreement 25%; 2 of 4 agreement 51%; 1 unique label 14%; 2 unique labels 47%; 3 unique labels 32%; 4 unique labels 7%.

### 2.12 Quality metrics  `Art. 10(3)`
Number of annotated examples 1058; Total number of annotations 4322; Average annotations per example 4.1; Number of annotators per example 4. Validation Type(s): Range and Constraint Validation; Structured Validation; Consistency Validation. Number of Data Points Validated: all. All skin tone labels are checked for validity. Inter-rater adjudication policy: Budget permitting, the next version of the dataset will include results from a labeler review of images where more than two labelers disagreed. Golden questions: No golden questions.

### 2.13 Contextual characteristics  `Art. 10(4)`
Data Subject(s): Images of consenting customers; Sensitive Data about people; Skin tones labels. Sensitivity Type(s): User Metadata (skin tones); Identifiable Data (unblurred images); S/PII. Intentionally Collected Sensitive Data: Images used in labeling contain pictures of customers (without blurred faces). Unintentionally Collected Sensitive Data: Can see the setting in which customers take pictures of themselves. Data Security Classification: Yellow.

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

---

## Section 5 — Sensitive Personal Data  `Art. 10(5)`

- **Processes sensitive data for bias correction:** yes — Protected attributes (Skin Tone) were intentionally collected; Protected attributes were labeled or collected as a part of the dataset creation process. Rationale: To be used for fairness evaluation. The primary purpose of this data is for fairness evaluation purposes. Security and Privacy Handling: Access to this data is restricted to a small select group of people as governed by Data Processing Requests (DPRs).
