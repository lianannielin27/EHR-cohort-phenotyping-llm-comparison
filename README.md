# Evaluating Lisinopril Treatment in Patients with Chronic Kidney Disease Using Structured EHR Data and Clinical Notes

## Purpose of Study

The purpose of this retrospective cohort study is to evaluate the effectiveness of lisinopril among patients with chronic kidney disease (CKD) using both structured electronic health record (EHR) data and unstructured clinical notes.

Lisinopril is an angiotensin-converting enzyme (ACE) inhibitor commonly used to treat hypertension and kidney disease, particularly when CKD is accompanied by hypertension, albuminuria, or diabetic kidney disease. ACE inhibitors decrease angiotensin II activity, resulting in vasodilation and reduced intraglomerular pressure, which may reduce albuminuria and help preserve kidney function.

This study has two related objectives:

1. Evaluate changes in kidney function following lisinopril treatment using structured EHR data.
2. Compare structured EHR cohort identification with clinical-note concept extraction using SQL pattern matching and multiple large language models.

---

## Methods

This study uses UCSF De-Identified Research Data to construct a retrospective CKD cohort and evaluate lisinopril treatment using structured and unstructured EHR data.

### Cohort Definition

#### Eligible CKD Cohort

- **Cohort Entry:** Condition era of CKD.
- **Inclusion Criteria:** Age >18 years with at least one of the following indications: albuminuria, hypertension, or diabetic nephropathy.
- **Cohort Exit:** End of continuous observation or death.

#### Lisinopril-Treated Cohort

Patients from the eligible CKD cohort were classified as treated using structured EHR data if they had a qualifying lisinopril drug exposure on or after cohort entry.

#### Effectiveness Cohort

For the kidney-function effectiveness analysis, treated patients were additionally required to have qualifying baseline and follow-up serum or plasma creatinine measurements.

---

## Cohort Demographics

### Table 1. Demographics of Eligible and Lisinopril-Treated CKD Patients

| Characteristic | Eligible CKD Patients (N + %) | CKD Patients + Lisinopril (N + %) |
|---|---|---|
| **Age (years)** | | |
| Mean (SD) | 65.02 (15.29) | 62.31 (15.60) |
| Median (P25, P75) | 67.00 (56.00, 76.00) | 65.00 (53.00, 74.00) |
| Min, Max | 19.00, 90.00 | 19.00, 90.00 |
| **Sex** | | |
| Male | 29,799 (56.45%) | 4,681 (59.98%) |
| Female | 22,975 (43.52%) | 3,122 (40.01%) |
| **Race** | | |
| White | 26,108 (49.46%) | 3,657 (46.86%) |
| Asian | 9,684 (18.34%) | 1,512 (19.37%) |
| Other Race | 7,311 (13.85%) | 1,141 (14.62%) |
| Black or African American | 6,188 (11.72%) | 1,193 (15.29%) |
| Native Hawaiian or Other Pacific Islander | 1,700 (3.22%) | 135 (1.73%) |
| Unknown | 1,476 (2.80%) | 116 (1.49%) |
| **Ethnicity** | | |
| Not Hispanic or Latino | 43,864 (83.09%) | 6,598 (84.55%) |
| Hispanic or Latino | 6,818 (12.92%) | 1,038 (13.30%) |
| **Total** | **52,791** | **7,804** |

---

## Structured EHR Effectiveness Analysis

### Outcome Extraction

To evaluate kidney function following lisinopril treatment, serum or plasma creatinine measurements were compared before and after treatment.

Baseline values were selected from 365 days before through the index date, and follow-up values were selected from 90–365 days after index. One paired set of measurements was selected per patient.

Changes were evaluated using a Wilcoxon signed-rank test as the primary analysis, with a paired t-test and effect-size calculations as sensitivity analyses.

The structured EHR cohort construction and creatinine extraction are implemented in [`sql/cohort_treatment_analysis.sql`](sql/cohort_treatment_analysis.sql).

### Table 2. Creatinine Change Following Lisinopril Treatment

| Creatinine Change | Number of Patients | Percentage |
|---|---:|---:|
| Decreased creatinine | 1,976 | 55.2% |
| Increased creatinine | 1,481 | 41.3% |
| No change | 125 | 3.5% |
| **Total** | **3,582** | **100.0%** |

