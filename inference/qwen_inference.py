#!/usr/bin/env python3
"""Run Qwen/vLLM concept extraction for the eligible progress note cohort.

This script sends clinical note text only to the local vLLM endpoint, writes
incremental checkpoints, and never includes NOTE_TEXT in output files.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


FIELDS = [
    "CKD_MENTIONED",
    "ALBUMINURIA_MENTIONED",
    "HYPERTENSION_MENTIONED",
    "DIABETIC_NEPHROPATHY_MENTIONED",
    "LISINOPRIL_MENTIONED",
]

OUTPUT_COLUMNS = ["NOTE_ID", "PERSON_ID", "NOTE_DATETIME", "NOTE_TITLE", *FIELDS]

SYSTEM_PROMPT = """You extract clinical concept mentions from a single progress note.
Return only one valid JSON object. Do not include markdown, prose, explanations, or reasoning.
Each JSON value must be a boolean.

Concept definitions:
CKD_MENTIONED: TRUE when the note contains evidence/mention of chronic kidney disease, including CKD, chronic kidney disease, chronic kidney failure, chronic renal insufficiency, or an equivalent explicit CKD diagnosis. Do not infer CKD solely from laboratory values or nonspecific renal findings. Ignore statements that deny or exclude CKD.
ALBUMINURIA_MENTIONED: TRUE when the note explicitly represents albuminuria or a specified equivalent, including albuminuria, albuminuric, microalbuminuria, macroalbuminuria, or proteinuria. Historical, negated, discontinued, planned, or contextualized explicit mentions count as TRUE.
HYPERTENSION_MENTIONED: TRUE when the note explicitly represents hypertension or hypertensive. Historical, negated, discontinued, planned, or contextualized explicit mentions count as TRUE.
DIABETIC_NEPHROPATHY_MENTIONED: TRUE when the note explicitly represents diabetic nephropathy, diabetic kidney disease, or diabetic nephrosis. Historical, negated, discontinued, planned, or contextualized explicit mentions count as TRUE.
LISINOPRIL_MENTIONED: TRUE when the note explicitly mentions lisinopril or one of these specified brand/combination names: Zestril, Prinivil, Qbrelis, Zestoretic, or Prinzide. Historical, negated, discontinued, planned, or contextualized explicit mentions count as TRUE.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Qwen concept extraction against a local vLLM endpoint."
    )
    parser.add_argument("--input", default="eligible_progressnotes_BRIM_ready.csv")
    parser.add_argument("--output-csv", default="qwen_eligible_cohort_results.csv")
    parser.add_argument("--output-json", default="qwen_eligible_cohort_results.json")
    parser.add_argument("--failures-jsonl", default="qwen_eligible_cohort_failures.jsonl")
    parser.add_argument("--endpoint", default="http://127.0.0.1:18000/v1/chat/completions")
    parser.add_argument("--model", default="Qwen/Qwen3-8B-AWQ")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--max-note-chars", type=int, default=24000)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"NOTE_ID", "PERSON_ID", "NOTE_DATETIME", "NOTE_TEXT", "NOTE_TITLE"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Input is missing required columns: {sorted(missing)}")
        return list(reader)


def load_completed(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as f:
        return {row["NOTE_ID"] for row in csv.DictReader(f) if row.get("NOTE_ID")}


def ensure_csv(path: Path, overwrite: bool) -> None:
    if overwrite and path.exists():
        path.unlink()
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS).writeheader()


def post_json(url: str, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_json_object(text: str) -> dict[str, Any]:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model response")
    return json.loads(match.group(0))


def validate_result(result: dict[str, Any]) -> dict[str, bool]:
    if set(result) != set(FIELDS):
        raise ValueError(f"Unexpected JSON keys: {sorted(result)}")
    validated: dict[str, bool] = {}
    for field in FIELDS:
        value = result[field]
        if not isinstance(value, bool):
            raise ValueError(f"{field} is not a boolean")
        validated[field] = value
    return validated


def classify_note(args: argparse.Namespace, note_text: str) -> dict[str, bool]:
    if len(note_text) > args.max_note_chars:
        note_text = note_text[: args.max_note_chars]
    user_prompt = f"""Classify this progress note for the five requested concept mentions.

Return exactly this JSON shape with boolean values:
{{
  "CKD_MENTIONED": true/false,
  "ALBUMINURIA_MENTIONED": true/false,
  "HYPERTENSION_MENTIONED": true/false,
  "DIABETIC_NEPHROPATHY_MENTIONED": true/false,
  "LISINOPRIL_MENTIONED": true/false
}}

Progress note:
{note_text}

/no_think"""
    payload = {
        "model": args.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
        "top_p": 1,
        "max_tokens": 256,
        "chat_template_kwargs": {"enable_thinking": False},
    }

    last_error: Exception | None = None
    for attempt in range(args.retries + 1):
        try:
            response = post_json(args.endpoint, payload, args.timeout)
            content = response["choices"][0]["message"]["content"]
            return validate_result(extract_json_object(content))
        except (HTTPError, URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            if attempt < args.retries:
                time.sleep(2**attempt)
    raise RuntimeError(str(last_error))


def write_json_from_csv(csv_path: Path, json_path: Path) -> None:
    with csv_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    normalized: list[dict[str, Any]] = []
    for row in rows:
        item: dict[str, Any] = {key: row[key] for key in ["NOTE_ID", "PERSON_ID", "NOTE_DATETIME", "NOTE_TITLE"]}
        for field in FIELDS:
            item[field] = row[field].strip().lower() == "true"
        normalized.append(item)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=2)
        f.write("\n")


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_csv = Path(args.output_csv)
    output_json = Path(args.output_json)
    failures_jsonl = Path(args.failures_jsonl)

    rows = load_rows(input_path)
    note_ids = [row["NOTE_ID"] for row in rows]
    unique_note_ids = set(note_ids)
    unique_person_ids = {row["PERSON_ID"] for row in rows}
    duplicate_count = len(note_ids) - len(unique_note_ids)
    print(
        "input_validation "
        f"rows={len(rows)} unique_note_ids={len(unique_note_ids)} "
        f"unique_patients={len(unique_person_ids)} duplicate_note_ids={duplicate_count}"
    )

    if duplicate_count:
        raise ValueError("Unexpected duplicate NOTE_IDs found; stopping before inference")

    ensure_csv(output_csv, args.overwrite)
    completed = set() if args.overwrite else load_completed(output_csv)
    candidates = [row for row in rows if row["NOTE_ID"] not in completed]
    if args.limit is not None:
        candidates = candidates[: args.limit]

    successes = 0
    failures = 0
    with output_csv.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_COLUMNS)
        for row in candidates:
            try:
                labels = classify_note(args, row.get("NOTE_TEXT", ""))
                output_row = {
                    "NOTE_ID": row["NOTE_ID"],
                    "PERSON_ID": row["PERSON_ID"],
                    "NOTE_DATETIME": row["NOTE_DATETIME"],
                    "NOTE_TITLE": row["NOTE_TITLE"],
                    **labels,
                }
                writer.writerow(output_row)
                csv_file.flush()
                successes += 1
            except Exception as exc:  # noqa: BLE001 - retain failures without note text.
                failures += 1
                failure = {"NOTE_ID": row["NOTE_ID"], "error": str(exc)}
                with failures_jsonl.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(failure) + "\n")
            if args.sleep:
                time.sleep(args.sleep)

    write_json_from_csv(output_csv, output_json)
    print(
        "run_complete "
        f"attempted={len(candidates)} successes={successes} failures={failures} "
        f"output_csv={output_csv} output_json={output_json}"
    )
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
