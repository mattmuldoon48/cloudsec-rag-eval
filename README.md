# cloudsec-rag-eval

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
- `data/processed/` – intermediate serialized docs and chunks.
- `data/indexes/` – saved chunks, embeddings, and index metadata.
- `data/eval_sets/` – evaluation questions with expected doc coverage.
- `prompts/` – answer generation and faithfulness judge prompts.
- `reports/runs/` – saved retrieval and answer evaluation results.

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

Place new markdown files in `data/raw_docs/`. Then run:

```bash
python scripts/ingest_docs.py
```

The loader currently skips `data/raw_docs/README.md` so folder instructions do not become retrieval evidence.

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

## Roadmap

1. Add more realistic cloud security documentation.
2. Add richer regression comparisons for prompt/embedding changes.
3. Add markdown or CSV report exports for portfolio-friendly summaries.
4. Add a lightweight dashboard once the core CLI workflow is stable.