### Table 3. Statistical Analysis

| Statistical Measure | Result |
|---|---:|
| Original cohort size | 3,762 |
| Paired sample size | 3,582 |
| Patients with complete pairs | 95.2% |
| Baseline creatinine, mean ± SD | 1.882 ± 2.141 mg/dL |
| Baseline creatinine, median | 1.324 mg/dL |
| Follow-up creatinine, mean ± SD | 1.576 ± 1.469 mg/dL |
| Follow-up creatinine, median | 1.239 mg/dL |
| Mean paired change | −0.306 mg/dL |
| 95% CI for mean change | −0.369 to −0.243 mg/dL |
| Median paired change | −0.035 mg/dL |
| IQR of paired change | −0.246 to 0.123 mg/dL |
| Wilcoxon signed-rank statistic | 2,437,225.5 |
| Wilcoxon p-value | <0.001 |
| Rank-biserial effect size | −0.184 (small) |
| Paired t-test | *t*(3581) = −9.573 |
| Paired t-test p-value | <0.001 |
| Paired Cohen's *d*<sub>z</sub> | −0.160 (small) |

### Effectiveness Results

Among 3,762 patients in the effectiveness cohort, 3,582 (95.2%) had paired serum or plasma creatinine measurements during the baseline and follow-up periods. Mean creatinine decreased from 1.882 mg/dL (SD 2.141) at baseline to 1.576 mg/dL (SD 1.469) during follow-up. The mean paired change was −0.306 mg/dL (95% CI −0.369 to −0.243).

Because the paired differences were markedly skewed and contained extreme values, a Wilcoxon signed-rank test was used as the primary analysis. Creatinine was significantly lower during follow-up (median change −0.035 mg/dL, IQR −0.246 to 0.123; W = 2,437,225.5, p < 0.001). The rank-biserial effect size was small (r = −0.184). A paired t-test produced a consistent result, *t*(3581) = −9.573, p < 0.001, with a small paired effect size (dz = −0.160).

These findings suggest that lisinopril initiation was associated with a modest improvement or preservation of kidney function. Because this was an uncontrolled retrospective pre-post analysis, the results do not establish that lisinopril caused the observed change.

---

## Clinical Note Extraction and Cohort Validation

### Clinical Note Selection

Progress Notes were selected because they provide longitudinal clinical documentation of CKD management and lisinopril use, including treatment decisions, medication changes, patient response, adverse effects, and clinicians' assessments.

Compared with administrative or procedure-specific notes, Progress Notes are more likely to capture the ongoing clinical context relevant to evaluating lisinopril treatment.

Notes were restricted to 7 days before through 1 year after cohort entry. This window captures clinical context surrounding cohort entry as well as short- and longer-term follow-up while reducing inclusion of unrelated documentation from distant periods.

To keep inference feasible across SQL, BRIM, and multiple LLMs, 250 eligible patients were randomly sampled and up to two qualifying Progress Notes per patient were retained. Sampling patients before notes reduced overrepresentation of patients with extensive documentation.

Patients with only one qualifying note were retained to avoid introducing a requirement for frequent healthcare encounters, which could create selection bias.

The final analytic dataset contained **403 Progress Notes from 207 patients**, including 11 patients with only one qualifying Progress Note.

The clinical-note sampling procedure is implemented in [`sql/eligible_progressnotes_sample.sql`](sql/eligible_progressnotes_sample.sql).

### Clinical Concepts

Each Progress Note was evaluated for five concepts corresponding to the structured cohort definition and treatment:

- `CKD_MENTIONED`
- `ALBUMINURIA_MENTIONED`
- `HYPERTENSION_MENTIONED`
- `DIABETIC_NEPHROPATHY_MENTIONED`
- `LISINOPRIL_MENTIONED`

Four extraction approaches were compared:

1. SQL pattern matching
2. BRIM
3. GPT-OSS-20B
4. Qwen3-8B-AWQ

---

### SQL Pattern Matching

Rule-based clinical concept extraction is implemented in [`sql/pattern_matching.sql`](sql/pattern_matching.sql).

The SQL query uses `CASE WHEN` statements with case-insensitive text matching to assign TRUE/FALSE values to the five concepts for every note.

