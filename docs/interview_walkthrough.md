# Interview Walkthrough: cloudsec-rag-eval

This document is for local interview prep. It explains how the project was built, which tools were used, what each major file does, and how to talk about the engineering decisions.

## Short Pitch

`cloudsec-rag-eval` is a local Python CLI project that demonstrates production-minded RAG evaluation for cloud security guidance.

The main point of the project is not “chat with docs.” The point is to show an evaluated RAG workflow:

- ingest source documents
- chunk them deterministically
- embed chunks with OpenAI embeddings
- retrieve relevant evidence with a local vector index
- generate cited answers
- evaluate retrieval quality
- evaluate answer faithfulness
- compare experiments
- track latency and estimated cost
- export reports
- fail CI if eval quality regresses

In an interview, I would frame it as:

> I built a local RAG evaluation harness for cloud security documentation. Instead of stopping at a chatbot, I focused on the production loop: retrieval quality, grounded answers, repeatable evals, experiment comparison, cost/latency tracking, and regression gates.

## Why I Built It This Way

The project is intentionally scoped as a local CLI system. I avoided FastAPI, React, Docker, auth, dashboards, and deployment because those would distract from the core AI engineering signal.

The goal was to show that I understand the parts of RAG that matter in production:

- whether retrieval found the right evidence
- whether the answer stayed grounded in that evidence
- whether a change improved or regressed quality
- what the latency and cost tradeoffs looked like
- whether the workflow can be repeated reliably

This makes the project more credible than a simple “ask questions over PDFs” app.

## Tools And Libraries Used

### Python

Python is the main language because it is the standard ecosystem for applied AI, evaluation, embeddings, and data processing.

### OpenAI SDK

Used directly instead of LangChain or LangGraph.

Why:

- keeps the implementation transparent
- makes API calls easy to reason about
- avoids hiding retrieval/eval logic behind framework abstractions
- shows I understand the pipeline mechanics myself

Used for:

- embeddings with `text-embedding-3-small`
- answer generation with `gpt-4.1-mini`
- faithfulness judging with `gpt-4.1-mini`

### Pydantic

Used for schemas and configuration.

Why:

- structured validation for documents, chunks, eval questions, generated answers, and run reports
- cleaner data contracts between pipeline stages
- easier to extend later

### scikit-learn

Used `NearestNeighbors` with cosine distance for local vector search.

Why:

- simple local vector index
- no server dependency
- good enough for a focused MVP
- easier to explain than running a separate vector DB

### NumPy

Used for storing and loading embedding arrays with `.npy` files.

### python-dotenv / pydantic-settings

Used for local environment variables:

- `OPENAI_API_KEY`
- `OPENAI_EMBEDDING_MODEL`
- `OPENAI_GENERATION_MODEL`

### pytest

Used for automated tests around:

- chunking behavior
- schema validation
- retrieval recall metric
- answer-eval helpers
- config loading
- report export
- run comparison and regression gates

### GitHub Actions

Used for CI.

The workflow runs:

- pytest
- a regression-gate fixture using checked-in sample eval reports

This shows the eval workflow can be enforced automatically.

## Project Structure

### `README.md`

Public-facing project overview.

It explains:

- what the project demonstrates
- current measured results
- architecture
- setup
- demo commands
- data sources
- regression gates
- roadmap

This is the file a recruiter or hiring manager is most likely to read first.

### `.env.example`

Template for required environment variables.

The real `.env` is ignored by git so the API key does not get committed.

### `.gitignore`

Prevents committing:

- `.env`
- generated processed docs
- embedding indexes
- eval run JSON files
- generated report summaries
- Python cache files

This matters because embeddings and eval runs are reproducible artifacts, while source files and configs should be tracked.

### `pyproject.toml`

Project metadata and dependencies.

Includes:

- Python dependency ranges
- package configuration
- pytest config with `pythonpath = ["src"]`

## Data Files

### `data/raw_docs/`

Contains local markdown documents.

There are two kinds of docs:

- synthetic starter docs
- concise official-source notes

The official-source notes are based on public AWS/NIST pages, but they are not full copied documentation. They are short local summaries with source URLs.

Important docs:

- `aws_iam_best_practices.md`
- `aws_logging_monitoring.md`
- `incident_response_basics.md`
- `aws_iam_official_notes.md`
- `aws_cloudtrail_official_notes.md`
- `nist_sp800_61r3_official_notes.md`

### `data/doc_manifest.json`

