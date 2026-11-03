-- create table with up to 250 eligible patients, up to 2 progress notes per patient, documented between -7 days before the index date and +1 year after the index date
DROP TABLE IF EXISTS llin11.ckd_eligible_progressnotes ;

CREATE TABLE llin11.ckd_eligible_progressnotes AS

WITH random_250_patients AS (
    SELECT patient_id
    FROM (
        SELECT DISTINCT patient_id
        FROM llin11.lisinopril_eligible_cohort
    )
    ORDER BY rand()
    LIMIT 250
),

eligible_progress_notes AS (
    SELECT DISTINCT
        c.patient_id,
        c.cohort_start_date,
        c.cohort_end_date,
        p.person_source_value,
        nm.patientepicid,
        nm.deid_note_key,
        nt.note_text,
        nm.deid_service_date

    FROM llin11.lisinopril_eligible_cohort c

    INNER JOIN random_250_patients rp
        ON c.patient_id = rp.patient_id

    INNER JOIN deid_omop.person p
        ON p.person_id = c.patient_id

    INNER JOIN deid_cdw_ucsf.note_metadata nm
        ON TRIM(CAST(p.person_source_value AS VARCHAR))
           = TRIM(CAST(nm.patientepicid AS VARCHAR))

    INNER JOIN deid_cdw_ucsf.note_text nt
        ON nm.deid_note_key = nt.deid_note_key

    WHERE nm.note_type = 'Progress Notes'

      AND CAST(nm.deid_service_date AS DATE)
          BETWEEN DATE_ADD(
                      'day',
                      -7,
                      CAST(c.cohort_start_date AS DATE)
                  )
              AND DATE_ADD(
                      'year',
                      1,
                      CAST(c.cohort_start_date AS DATE)
                  )
),

ranked_notes AS (
    SELECT
        patient_id,
        cohort_start_date,
        cohort_end_date,
        person_source_value,
        patientepicid,
        deid_note_key,
        note_text,
        deid_service_date,

        ROW_NUMBER() OVER (
            PARTITION BY patient_id
            ORDER BY rand()
        ) AS note_rank

    FROM eligible_progress_notes
)

SELECT
    patient_id AS person_id,
    cohort_start_date,
    cohort_end_date,
    person_source_value,
    patientepicid,
    deid_note_key,
    note_text,
    deid_service_date

FROM ranked_notes

WHERE note_rank <= 2;

-- finding patient count and progress note count(run separately)
SELECT
    COUNT(*) AS number_of_notes,
    COUNT(DISTINCT person_id) AS number_of_patients,
    COUNT(DISTINCT deid_note_key) AS unique_notes
FROM llin11.ckd_eligible_progressnotes;

-- patients with less than two eligible progress notes
SELECT
    person_id,
    COUNT(*) AS number_of_notes
FROM llin11.ckd_eligible_progressnotes
GROUP BY person_id
HAVING COUNT(*) < 2;