The workflow can be reproduced as follows:

1. Run [`sql/eligible_progressnotes_sample.sql`](sql/eligible_progressnotes_sample.sql) to extract the analytic Progress Note sample.
2. Run [`sql/pattern_matching.sql`](sql/pattern_matching.sql).
3. Apply the predefined terms for the five variables.
4. Export the resulting note-level classifications from Athena as CSV/JSON for downstream analysis.

The same SQL script also calculates note-level and patient-level concept counts.

---

### BRIM Extraction

The BRIM variable definitions used for clinical concept extraction are provided in [`brim/BrimVariableExport_lisinopril_eligible.csv`](brim/BrimVariableExport_lisinopril_eligible.csv).

Clinical notes are standardized to the following BRIM schema:

- `NOTE_ID`
- `PERSON_ID`
- `NOTE_DATETIME`
- `NOTE_TEXT`
- `NOTE_TITLE`

To reproduce the analysis:

1. Create a BRIM project.
2. Upload the standardized clinical-note input.
3. Configure the five variables using [`brim/BrimVariableExport_lisinopril_eligible.csv`](brim/BrimVariableExport_lisinopril_eligible.csv).
4. Run BRIM inference across the uploaded notes.
5. Export the resulting document-level classifications.
6. If BRIM exports results in long format, transform them into wide format with one row per `NOTE_ID` and one column for each TRUE/FALSE variable.

Results can then be aligned with the other extraction approaches using `NOTE_ID`.

---

### Qwen3-8B-AWQ Extraction

Qwen inference is implemented in [`inference/qwen_inference.py`](inference/qwen_inference.py).

The script runs `Qwen/Qwen3-8B-AWQ` through vLLM in the UCSF IC AWS Secure GPU environment.

The script:

- validates the clinical-note input;
- applies the five concept definitions;
- requests structured boolean outputs;
- validates model responses;
- saves results incrementally;
- supports resuming incomplete inference; and
- produces CSV and JSON outputs without including clinical note text.

The resulting output contains:

- `NOTE_ID`
- `PERSON_ID`
- `NOTE_DATETIME`
- `NOTE_TITLE`
- `CKD_MENTIONED`
- `ALBUMINURIA_MENTIONED`
- `HYPERTENSION_MENTIONED`
- `DIABETIC_NEPHROPATHY_MENTIONED`
- `LISINOPRIL_MENTIONED`

The Qwen workflow produces:

- `qwen_eligible_cohort_results.csv`
- `qwen_eligible_cohort_results.json`

---

### GPT-OSS-20B Extraction

GPT-OSS inference is implemented in [`inference/gpt_oss_inference.py`](inference/gpt_oss_inference.py).

The script uses `openai/gpt-oss-20b` through the UCSF IC FAC AI Deployment Server.

The script:

- uses structured JSON outputs;
- applies the same five clinical concept definitions;
- validates model responses;
- saves results incrementally;
- supports resuming interrupted inference; and
- produces both CSV and JSON result files.

The resulting output can be aligned with SQL, BRIM, and Qwen using `NOTE_ID`.

---

## Comparison of Clinical Note Extraction Methods

### Patient-Level Concept Mentions

A patient was considered positive for a concept if at least one of their sampled Progress Notes was classified as TRUE for that concept. Counts therefore represent unique patients rather than individual notes.

| Extraction Method | CKD | Albuminuria | Hypertension | Diabetic Nephropathy | Lisinopril |
|---|---:|---:|---:|---:|---:|
| SQL Pattern Matching | 76 | 24 | 87 | 3 | 20 |
| BRIM | 101 | 30 | 101 | 12 | 21 |
| GPT-OSS-20B | 107 | 25 | 105 | 2 | 20 |
| Qwen3-8B-AWQ | 88 | 20 | 118 | 9 | 22 |

### Note-Level Concept Mentions

| Extraction Method | Total Notes | CKD TRUE | Albuminuria TRUE | Hypertension TRUE | Diabetic Nephropathy TRUE | Lisinopril TRUE |
|---|---:|---:|---:|---:|---:|---:|
| SQL Pattern Matching | 403 | 98 | 29 | 116 | 3 | 24 |
| BRIM | 402 | 138 | 37 | 133 | 15 | 25 |
| GPT-OSS-20B | 402 | 146 | 30 | 136 | 2 | 24 |
| Qwen3-8B-AWQ | 403 | 115 | 21 | 171 | 10 | 27 |

