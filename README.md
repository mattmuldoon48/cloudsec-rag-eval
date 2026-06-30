# cloudsec-rag-eval

[![CI](https://github.com/mattmuldoon48/cloudsec-rag-eval/actions/workflows/ci.yml/badge.svg)](https://github.com/mattmuldoon48/cloudsec-rag-eval/actions/workflows/ci.yml)

Local RAG evaluation system for cloud security guidance. This project demonstrates evaluated retrieval, grounded cited generation, experiment comparison, latency/cost tracking, report exports, and regression gates without adding a web app or deployment layer.

## What This Demonstrates

- Local document ingestion, chunking, OpenAI embeddings, and vector retrieval
- Cited answer generation using retrieved evidence
- Retrieval recall@k evaluation against expected source documents
- LLM-as-judge faithfulness evaluation for generated answers
- Multi-document eval questions that expose retrieval misses
- Named experiment configs for top-k/chunking/prompt comparisons
- Cost and latency tracking in every eval report
- Markdown/CSV report exports for review and portfolio summaries
- CI-backed tests and a regression gate for eval-run comparisons

## Why Evaluated RAG Matters

Production RAG is more than a chat interface over documents. It needs evidence-aware retrieval, grounded generation, and repeatable evals so changes to chunking, retrieval depth, prompts, and models can be measured instead of guessed. This repo focuses on that evaluation loop.

## Eval Coverage

The current official-source-notes eval uses concise local notes derived from AWS IAM, AWS CloudTrail, and NIST SP 800-61 Rev. 3 sources. The eval set now includes `25` questions across:

- single-source retrieval
- multi-source retrieval
- ambiguous cloud security questions
- not-enough-information questions
- IAM plus CloudTrail questions
- questions with `avoided_doc_ids` to check that retrieval does not pull unrelated docs

| Experiment | Top-k | Questions | Recall@k | Faithfulness | Avg latency ms | Est. cost USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `official_notes` | `3` | `25` | `0.9067` | `1.0` | `3401.76` | `$0.036722` |
| `official_notes_top5` | `5` | `25` | `0.9733` | `1.0` | `2873.9` | `$0.05144` |

The expanded 25-question eval exposed several harder multi-document retrieval misses. The top-5 experiment improved recall by `0.0666`, preserved average faithfulness, and passed the regression gate. It still missed expected sources on two questions, which is useful signal for future retrieval work. Estimated cost increased because more retrieved evidence was included. The latency result is useful for this local run but should not be treated as a stable latency benchmark. The latency column is a local phase-timing average, and the cost column is an approximate estimate, not provider billing data. These numbers are backed by sanitized checked-in summaries under `reports/examples/`.

## Architecture

- `scripts/` - CLI entry points for ingest, indexing, question answering, evals, report export, run comparison, and regression checks
- `src/cloudsec_rag/` - modular pipeline code for schemas, config, ingestion, chunking, embeddings, retrieval, generation, evaluation, metrics, and reports
- `configs/` - named experiment configs for retrieval/chunking/prompt variants
- `data/raw_docs/` - local markdown source notes
- `data/doc_manifest.json` - source metadata, including whether docs are official-source notes or synthetic samples
- `data/eval_sets/` - JSONL eval questions with expected doc IDs, expected answer points, and optional avoided doc IDs
- `data/processed/` and `data/indexes/` - generated local artifacts, ignored by git
- `prompts/` - answer-generation and faithfulness-judge prompts
- `reports/runs/` and `reports/summaries/` - generated JSON, Markdown, and CSV reports, ignored by git
- `reports/examples/` - sanitized checked-in example reports that support the README metrics
- `docs/eval_protocol.md` - methodology notes for sources, recall@k, faithfulness scoring, limitations, and expansion
- `.github/workflows/ci.yml` - CI test run plus regression-gate fixture

## Data Sources

The repo includes two kinds of local docs:

- Synthetic starter docs, clearly marked as non-official. These support the starter eval set and should not be treated as AWS, NIST, or production guidance.
- Concise official-source notes based on public AWS and NIST pages. These support the current 25-question README metrics.

The official-source notes are intentionally short local summaries with source URLs, not full copies of upstream documentation. See `docs/eval_protocol.md` for the full eval methodology and limitations.

Official-source note references:
- AWS IAM best practices: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- AWS access key guidance: https://docs.aws.amazon.com/IAM/latest/UserGuide/securing_access-keys.html
- AWS CloudTrail guide: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html
- AWS CloudTrail Insights: https://docs.aws.amazon.com/en_en/awscloudtrail/latest/userguide/logging-insights-events-with-cloudtrail.html
- NIST SP 800-61 Rev. 3: https://csrc.nist.gov/pubs/sp/800/61/r3/final

## Setup

Create a virtual environment with Python 3.11+:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
```

If you prefer Poetry:

```bash
poetry install
```

Copy the example environment file:

```bash
cp .env.example .env
```

Set your OpenAI API key in `.env`. The model names shown in `.env.example` match the checked-in configs:

```bash
OPENAI_API_KEY=
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_GENERATION_MODEL=gpt-4.1-mini
```

## Demo Commands

Build the official-source-notes index:

```bash
python scripts/build_index.py --config configs/official_notes.json
```

Ask a cited question:

```bash
python scripts/ask.py "How can IAM least privilege and CloudTrail auditing work together to reduce cloud security risk?" --config configs/official_notes.json
```

A good cited answer should stay inside the retrieved evidence, cite the source notes it used, and say when the local corpus is insufficient. Treat uncited operational advice as a review finding, not as validated guidance.

Run the official-source eval:

```bash
python scripts/run_eval.py --config configs/official_notes.json
```

The eval command writes a timestamped JSON report under `reports/runs/` and prints the saved report path; review aggregate retrieval, faithfulness, latency, and estimated-cost metrics in that JSON or in exported summaries. Generated full reports stay local; only sanitized examples should be committed.

Run the top-5 retrieval experiment:

```bash
python scripts/build_index.py --config configs/official_notes_top5.json
python scripts/run_eval.py --config configs/official_notes_top5.json
```

Compare two runs:

```bash
python scripts/compare_runs.py reports/runs/baseline.json reports/runs/candidate.json
```

Check regression gates:

```bash
python scripts/check_regression.py reports/runs/baseline.json reports/runs/candidate.json
```

Export a report:

```bash
python scripts/export_report.py reports/runs/run_official_notes_<timestamp>_<run_id>.json
```

Sanitized checked-in examples are available under `reports/examples/`, including the current top-5 summary at `reports/examples/official_notes_top5_2026-05-25_summary.md`.

Keep checked-in examples tied to exported summaries from completed local runs. Before replacing one, verify the config name, eval set, top-k, and timestamp match the README metrics it supports.

## Adding Docs

Place markdown or text files in `data/raw_docs/`, then add metadata to `data/doc_manifest.json`.

Example manifest entry:

```json
{
  "doc_id": "aws_iam_best_practices",
  "title": "AWS IAM Best Practices (sample)",
  "source_type": "sample",
  "source_url": null,
  "is_official": false,
  "notes": "Synthetic starter document for local evaluation. Not official AWS documentation."
}
```

Then run:

```bash
python scripts/ingest_docs.py
```

The loader skips `data/raw_docs/README.md` so folder instructions do not become retrieval evidence.

Rebuild each affected experiment index after changing raw docs, manifest metadata, chunk size, or chunk overlap. `ask.py` and `run_eval.py` read from the configured `data/indexes/` directory, so ingestion alone does not update the vectors used by demos or evals.

## Eval Report Contents

Each JSON report includes:

- `retrieval_recall_at_k`
- `average_faithfulness_score`
- `average_latency_ms`
- `estimated_cost_usd`
- per-question retrieved doc IDs
- avoided doc IDs and whether any were retrieved
- generated answer text
- citation checks
- missing expected answer points
- judge rationale and unsupported-claim notes

Exported summaries include a compact Markdown overview and a per-question CSV. The committed examples in `reports/examples/` are sanitized summaries; generated full reports remain local by default.

## Regression Gates

`scripts/check_regression.py` compares a baseline run against a candidate run and exits non-zero if:

- recall delta is below the allowed threshold
- faithfulness delta is below the allowed threshold
- latency increase is above the allowed threshold

Defaults:

- recall delta must be at least `-0.01`
- faithfulness delta must be at least `-0.01`
- latency increase must be no more than `1000 ms`

CI runs pytest plus a regression-gate fixture so the comparison mechanism is exercised without OpenAI calls.

## Tests

Run the current test suite with:

```bash
python -m pytest
```

## Roadmap

1. Add more experiment configs for chunk size and prompt variants.
2. Add a lightweight dashboard once the core CLI workflow is stable.
