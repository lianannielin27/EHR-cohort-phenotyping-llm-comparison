import csv
import json
import os
from pathlib import Path

from openai import OpenAI


# ============================================================
# IC FAC AI DEPLOYMENT SERVER CONFIGURATION
# ============================================================

# The IC FAC internal AI Deployment Server should bypass the
# FAC proxy when this is run as a Python script.
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("__CONDA_SHLVL_1_HTTP_PROXY", None)
os.environ.pop("__CONDA_SHLVL_1_HTTPS_PROXY", None)

BASE_URL = "http://gpu-dev2.ic.fac.ucsf.edu:8000/v1/"
MODEL = "openai/gpt-oss-20b"

client = OpenAI(
    base_url=BASE_URL,
    api_key="None"
)


# ============================================================
# FILE CONFIGURATION
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    SCRIPT_DIR / "eligible_progressnotes_BRIM_ready.csv"
)

RESULTS_DIR = SCRIPT_DIR / "results"
RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_JSON = (
    RESULTS_DIR /
    "gpt_oss_eligible_cohort_results.json"
)

OUTPUT_CSV = (
    RESULTS_DIR /
    "gpt_oss_eligible_cohort_results.csv"
)


# ============================================================
# STRUCTURED OUTPUT SCHEMA
# ============================================================

RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "clinical_concept_mentions",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "CKD_MENTIONED": {
                    "type": "boolean"
                },
                "ALBUMINURIA_MENTIONED": {
                    "type": "boolean"
                },
                "HYPERTENSION_MENTIONED": {
                    "type": "boolean"
                },
                "DIABETIC_NEPHROPATHY_MENTIONED": {
                    "type": "boolean"
                },
                "LISINOPRIL_MENTIONED": {
                    "type": "boolean"
                }
            },
            "required": [
                "CKD_MENTIONED",
                "ALBUMINURIA_MENTIONED",
                "HYPERTENSION_MENTIONED",
                "DIABETIC_NEPHROPATHY_MENTIONED",
                "LISINOPRIL_MENTIONED"
            ]
        }
    }
}


# ============================================================
# SYSTEM PROMPT
# ============================================================
#
# These instructions are aligned with the newest BRIM variable
# definitions for this eligible-cohort analysis.
# ============================================================