---

## Demographics of Note-Derived Lisinopril-Positive Patients

Patients were classified as note-derived lisinopril-positive if lisinopril was identified in at least one sampled Progress Note.

Patients without a detected lisinopril mention were classified as having no lisinopril mention for this analysis.

Because only up to two Progress Notes per patient were sampled, absence of a lisinopril mention does **not** necessarily indicate absence of true lisinopril exposure.

### SQL Pattern Matching

| Characteristic | Lisinopril-Positive (N=20) | No Lisinopril Mention (N=187) |
|---|---:|---:|
| **Age, mean (SD)** | 59.0 (14.0) | 64.0 (14.4) |
| **Sex, n (%)** | | |
| Female | 7 (35.0%) | 79 (42.2%) |
| Male | 13 (65.0%) | 108 (57.8%) |
| **Race, n (%)** | | |
| White | 8 (40.0%) | 89 (47.6%) |
| Asian | 5 (25.0%) | 31 (16.6%) |
| Black or African American | 3 (15.0%) | 18 (9.6%) |
| Other Race | 2 (10.0%) | 38 (20.3%) |
| Native Hawaiian or Other Pacific Islander | 1 (5.0%) | 7 (3.7%) |
| American Indian or Alaska Native | 0 (0.0%) | 1 (0.5%) |
| Unknown | 1 (5.0%) | 3 (1.6%) |
| **Ethnicity, n (%)** | | |
| Hispanic or Latino | 4 (20.0%) | 31 (16.6%) |
| Not Hispanic or Latino | 15 (75.0%) | 149 (79.7%) |
| Unknown | 1 (5.0%) | 7 (3.7%) |

### BRIM

| Characteristic | Lisinopril-Positive (N=21) | No Lisinopril Mention (N=186) |
|---|---:|---:|
| **Age, mean (SD)** | 59.1 (13.6) | 64.0 (14.4) |
| **Sex, n (%)** | | |
| Female | 7 (33.3%) | 79 (42.5%) |
| Male | 14 (66.7%) | 107 (57.5%) |
| **Race, n (%)** | | |
| White | 8 (38.1%) | 89 (47.8%) |
| Asian | 5 (23.8%) | 31 (16.7%) |
| Black or African American | 3 (14.3%) | 18 (9.7%) |
| Other Race | 3 (14.3%) | 37 (19.9%) |
| Native Hawaiian or Other Pacific Islander | 1 (4.8%) | 7 (3.8%) |
| American Indian or Alaska Native | 0 (0.0%) | 1 (0.5%) |
| Unknown | 1 (4.8%) | 3 (1.6%) |
| **Ethnicity, n (%)** | | |
| Hispanic or Latino | 4 (19.0%) | 31 (16.7%) |
| Not Hispanic or Latino | 15 (71.4%) | 149 (80.1%) |
| Unknown | 2 (9.5%) | 6 (3.2%) |

### GPT-OSS-20B

| Characteristic | Lisinopril-Positive (N=20) | No Lisinopril Mention (N=187) |
|---|---:|---:|
| **Age, mean (SD)** | 59.0 (14.0) | 64.0 (14.4) |
| **Sex, n (%)** | | |
| Female | 7 (35.0%) | 79 (42.2%) |
| Male | 13 (65.0%) | 108 (57.8%) |
| **Race, n (%)** | | |
| White | 8 (40.0%) | 89 (47.6%) |
| Asian | 5 (25.0%) | 31 (16.6%) |
| Black or African American | 3 (15.0%) | 18 (9.6%) |
| Other Race | 2 (10.0%) | 38 (20.3%) |
| Native Hawaiian or Other Pacific Islander | 1 (5.0%) | 7 (3.7%) |
| American Indian or Alaska Native | 0 (0.0%) | 1 (0.5%) |
| Unknown | 1 (5.0%) | 3 (1.6%) |
| **Ethnicity, n (%)** | | |
| Hispanic or Latino | 4 (20.0%) | 31 (16.6%) |
| Not Hispanic or Latino | 15 (75.0%) | 149 (79.7%) |
| Unknown | 1 (5.0%) | 7 (3.7%) |

