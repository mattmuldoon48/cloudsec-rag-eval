# cloudsec-rag-eval

[![CI](https://github.com/mattmuldoon48/cloudsec-rag-eval/actions/workflows/ci.yml/badge.svg)](https://github.com/mattmuldoon48/cloudsec-rag-eval/actions/workflows/ci.yml)

Production-style local RAG evaluation system for cloud security guidance. This project demonstrates evaluated retrieval, grounded cited generation, experiment comparison, latency/cost tracking, report exports, and regression gates without adding a web app or deployment layer.

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

## Current Results

The current official-source-notes eval uses concise local notes derived from AWS IAM, AWS CloudTrail, and NIST SP 800-61 Rev. 3 sources. These are small starter evals, not broad benchmark claims.

| Experiment | Top-k | Questions | Recall@k | Faithfulness | Avg latency ms | Est. cost USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `official_notes` | `3` | `8` | `0.9375` | `1.0` | `3136.98` | `$0.012721` |
| `official_notes_top5` | `5` | `8` | `1.0` | `1.0` | `2200.65` | `$0.017195` |

The harder multi-document questions exposed a top-3 retrieval miss on a CloudTrail-plus-NIST question. The top-5 experiment recovered the missing source, preserved faithfulness, and passed the regression gate. Estimated cost increased because more retrieved evidence was included. The latency result is useful for this local run but should not be treated as a stable latency benchmark.

## Architecture

- `scripts/` - CLI entry points for ingest, indexing, question answering, evals, report export, run comparison, and regression checks
- `src/cloudsec_rag/` - modular pipeline code for schemas, config, ingestion, chunking, embeddings, retrieval, generation, evaluation, metrics, and reports
- `configs/` - named experiment configs for retrieval/chunking/prompt variants
- `data/raw_docs/` - local markdown source notes
- `data/doc_manifest.json` - source metadata, including whether docs are official-source notes or synthetic samples
- `data/eval_sets/` - JSONL eval questions with expected doc IDs and expected answer points
- `data/processed/` and `data/indexes/` - generated local artifacts, ignored by git
- `prompts/` - answer-generation and faithfulness-judge prompts
- `reports/runs/` and `reports/summaries/` - generated JSON, Markdown, and CSV reports, ignored by git
- `.github/workflows/ci.yml` - CI test run plus regression-gate fixture

## Data Sources

The repo includes two kinds of local docs:

- Synthetic starter docs, clearly marked as non-official
- Concise official-source notes based on public AWS and NIST pages

The official-source notes are intentionally short local summaries with source URLs, not full copies of upstream documentation.

Official-source note references:
- AWS IAM best practices: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- AWS access key guidance: https://docs.aws.amazon.com/IAM/latest/UserGuide/securing_access-keys.html
- AWS CloudTrail guide: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html
- AWS CloudTrail Insights: https://docs.aws.amazon.com/en_en/awscloudtrail/latest/userguide/logging-insights-events-with-cloudtrail.html
- NIST SP 800-61 Rev. 3: https://csrc.nist.gov/pubs/sp/800/61/r3/final

## Setup

Create a virtual environment with Python 3.11+:

```bash
python -m venv .venv
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

Set your OpenAI API key in `.env`:

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

Run the baseline eval:

```bash
python scripts/run_eval.py --config configs/official_notes.json
```

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

## Eval Report Contents

Each JSON report includes:

- `retrieval_recall_at_k`
- `average_faithfulness_score`
- `average_latency_ms`
- `estimated_cost_usd`
- per-question retrieved doc IDs
- generated answer text
- citation checks
- missing expected answer points
- judge rationale and unsupported-claim notes

Exported summaries include a compact Markdown overview and a per-question CSV.

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

```bash
python -m pytest
```

Current local status:

```text
19 passed
```

## Roadmap

1. Add more experiment configs for chunk size and prompt variants.
2. Add a small checked-in example summary report with sanitized outputs.
3. Add a lightweight dashboard once the core CLI workflow is stable.