SYSTEM_PROMPT = """
You are performing clinical concept extraction from de-identified
clinical notes.

For each note, determine the values of exactly five boolean variables.

Return ONLY the structured JSON object requested by the schema.
Do not include explanations, reasoning, markdown, or any additional
fields.

============================================================
1. CKD_MENTIONED
============================================================

Determine whether the clinical note contains any evidence that the
patient has Chronic Kidney Disease (CKD).

Chronic Kidney Disease is a long-term condition involving gradual
loss of kidney function.

Evidence includes any mention of:
- CKD
- chronic kidney disease
- chronic kidney failure
- chronic renal insufficiency
- related diagnoses indicating that the patient has CKD

Synonyms and related terms count as evidence; the exact phrase "CKD"
is not required.

IMPORTANT:
Statements that deny, exclude, or rule out CKD should NOT count.

For example:
"The patient has stage 3 chronic kidney disease with declining
renal function." -> TRUE

"No history of chronic kidney disease." -> FALSE

"CKD ruled out." -> FALSE


============================================================
2. ALBUMINURIA_MENTIONED
============================================================

Determine whether the clinical note contains any mention of albuminuria
or related terms indicating albumin or protein in the urine.

The target terms are:
- albuminuria
- albuminuric
- microalbuminuria
- macroalbuminuria
- proteinuria

Return TRUE if ANY of these terms occur anywhere in the note.

The mention counts regardless of context, including:
- affirmed statements
- historical statements
- negated statements
- qualified statements

Do not require that the patient currently has albuminuria.

Examples:

"The patient has persistent albuminuria." -> TRUE

"No evidence of proteinuria." -> TRUE

"History of microalbuminuria." -> TRUE

If none of the target terms occur -> FALSE


============================================================
3. HYPERTENSION_MENTIONED
============================================================

Determine whether the clinical note contains any mention of:
- hypertension
- hypertensive

Return TRUE if either term occurs anywhere in the note.

The mention counts regardless of context or negation.

Examples:

"The patient has a history of hypertension." -> TRUE

"No history of hypertension." -> TRUE

"Hypertensive urgency was considered." -> TRUE

"Blood pressure is normal." -> FALSE if neither target term occurs


============================================================
4. DIABETIC_NEPHROPATHY_MENTIONED
============================================================

Determine whether the clinical note contains any mention of:
- diabetic nephropathy
- diabetic kidney disease
- diabetic nephrosis

Return TRUE if ANY of these terms occur anywhere in the note.

The mention counts regardless of context or negation.

Examples:

"The patient has diabetic nephropathy." -> TRUE

"No evidence of diabetic nephropathy." -> TRUE

"History of diabetic kidney disease." -> TRUE

If none of the target terms occur -> FALSE


============================================================
5. LISINOPRIL_MENTIONED
============================================================

Determine whether the clinical note contains any mention of the
medication lisinopril or any of its specified brand names.

Target medication terms:
- lisinopril
- Zestril
- Prinivil
- Qbrelis
- Zestoretic
- Prinzide

Return TRUE if ANY of these terms occur anywhere in the note.

The mention counts in any context, including:
- current use
- previous use
- discontinued use
- planned use
- questioned use
- negated mentions
- medication history

Do NOT infer lisinopril from generic terms such as:
- ACE inhibitor
- ACE-I
- ACEi

Examples:

"The patient was started on Prinivil for hypertension." -> TRUE

"Previously took lisinopril." -> TRUE

"Lisinopril was discontinued." -> TRUE

"No ACE inhibitors were prescribed." -> FALSE unless one of the
specified lisinopril terms is also explicitly present


============================================================
GENERAL RULES
============================================================

These variables are concept-mention/documentation variables.

Do not infer a target concept solely from unrelated findings.

Do not substitute general medical knowledge for the specified
target terminology.

Use only the definitions above.

Return exactly these five boolean fields:

CKD_MENTIONED
ALBUMINURIA_MENTIONED
HYPERTENSION_MENTIONED
DIABETIC_NEPHROPATHY_MENTIONED
LISINOPRIL_MENTIONED
"""


# ============================================================
# REQUIRED INPUT COLUMNS
# ============================================================

REQUIRED_COLUMNS = {
    "NOTE_ID",
    "PERSON_ID",
    "NOTE_DATETIME",
    "NOTE_TEXT",
    "NOTE_TITLE"
}


# ============================================================
# LOAD INPUT NOTES
# ============================================================

