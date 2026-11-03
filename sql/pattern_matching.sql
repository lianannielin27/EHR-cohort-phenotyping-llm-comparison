-- creating table of pattern matching labels

CREATE TABLE llin11.ckd_eligible_sql_pattern_matching AS

SELECT 
    person_id,
    cohort_start_date,
    cohort_end_date,
    deid_note_key,
    note_text,

    -- CKD
    CASE 
        WHEN LOWER(note_text) LIKE '%ckd%'
          OR LOWER(note_text) LIKE '%chronic kidney disease%'
          OR LOWER(note_text) LIKE '%chronic kidney failure%'
          OR LOWER(note_text) LIKE '%chronic renal insufficiency%'
        THEN TRUE 
        ELSE FALSE 
    END AS ckd_mentioned,

    -- Albuminuria
    CASE 
        WHEN LOWER(note_text) LIKE '%albuminuria%'
          OR LOWER(note_text) LIKE '%albuminuric%'
          OR LOWER(note_text) LIKE '%microalbuminuria%'
          OR LOWER(note_text) LIKE '%macroalbuminuria%'
          OR LOWER(note_text) LIKE '%proteinuria%'
        THEN TRUE 
        ELSE FALSE 
    END AS albuminuria_mentioned,

    -- Hypertension
    CASE 
        WHEN LOWER(note_text) LIKE '%hypertension%'
          OR LOWER(note_text) LIKE '%hypertensive%'
        THEN TRUE 
        ELSE FALSE 
    END AS hypertension_mentioned,

    -- Diabetic nephropathy
    CASE 
        WHEN LOWER(note_text) LIKE '%diabetic nephropathy%'
          OR LOWER(note_text) LIKE '%diabetic kidney disease%'
          OR LOWER(note_text) LIKE '%diabetic nephrosis%'
        THEN TRUE 
        ELSE FALSE 
    END AS diabetic_nephropathy_mentioned,

    -- Lisinopril
    CASE 
        WHEN LOWER(note_text) LIKE '%lisinopril%'
          OR LOWER(note_text) LIKE '%zestril%'
          OR LOWER(note_text) LIKE '%prinivil%'
          OR LOWER(note_text) LIKE '%qbrelis%'
          OR LOWER(note_text) LIKE '%zestoretic%'
          OR LOWER(note_text) LIKE '%prinzide%'
        THEN TRUE 
        ELSE FALSE 
    END AS lisinopril_mentioned

FROM llin11.ckd_eligible_progressnotes;

-- seeing note-level counts of each concept set label (run separately)
SELECT
    COUNT(*) AS total_notes,

    COUNT_IF(ckd_mentioned = TRUE) AS ckd_true,
    COUNT_IF(ckd_mentioned = FALSE) AS ckd_false,

    COUNT_IF(albuminuria_mentioned = TRUE) AS albuminuria_true,
    COUNT_IF(albuminuria_mentioned = FALSE) AS albuminuria_false,

    COUNT_IF(hypertension_mentioned = TRUE) AS hypertension_true,
    COUNT_IF(hypertension_mentioned = FALSE) AS hypertension_false,

    COUNT_IF(diabetic_nephropathy_mentioned = TRUE) AS diabetic_nephropathy_true,
    COUNT_IF(diabetic_nephropathy_mentioned = FALSE) AS diabetic_nephropathy_false,

    COUNT_IF(lisinopril_mentioned = TRUE) AS lisinopril_true,
    COUNT_IF(lisinopril_mentioned = FALSE) AS lisinopril_false

FROM llin11.ckd_eligible_sql_pattern_matching;

-- seeing patient-level counts of each concept set label (run separately)
SELECT
    COUNT(DISTINCT person_id) AS total_patients,

    COUNT(DISTINCT CASE
        WHEN ckd_mentioned = TRUE THEN person_id
    END) AS patients_ckd_true,

    COUNT(DISTINCT CASE
        WHEN albuminuria_mentioned = TRUE THEN person_id
    END) AS patients_albuminuria_true,

    COUNT(DISTINCT CASE
        WHEN hypertension_mentioned = TRUE THEN person_id
    END) AS patients_hypertension_true,

    COUNT(DISTINCT CASE
        WHEN diabetic_nephropathy_mentioned = TRUE THEN person_id
    END) AS patients_diabetic_nephropathy_true,

    COUNT(DISTINCT CASE
        WHEN lisinopril_mentioned = TRUE THEN person_id
    END) AS patients_lisinopril_true

FROM llin11.ckd_eligible_sql_pattern_matching;
