# Checked-in example reports

`reports/runs/` and `reports/summaries/` are generated locally and ignored by git. This directory contains sanitized Markdown examples copied from real local runs so benchmark claims can be reviewed without requiring OpenAI calls.

## Included artifacts

| File | Source run | What it supports |
| --- | --- | --- |
| `official_notes_2026-05-25_summary.md` | `reports/runs/run_official_notes_2026-05-25T22-25-06Z_efcf79b0-4b44-4a71-a48b-342aa8e000c3.json` | Top-3 official-source-notes metrics shown in the README. |
| `official_notes_top5_2026-05-25_summary.md` | `reports/runs/run_official_notes_top5_2026-05-25T22-27-41Z_2590bdc2-a9d8-4a25-bd6b-7ff3cec8bbd0.json` | Top-5 official-source-notes metrics shown in the README and the example report shape. |

## What these artifacts prove

They show that the checked-in 25-question official-source-notes eval produced the recorded recall@k, faithfulness, latency, estimated-cost, failed-retrieval, and missing-point values for those local runs.

They do not prove production readiness, general cloud-security accuracy, stable latency, or performance on upstream AWS/NIST documentation. The source corpus is small and uses concise local notes.

## Historical local reports

Older generated files may exist under ignored `reports/runs/` or `reports/summaries/` directories in a working tree. Earlier 8-question reports are historical local artifacts only; use the 25-question artifacts in this directory for current README claims.