### Qwen3-8B-AWQ

| Characteristic | Lisinopril-Positive (N=22) | No Lisinopril Mention (N=185) |
|---|---:|---:|
| **Age, mean (SD)** | 60.4 (13.8) | 63.9 (14.5) |
| **Sex, n (%)** | | |
| Female | 9 (40.9%) | 77 (41.6%) |
| Male | 13 (59.1%) | 108 (58.4%) |
| **Race, n (%)** | | |
| White | 10 (45.5%) | 87 (47.0%) |
| Asian | 5 (22.7%) | 31 (16.8%) |
| Black or African American | 3 (13.6%) | 18 (9.7%) |
| Other Race | 3 (13.6%) | 37 (20.0%) |
| Native Hawaiian or Other Pacific Islander | 0 (0.0%) | 8 (4.3%) |
| American Indian or Alaska Native | 0 (0.0%) | 1 (0.5%) |
| Unknown | 1 (4.5%) | 3 (1.6%) |
| **Ethnicity, n (%)** | | |
| Hispanic or Latino | 6 (27.3%) | 29 (15.7%) |
| Not Hispanic or Latino | 15 (68.2%) | 149 (80.5%) |
| Unknown | 1 (4.5%) | 7 (3.8%) |

---

## Structured EHR vs. Clinical Note Identification

Overall, the unstructured clinical-note results were directionally consistent with the structured EHR findings but identified a smaller proportion of patients with lisinopril documentation.

Structured drug-exposure data classified **7,804 of 52,791 eligible CKD patients (14.8%)** as lisinopril-treated.

In the clinical-note sample, lisinopril was identified in approximately **9.7–10.6%** of patients, with highly consistent results across SQL, BRIM, GPT-OSS, and Qwen.

The demographics were also broadly similar. Structured-EHR lisinopril-treated patients had a mean age of 62.31 years and were 59.98% male. Across the four note-extraction approaches, lisinopril-positive patients had mean ages of approximately 59–60 years and were approximately 59–67% male.

### Structured Versus Note-Derived Lisinopril Evidence

| Source | Positive Patients | Evaluated | Positive % |
|---|---:|---:|---:|
| Structured EHR | 7,804 | 52,791 | 14.8% |
| SQL Pattern Matching | 20 | 207 | 9.7% |
| BRIM | 21 | 207 | 10.1% |
| GPT-OSS-20B | 20 | 207 | 9.7% |
| Qwen3-8B-AWQ | 22 | 207 | 10.6% |

**Note:** The structured EHR and note-derived percentages use different denominators. The structured estimate represents lisinopril drug exposure among the full eligible CKD cohort (N=52,791), whereas the note-derived estimates represent lisinopril mentions among the 207 patients in the sampled Progress Note cohort. Therefore, these percentages provide a descriptive comparison and should not be interpreted as a direct measure of sensitivity or agreement.

Lisinopril detection was highly consistent across the four note-extraction methods: SQL pattern matching identified 20 patients, BRIM identified 21, GPT-OSS-20B identified 20, and Qwen3-8B-AWQ identified 22.

Structured EHR data is more appropriate for identifying actual treatment exposure because lisinopril may not be mentioned in the limited Progress Notes sampled for a patient. Conversely, clinical notes provide useful complementary information about the clinical context of treatment, but a medication mention alone does not necessarily indicate active use.

---

## Reproducibility

The analysis code is organized into structured EHR cohort construction, clinical-note sampling, and clinical concept extraction.

### Structured EHR Cohort and Effectiveness Analysis

The structured EHR analysis is implemented in [`sql/cohort_treatment_analysis.sql`](sql/cohort_treatment_analysis.sql).

This script:

- constructs the CKD/lisinopril cohort using OMOP condition, drug-exposure, observation-period, and measurement data;
- applies the cohort eligibility criteria;
- identifies qualifying lisinopril exposure;
- extracts baseline and follow-up creatinine measurements; and
- creates paired creatinine measurements for the treatment-effectiveness analysis.

Baseline creatinine measurements are selected from 365 days before through the index date, and follow-up measurements are selected from 90 through 365 days after the index date.

### Clinical Note Sampling