Tracks source metadata for each raw doc.

Fields include:

- `doc_id`
- `title`
- `source_type`
- `source_url`
- `is_official`
- `notes`

Why this matters:

- makes source provenance explicit
- distinguishes synthetic docs from official-source notes
- avoids claiming synthetic docs are official AWS/NIST content
- gives future ingestion a clean metadata pattern

### `data/eval_sets/cloudsec_eval_v1.jsonl`

Starter eval set for the synthetic sample docs.

Each line is an eval question with:

- question ID
- question text
- expected document IDs
- expected answer points

### `data/eval_sets/cloudsec_official_notes_eval_v1.jsonl`

Eval set for the official-source notes.

This is the more portfolio-relevant 25-question eval set. It includes single-source, multi-source, ambiguous, not-enough-information, and avoided-document questions. The multi-source questions are important because they test whether retrieval can find evidence across more than one document.

Example:

- IAM least privilege + CloudTrail auditing
- CloudTrail evidence + NIST incident response coordination

## Config Files

### `configs/baseline.json`

Baseline config for the synthetic sample docs.

### `configs/high_recall_top5.json`

Synthetic-doc variant with `top_k = 5`.

### `configs/official_notes.json`

Main official-source-notes baseline.

Key settings:

- `experiment_name`: `official_notes`
- `chunk_size`: `700`
- `chunk_overlap`: `100`
- `top_k`: `3`
- `eval_set_path`: `data/eval_sets/cloudsec_official_notes_eval_v1.jsonl`

### `configs/official_notes_top5.json`

Official-source experiment variant.

Only retrieval depth changes:

- `top_k`: `5`

This is useful because the project can show a measured tradeoff on the checked-in 25-question eval:

- top-3 averaged `0.9067` recall@k with four retrieval misses
- top-5 averaged `0.9733` recall@k with two retrieval misses
- estimated cost increased because more evidence was sent to generation/judging

## Prompt Files

### `prompts/answer_v1.txt`

Prompt used for answer generation.

It instructs the model to:

- answer as a cloud security engineer
- use only retrieved evidence
- cite sources as `[1]`, `[2]`, etc.
- avoid hallucinating unsupported facts

### `prompts/faithfulness_judge_v1.txt`

Prompt used by the judge model.

It asks the model to return JSON with:

- `faithfulness_score`
- `is_faithful`
- `unsupported_claims`
- `rationale`

This makes answer evaluation structured instead of free-form.

## Source Code Files

### `src/cloudsec_rag/schemas.py`

Defines Pydantic models:

- `Document`
- `Chunk`
- `RetrievedChunk`
- `EvalQuestion`
- `GeneratedAnswer`
- `EvalRunResult`

These models are the data contracts for the whole pipeline.

### `src/cloudsec_rag/config.py`

Loads settings from:

- environment variables
- optional experiment config JSON files

Important function:

- `load_settings(config_path)`

This allows commands like:

```bash
python scripts/run_eval.py --config configs/official_notes_top5.json
```

### `src/cloudsec_rag/ingest.py`

Loads raw markdown/text files from `data/raw_docs/`.

Important behavior:

- skips `README.md`
- applies metadata from `data/doc_manifest.json`
- writes processed docs/chunks to `data/processed/`

### `src/cloudsec_rag/chunk.py`

Implements deterministic character-based chunking.

Configurable:

- `chunk_size`
- `chunk_overlap`

Important details:

- avoids empty chunks
- validates invalid overlap settings
- preserves metadata from documents into chunks

### `src/cloudsec_rag/llm_client.py`

Small wrapper around the OpenAI SDK.

Handles:

- embedding requests
- generation requests

I kept this thin on purpose so OpenAI calls remain easy to inspect.

### `src/cloudsec_rag/embed.py`

Embeds chunks using the OpenAI embedding model and returns a NumPy array.

### `src/cloudsec_rag/index_store.py`

Saves and loads local index artifacts:

- `chunks.jsonl`
- `embeddings.npy`
- `index_config.json`

This keeps the index local and reproducible.

### `src/cloudsec_rag/retrieve.py`

Implements retrieval using `sklearn.neighbors.NearestNeighbors`.

Uses cosine distance and returns `RetrievedChunk` objects with:

- score
- text
- metadata
- source path
- source type/source URL flags

### `src/cloudsec_rag/generate.py`

Builds the evidence section and calls the generation model.

It formats retrieved chunks as numbered evidence sources so the model can cite them.