def load_input_notes():
    """Load and validate the BRIM-ready eligible-cohort CSV."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as infile:

        reader = csv.DictReader(infile)

        if reader.fieldnames is None:
            raise RuntimeError(
                "Input CSV has no header row."
            )

        missing = REQUIRED_COLUMNS.difference(
            reader.fieldnames
        )

        if missing:
            raise RuntimeError(
                "Input CSV is missing required columns: "
                f"{sorted(missing)}"
            )

        rows = list(reader)

    if len(rows) == 0:
        raise RuntimeError(
            "Input CSV contains no rows."
        )

    return rows


# ============================================================
# LOAD EXISTING RESULTS
# ============================================================

def load_existing_results():
    """
    Load previously completed results so the script can resume
    without reprocessing completed NOTE_IDs.
    """

    if not OUTPUT_JSON.exists():
        return []

    with OUTPUT_JSON.open(
        "r",
        encoding="utf-8"
    ) as infile:

        results = json.load(infile)

    if not isinstance(results, list):
        raise RuntimeError(
            "Existing JSON output must contain a list."
        )

    return results


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(results):
    """Save current results to JSON and CSV."""

    with OUTPUT_JSON.open(
        "w",
        encoding="utf-8"
    ) as outfile:

        json.dump(
            results,
            outfile,
            indent=2,
            ensure_ascii=False
        )

        outfile.write("\n")

    fieldnames = [
        "NOTE_ID",
        "PERSON_ID",
        "NOTE_DATETIME",
        "NOTE_TITLE",
        "CKD_MENTIONED",
        "ALBUMINURIA_MENTIONED",
        "HYPERTENSION_MENTIONED",
        "DIABETIC_NEPHROPATHY_MENTIONED",
        "LISINOPRIL_MENTIONED"
    ]

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as outfile:

        writer = csv.DictWriter(
            outfile,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for result in results:
            writer.writerow({
                field: result.get(field, "")
                for field in fieldnames
            })


# ============================================================
# VALIDATE MODEL RESPONSE
# ============================================================

def parse_model_response(response):
    """Parse and validate the structured model response."""

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "Model returned an empty response."
        )

    try:
        parsed = json.loads(content)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Model response was not valid JSON: {error}"
        ) from error

    expected_fields = {
        "CKD_MENTIONED",
        "ALBUMINURIA_MENTIONED",
        "HYPERTENSION_MENTIONED",
        "DIABETIC_NEPHROPATHY_MENTIONED",
        "LISINOPRIL_MENTIONED"
    }

    actual_fields = set(parsed.keys())

    if actual_fields != expected_fields:
        raise ValueError(
            "Unexpected model output fields. "
            f"Received: {sorted(actual_fields)}. "
            f"Expected: {sorted(expected_fields)}."
        )

    for field in expected_fields:

        if not isinstance(
            parsed[field],
            bool
        ):
            raise ValueError(
                f"{field} must be a boolean."
            )

    return parsed


# ============================================================
# CLASSIFY ONE NOTE
# ============================================================

def classify_note(
    note_id,
    note_text
):
    """Send exactly one structured inference request."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": (
                    f"NOTE_ID: {note_id}\n\n"
                    f"Clinical note:\n{note_text}"
                )
            }
        ],
        temperature=0,
        response_format=RESPONSE_FORMAT
    )

    return parse_model_response(response)


# ============================================================
# MAIN
# ============================================================