The clinical-note analytic sample is created using [`sql/eligible_progressnotes_sample.sql`](sql/eligible_progressnotes_sample.sql).

The script starts with the eligible CKD cohort, randomly samples up to 250 patients, and extracts Progress Notes documented from 7 days before through 1 year after cohort entry. Up to two qualifying Progress Notes are retained per patient.

The final analytic sample contained 403 Progress Notes from 207 patients.

### SQL Pattern Matching

Rule-based clinical concept extraction is implemented in [`sql/pattern_matching.sql`](sql/pattern_matching.sql).

The script assigns TRUE/FALSE labels for:

- `CKD_MENTIONED`
- `ALBUMINURIA_MENTIONED`
- `HYPERTENSION_MENTIONED`
- `DIABETIC_NEPHROPATHY_MENTIONED`
- `LISINOPRIL_MENTIONED`

The same script also calculates note-level and patient-level concept counts.

### BRIM

The BRIM variable definitions used for clinical concept extraction are provided in [`brim/BrimVariableExport_lisinopril_eligible.csv`](brim/BrimVariableExport_lisinopril_eligible.csv).

Clinical notes are standardized to the BRIM schema:

- `NOTE_ID`
- `PERSON_ID`
- `NOTE_DATETIME`
- `NOTE_TEXT`
- `NOTE_TITLE`

BRIM results can be exported and aligned with the other extraction approaches using `NOTE_ID`.

### Qwen3-8B-AWQ

Qwen inference is implemented in [`inference/qwen_inference.py`](inference/qwen_inference.py).

The script runs `Qwen/Qwen3-8B-AWQ` through vLLM in the UCSF IC AWS Secure GPU environment. It:

- validates the clinical-note input;
- applies the five concept definitions;
- requests structured boolean outputs;
- validates model responses;
- saves results incrementally;
- supports resuming incomplete inference; and
- produces CSV and JSON outputs without including clinical note text.

### GPT-OSS-20B

GPT-OSS inference is implemented in [`inference/gpt_oss_inference.py`](inference/gpt_oss_inference.py).

The script uses `openai/gpt-oss-20b` through the UCSF IC FAC AI Deployment Server. It:

- uses structured JSON outputs;
- applies the same five clinical concept definitions;
- validates model responses;
- saves results incrementally;
- supports resuming interrupted inference; and
- produces both CSV and JSON result files.

### Analysis Workflow

The overall reproducible workflow is:

1. Construct the eligible CKD and lisinopril-treated cohorts using [`sql/cohort_treatment_analysis.sql`](sql/cohort_treatment_analysis.sql).
2. Perform the structured EHR creatinine effectiveness analysis.
3. Sample eligible-patient Progress Notes using [`sql/eligible_progressnotes_sample.sql`](sql/eligible_progressnotes_sample.sql).
4. Apply SQL pattern matching using [`sql/pattern_matching.sql`](sql/pattern_matching.sql).
5. Apply the same concept definitions in BRIM.
6. Run Qwen3-8B-AWQ using [`inference/qwen_inference.py`](inference/qwen_inference.py).
7. Run GPT-OSS-20B using [`inference/gpt_oss_inference.py`](inference/gpt_oss_inference.py).
8. Aggregate note-level classifications to patient-level classifications.
9. Compare structured EHR lisinopril exposure with note-derived lisinopril documentation.

---

## Conclusions

This study combined structured EHR cohort construction, treatment-effectiveness analysis, and unstructured clinical-note extraction to evaluate lisinopril use among patients with CKD.

Structured EHR data identified **52,791 eligible CKD patients**, of whom **7,804 (14.8%)** had documented lisinopril exposure. Among patients with sufficient laboratory follow-up, creatinine decreased modestly after treatment, although the small effect size and uncontrolled retrospective design prevent causal interpretation.

Clinical-note extraction produced broadly consistent lisinopril detection across SQL pattern matching, BRIM, GPT-OSS-20B, and Qwen3-8B-AWQ. However, note-derived lisinopril mentions were less frequent than structured drug exposures, likely because medications are not necessarily documented in every Progress Note and only up to two notes per patient were analyzed.

Overall, structured EHR data provides a more direct and complete approach for defining treatment exposure, while unstructured clinical notes provide complementary clinical context and can help validate or characterize structured cohorts.