### `src/cloudsec_rag/metrics.py`

Contains simple metric helpers:

- `recall_at_k`
- `average_latency_ms`
- `estimate_cost_usd`

The cost estimate is approximate and intentionally presented as an estimate.

### `src/cloudsec_rag/evaluate_retrieval.py`

Main eval pipeline.

For each eval question:

1. retrieve top-k chunks
2. calculate retrieval recall@k
3. generate an answer
4. judge answer faithfulness
5. record latency and estimated cost
6. write per-question results

This is the core of the project.

### `src/cloudsec_rag/evaluate_answers.py`

Answer-level evaluation helpers.

Includes:

- citation detection
- citation coverage
- expected answer point matching
- faithfulness judge call
- JSON parsing from judge output

### `src/cloudsec_rag/compare_runs.py`

Compares two run JSON files.

Computes deltas for:

- recall
- faithfulness
- latency

Also includes `check_regression()`, which decides whether a candidate run passes or fails threshold rules.

### `src/cloudsec_rag/export_report.py`

Exports eval reports to:

- Markdown summary
- per-question CSV

Useful for portfolio review and regression analysis.

## Script Files

### `scripts/ingest_docs.py`

Loads raw docs, applies metadata, chunks them, and writes processed artifacts.

Command:

```bash
python scripts/ingest_docs.py
```

### `scripts/build_index.py`

Runs ingestion, embeds chunks, and saves local index artifacts.

Command:

```bash
python scripts/build_index.py --config configs/official_notes.json
```

### `scripts/ask.py`

CLI question-answering entry point.

Command:

```bash
python scripts/ask.py "How can IAM least privilege and CloudTrail auditing work together to reduce cloud security risk?" --config configs/official_notes.json
```

### `scripts/run_eval.py`

Runs the full eval pipeline and saves a JSON report.

Command:

```bash
python scripts/run_eval.py --config configs/official_notes.json
```

### `scripts/compare_runs.py`

Compares two eval run reports.

Command:

```bash
python scripts/compare_runs.py reports/runs/baseline.json reports/runs/candidate.json
```

### `scripts/check_regression.py`

Fails if a candidate run regresses beyond thresholds.

Command:

```bash
python scripts/check_regression.py reports/runs/baseline.json reports/runs/candidate.json
```

This is important because it demonstrates how evals can become part of a quality gate.

### `scripts/export_report.py`

Exports a run JSON to Markdown and CSV.

Command:

```bash
python scripts/export_report.py reports/runs/run_official_notes_<timestamp>_<run_id>.json
```

## Tests

The test suite covers:

- chunking behavior
- chunk overlap
- schema validation
- manifest metadata ingestion
- retrieval recall metric
- answer citation helpers
- expected answer point matching
- config loading
- report exporting
- run comparison
- regression gate pass/fail behavior

Current local status:

```text
19 passed
```

## CI

GitHub Actions runs:

1. install dependencies with Poetry
2. run pytest
3. run the regression gate against fixture eval reports

The fixture reports live in:

- `tests/fixtures/eval_runs/baseline.json`
- `tests/fixtures/eval_runs/candidate_top5.json`

This means CI can test the regression mechanism without making OpenAI calls.

## Example Report

The checked-in example reports are:

```text
reports/examples/
examples/official_notes_top5_summary.md
```

These are sanitized and meant for review. Generated full local reports remain ignored by git under `reports/runs/` and `reports/summaries/`.

## Key Design Decisions

### Why CLI instead of web app?

Because the goal was to show evaluated RAG. A web app would add surface area without improving the core AI engineering signal.

### Why OpenAI SDK directly?

To keep the pipeline transparent. I wanted retrieval, prompting, evaluation, and cost tracking to be visible in the code.

### Why scikit-learn instead of a vector database?

For this local project, `NearestNeighbors` is enough. It avoids infrastructure while still demonstrating embeddings and semantic retrieval.

### Why JSON/JSONL and `.npy` files?

They are easy to inspect, easy to reproduce, and avoid introducing a database before the project needs one.

### Why LLM-as-judge?

Retrieval recall tells me whether I found expected evidence. It does not tell me whether the generated answer stayed grounded. The faithfulness judge adds an answer-quality layer.

### Why regression gates?

Because production systems need to know whether a change made quality worse. The regression gate turns eval metrics into a pass/fail decision.

## Important Results To Explain

