# cloudsec-rag-eval

[![CI](https://github.com/mattmuldoon48/cloudsec-rag-eval/actions/workflows/ci.yml/badge.svg)](https://github.com/mattmuldoon48/cloudsec-rag-eval/actions/workflows/ci.yml)

A local RAG evaluation system for cloud security guidance built as a production-minded portfolio project.

## Project overview

This project demonstrates how to build and evaluate a local retrieval-augmented generation pipeline for cloud/security documentation. It focuses on:
- ingesting raw documentation files
- chunking text into consistent embeddings
- embedding and indexing locally
- retrieving the best evidence for a question
- generating answers with explicit citations
- evaluating retrieval performance with recall@k and latency tracking
- judging whether generated answers stay faithful to retrieved evidence
- saving reproducible evaluation reports

## Why evaluated RAG matters

A true production-ready RAG system is more than a chat interface. It requires evidence-aware retrieval, grounded answer generation, and repeatable evaluation so teams can measure improvements instead of guessing. This project is intentionally focused on evaluation and grounding rather than a full web app.

## Architecture

- `scripts/` – CLI entry points for ingest, index building, question answering, evaluation, and run comparison.
- `src/cloudsec_rag/` – modular pipeline code for ingestion, chunking, embeddings, retrieval, generation, and evaluation.
- `configs/` – named experiment configs for chunking, retrieval, prompts, and index locations.
- `data/raw_docs/` – source markdown docs.
- `data/doc_manifest.json` – source metadata for raw docs, including whether docs are official or synthetic.
- `data/processed/` – intermediate serialized docs and chunks.
- `data/indexes/` – saved chunks, embeddings, and index metadata.
- `data/eval_sets/` – evaluation questions with expected doc coverage.
- `prompts/` – answer generation and faithfulness judge prompts.
- `reports/runs/` – saved retrieval and answer evaluation JSON results.
- `reports/summaries/` – generated Markdown and CSV report exports.

## Setup

Create a virtual environment with Python 3.11+:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
```

If you prefer Poetry, this project also includes Poetry metadata:

```bash
poetry install
```

Copy the example environment file:

```bash
cp .env.example .env
```

Set your OpenAI API key in `.env`.

## Environment variables

- `OPENAI_API_KEY` – required for OpenAI API access.
- `OPENAI_EMBEDDING_MODEL` – default: `text-embedding-3-small`
- `OPENAI_GENERATION_MODEL` – default: `gpt-4.1-mini`

## How to add docs

Place new markdown files in `data/raw_docs/`, then add metadata to `data/doc_manifest.json`.

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

The loader currently skips `data/raw_docs/README.md` so folder instructions do not become retrieval evidence. The starter docs are synthetic samples and are clearly marked as non-official in the manifest.

The repo also includes concise official-source notes based on AWS IAM, AWS CloudTrail, and NIST SP 800-61 Rev. 3. These are intentionally short local summaries with source URLs, not full copies of the upstream documentation.

## How to build the index

```bash
python scripts/build_index.py
```

This will create:
- `data/indexes/chunks.jsonl`
- `data/indexes/embeddings.npy`
- `data/indexes/index_config.json`

You can also build a named experiment:

```bash
python scripts/build_index.py --config configs/baseline.json
```

Named configs can write to separate index folders such as `data/indexes/baseline/`, which makes regression comparisons cleaner.

To build the official-source-notes experiment:

```bash
python scripts/build_index.py --config configs/official_notes.json
```

To build the top-5 retrieval variant:

```bash
python scripts/build_index.py --config configs/official_notes_top5.json
```

## How to ask a question

```bash
python scripts/ask.py "What practices help enforce least privilege in AWS IAM?"
```

To ask against a named experiment index:

```bash
python scripts/ask.py "What practices help enforce least privilege in AWS IAM?" --config configs/baseline.json
```

The CLI prints a grounded answer plus a numbered source list.

## How to run evals

```bash
python scripts/run_eval.py
```

A new JSON report is saved under `reports/runs/`.

To run a named experiment:

```bash
python scripts/run_eval.py --config configs/baseline.json
```

To run the official-source-notes eval set:

```bash
python scripts/run_eval.py --config configs/official_notes.json
```

To run the top-5 retrieval variant:

```bash
python scripts/run_eval.py --config configs/official_notes_top5.json
```

## How to export reports

Turn a JSON run report into a readable Markdown summary and per-question CSV:

```bash
python scripts/export_report.py reports/runs/run_baseline_<timestamp>_<run_id>.json
```

By default, exports are written to `reports/summaries/`.

## How to check regressions

Compare a baseline run against a candidate run and fail if quality drops or latency rises too much:

```bash
python scripts/check_regression.py reports/runs/baseline.json reports/runs/candidate.json
```

Default gates:
- recall delta must be at least `-0.01`
- faithfulness delta must be at least `-0.01`
- latency increase must be no more than `1000 ms`

You can tune thresholds:

```bash
python scripts/check_regression.py reports/runs/baseline.json reports/runs/candidate.json \
  --min-recall-delta -0.02 \
  --min-faithfulness-delta -0.02 \
  --max-latency-increase-ms 1500
```

## Example output

Question answering prints a cited answer and source list:

```text
=== Answer ===
Least privilege in AWS IAM is supported by using fine-grained policies,
granting only task-required permissions, avoiding broad `*` actions, and
using roles instead of long-lived credentials [1].

=== Sources ===
[1] data/raw_docs/aws_iam_best_practices.md (score=0.812)
```

- `reports/runs/run_<timestamp>.json` contains:
  - `retrieval_recall_at_k`
  - `average_faithfulness_score`
  - `average_latency_ms`
  - `estimated_cost_usd`
  - `per_question_results`

Each per-question result includes retrieved doc IDs, recall@k, the generated answer, a judge faithfulness score, citation checks, and any missing expected answer points.

Exported summaries include top-line metrics plus a compact per-question table suitable for portfolio notes or regression review.

## Baseline snapshot

The current official-source-notes baseline was run locally against concise notes derived from official AWS IAM, AWS CloudTrail, and NIST SP 800-61 Rev. 3 sources.

Configuration:
- Experiment: `official_notes`
- Eval set: `data/eval_sets/cloudsec_official_notes_eval_v1.jsonl`
- Top-k: `3`
- Chunk size: `700`
- Chunk overlap: `100`

Latest local result:
- Questions: `8`
- Retrieval recall@k: `0.9375`
- Average faithfulness score: `1.0`
- Average latency: `3136.98 ms`
- Estimated cost: `$0.012721`
- Missing expected answer points: `0`

These metrics are from a small starter eval set and should be treated as a baseline sanity check, not a broad benchmark claim. The eval set includes two multi-document questions; top-3 retrieval missed one expected source on the CloudTrail-plus-NIST question.

## Experiment comparison

The `official_notes_top5` experiment keeps chunking and prompts fixed while changing retrieval from `top_k=3` to `top_k=5`.

Latest local comparison:

| Experiment | Recall@k | Faithfulness | Avg latency ms | Est. cost USD |
| --- | ---: | ---: | ---: | ---: |
| `official_notes` | `0.9375` | `1.0` | `3136.98` | `$0.012721` |
| `official_notes_top5` | `1.0` | `1.0` | `2200.65` | `$0.017195` |

Observed result on the small starter eval: top-5 recovered the missing source for the harder multi-document question, preserved faithfulness, and passed the regression gate. Estimated cost increased because more retrieved evidence was included. The latency difference was favorable in this run, but this small sample should not be treated as a stable latency benchmark.

## Roadmap

1. Add CI regression-gate fixtures once stable baseline artifacts are checked in.
2. Expand the official-source eval set with harder multi-document questions.
3. Add a lightweight dashboard once the core CLI workflow is stable.