def main():

    rows = load_input_notes()

    results = load_existing_results()

    completed_ids = {
        str(result.get("NOTE_ID"))
        for result in results
        if result.get("NOTE_ID")
    }

    print(
        f"Model: {MODEL}"
    )

    print(
        f"Input file: {INPUT_FILE}"
    )

    print(
        f"Total input rows: {len(rows)}"
    )

    print(
        f"Previously completed: {len(completed_ids)}"
    )

    print()

    successful = 0
    skipped = 0
    failed = 0

    for index, row in enumerate(
        rows,
        start=1
    ):

        note_id = str(
            row.get(
                "NOTE_ID",
                ""
            )
        ).strip()

        note_text = row.get(
            "NOTE_TEXT",
            ""
        )

        if not note_id:

            print(
                f"[{index}/{len(rows)}] "
                "Skipping row with missing NOTE_ID"
            )

            failed += 1
            continue

        if not note_text.strip():

            print(
                f"[{index}/{len(rows)}] "
                f"Skipping {note_id}: "
                "NOTE_TEXT is blank"
            )

            failed += 1
            continue

        if note_id in completed_ids:

            print(
                f"[{index}/{len(rows)}] "
                f"Skipping {note_id} "
                "(already completed)"
            )

            skipped += 1
            continue

        print(
            f"[{index}/{len(rows)}] "
            f"Processing {note_id}"
        )

        try:

            labels = classify_note(
                note_id,
                note_text
            )

            result = {
                "NOTE_ID": note_id,
                "PERSON_ID": row.get(
                    "PERSON_ID",
                    ""
                ),
                "NOTE_DATETIME": row.get(
                    "NOTE_DATETIME",
                    ""
                ),
                "NOTE_TITLE": row.get(
                    "NOTE_TITLE",
                    ""
                ),
                "CKD_MENTIONED": labels[
                    "CKD_MENTIONED"
                ],
                "ALBUMINURIA_MENTIONED": labels[
                    "ALBUMINURIA_MENTIONED"
                ],
                "HYPERTENSION_MENTIONED": labels[
                    "HYPERTENSION_MENTIONED"
                ],
                "DIABETIC_NEPHROPATHY_MENTIONED": labels[
                    "DIABETIC_NEPHROPATHY_MENTIONED"
                ],
                "LISINOPRIL_MENTIONED": labels[
                    "LISINOPRIL_MENTIONED"
                ]
            }

            results.append(result)

            completed_ids.add(
                note_id
            )

            successful += 1

            # Save after every successful inference.
            save_results(results)

        except Exception as error:

            failed += 1

            print(
                f"ERROR for {note_id}: "
                f"{error}"
            )

            continue


    # Final save
    save_results(results)


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    unique_note_ids = {
        result["NOTE_ID"]
        for result in results
    }

    ckd_true = sum(
        result.get("CKD_MENTIONED") is True
        for result in results
    )

    ckd_false = sum(
        result.get("CKD_MENTIONED") is False
        for result in results
    )

    albuminuria_true = sum(
        result.get("ALBUMINURIA_MENTIONED") is True
        for result in results
    )

    albuminuria_false = sum(
        result.get("ALBUMINURIA_MENTIONED") is False
        for result in results
    )

    hypertension_true = sum(
        result.get("HYPERTENSION_MENTIONED") is True
        for result in results
    )

    hypertension_false = sum(
        result.get("HYPERTENSION_MENTIONED") is False
        for result in results
    )

    diabetic_nephropathy_true = sum(
        result.get(
            "DIABETIC_NEPHROPATHY_MENTIONED"
        ) is True
        for result in results
    )

    diabetic_nephropathy_false = sum(
        result.get(
            "DIABETIC_NEPHROPATHY_MENTIONED"
        ) is False
        for result in results
    )

    lisinopril_true = sum(
        result.get(
            "LISINOPRIL_MENTIONED"
        ) is True
        for result in results
    )

    lisinopril_false = sum(
        result.get(
            "LISINOPRIL_MENTIONED"
        ) is False
        for result in results
    )


    print()
    print(
        "=========================================="
    )
    print(
        "GPT-OSS-20B eligible cohort inference"
    )
    print(
        "=========================================="
    )

    print(
        f"Successful this run: {successful}"
    )

    print(
        f"Skipped previously completed: {skipped}"
    )

    print(
        f"Failed: {failed}"
    )

    print(
        f"Total saved results: {len(results)}"
    )

    print(
        f"Unique NOTE_IDs: {len(unique_note_ids)}"
    )

    print()

    print(
        "NOTE-LEVEL LABEL COUNTS"
    )

    print(
        f"CKD TRUE: {ckd_true}"
    )

    print(
        f"CKD FALSE: {ckd_false}"
    )

    print(
        f"Albuminuria TRUE: {albuminuria_true}"
    )

    print(
        f"Albuminuria FALSE: {albuminuria_false}"
    )

    print(
        f"Hypertension TRUE: {hypertension_true}"
    )

    print(
        f"Hypertension FALSE: {hypertension_false}"
    )

    print(
        f"Diabetic nephropathy TRUE: "
        f"{diabetic_nephropathy_true}"
    )

    print(
        f"Diabetic nephropathy FALSE: "
        f"{diabetic_nephropathy_false}"
    )

    print(
        f"Lisinopril TRUE: {lisinopril_true}"
    )

    print(
        f"Lisinopril FALSE: {lisinopril_false}"
    )

    print()

    print(
        f"JSON output: {OUTPUT_JSON}"
    )

    print(
        f"CSV output: {OUTPUT_CSV}"
    )


if __name__ == "__main__":
    main()