The most important result is the top-3 vs top-5 comparison on the current 25-question official-source eval set.

Top-3 result:

- recall@k: `0.9067`
- faithfulness: `1.0`
- failed retrievals: `4`

Top-5 result:

- recall@k: `0.9733`
- faithfulness: `1.0`
- failed retrievals: `2`

Interpretation:

- top-5 improved recall but did not eliminate every retrieval miss
- answer faithfulness stayed high in these local runs
- estimated cost increased because more context was sent downstream

This is the main proof that the project evaluates tradeoffs instead of guessing.

## How To Explain The Pipeline In An Interview

I would explain it like this:

1. I start with local cloud/security markdown docs and source metadata.
2. I chunk the docs deterministically so changes are reproducible.
3. I embed chunks with OpenAI embeddings and save a local vector index.
4. For a question, I embed the query and retrieve top-k chunks with cosine similarity.
5. I build a prompt from those retrieved chunks and ask the generation model for a cited answer.
6. For evals, I compare retrieved document IDs against expected document IDs to compute recall@k.
7. I then run a faithfulness judge over the answer and retrieved evidence.
8. I save latency, estimated cost, retrieval metrics, answer metrics, and per-question details.
9. I can compare two runs and fail a regression gate if quality drops.

## Interview Talking Points

### If asked: “What makes this production-minded?”

The project includes repeatable evals, source metadata, structured schemas, local artifacts, experiment configs, report exports, CI, and regression gates. It is not just a demo chatbot.

### If asked: “How did you evaluate retrieval?”

Each eval question includes expected document IDs. After retrieval, I compare the retrieved doc IDs against the expected set and compute recall@k.

### If asked: “How did you evaluate groundedness?”

I generate an answer using retrieved chunks only, then use a judge prompt that returns structured JSON with a faithfulness score, unsupported claims, and rationale.

### If asked: “What did you learn from the experiment?”

The current 25-question eval showed that increasing retrieval depth from top-3 to top-5 improved recall@k from `0.9067` to `0.9733`, while preserving average faithfulness in these local runs and increasing estimated cost because more evidence was passed downstream.

### If asked: “What would you improve next?”

I would add more real official-source documents, harder eval questions, prompt and chunk-size experiments, and eventually a small dashboard after the CLI evaluation loop is mature.

### If asked: “Why not LangChain?”

I wanted to show the underlying mechanics directly: chunking, embedding, retrieval, prompt construction, evaluation, reporting, and regression gates. A framework could be added later, but it was not necessary for the core learning goal.

### If asked: “How do you prevent hallucinations?”

The answer prompt instructs the model to use only retrieved evidence and cite sources. Then the faithfulness judge evaluates whether the answer is supported by the retrieved chunks. The project records unsupported claims if the judge finds any.

### If asked: “How do you handle cost?”

The eval report includes estimated cost. It is approximate, but it makes tradeoffs visible when changing top-k, prompts, or model choices.

## Commands To Remember

Build official index:

```bash
python scripts/build_index.py --config configs/official_notes.json
```

Ask a question:

```bash
python scripts/ask.py "How can IAM least privilege and CloudTrail auditing work together to reduce cloud security risk?" --config configs/official_notes.json
```

Run eval:

```bash
python scripts/run_eval.py --config configs/official_notes.json
```

Run top-5 experiment:

```bash
python scripts/build_index.py --config configs/official_notes_top5.json
python scripts/run_eval.py --config configs/official_notes_top5.json
```

Compare runs:

```bash
python scripts/compare_runs.py reports/runs/baseline.json reports/runs/candidate.json
```

Check regression:

```bash
python scripts/check_regression.py reports/runs/baseline.json reports/runs/candidate.json
```

Export report:

```bash
python scripts/export_report.py reports/runs/run_official_notes_top5_<timestamp>_<run_id>.json
```

Run tests:

```bash
python -m pytest
```

## One-Minute Interview Version

I built a local RAG evaluation system for cloud security guidance. It ingests markdown docs, chunks them, embeds them with OpenAI, retrieves evidence with a local cosine-similarity index, and generates cited answers. The important part is the eval harness: each question has expected source documents, so I measure retrieval recall@k, then I judge whether the generated answer is faithful to retrieved evidence. I added experiment configs so I can compare top-k and other changes, report latency and estimated cost, export Markdown/CSV summaries, and run a regression gate in CI. On the current 25-question eval, top-5 retrieval improved recall over top-3 but still left two retrieval misses visible.
