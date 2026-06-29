# Eval Protocol

This document describes the checked-in evaluation setup and the limits of what the current numbers prove.

## Document sources

The repository contains two local document sets under `data/raw_docs/`:

- **Synthetic starter docs**: short, non-official sample notes used by the original starter eval (`data/eval_sets/cloudsec_eval_v1.jsonl`). These are useful for exercising the pipeline locally, but they should not be described as AWS, NIST, or production guidance.
- **Official-source notes**: concise local notes derived from public AWS IAM, AWS CloudTrail, and NIST SP 800-61 Rev. 3 sources. These notes include source URLs in `data/doc_manifest.json`, but they are not full copies of the upstream documentation.

The current credibility numbers in the README are based on the official-source-notes eval set, not the synthetic starter data.

## Chunking and retrieval setup

The official-source experiments use:

- Configs: `configs/official_notes.json` and `configs/official_notes_top5.json`
- Eval set: `data/eval_sets/cloudsec_official_notes_eval_v1.jsonl`
- Chunk size: `700`
- Chunk overlap: `100`
- Embedding model: `text-embedding-3-small`
- Generation model: `gpt-4.1-mini`

`official_notes` retrieves the top 3 chunks. `official_notes_top5` retrieves the top 5 chunks. The index is generated locally under `data/indexes/`, which is ignored by git.

Compare retrieval experiments only when the saved index and eval config describe the same source set, chunking settings, prompt paths, and eval set. If any of those inputs change, treat the result as a new experiment rather than attributing the delta only to top-k.

## Eval set design

The current official-source-notes eval set has 25 questions:

- single-source questions for IAM, CloudTrail, and NIST notes
- multi-source questions requiring evidence from more than one document
- ambiguous cloud security questions spanning prevention, detection, and response
- not-enough-information questions that should avoid unsupported specifics
- `avoided_doc_ids` cases that check whether unrelated documents were retrieved

Each JSONL row includes an `id`, `question`, `expected_doc_ids`, and `expected_answer_points`. Some rows also include `avoided_doc_ids`.

## Recall@k calculation

Recall@k is calculated per question from document IDs, not chunk IDs:

```text
matched expected_doc_ids / total expected_doc_ids
```

A question expecting one document scores `1.0` if that document appears in any retrieved chunk and `0.0` otherwise. A question expecting three documents scores `0.6667` when two of the three expected document IDs appear in the retrieved chunks. The run-level `retrieval_recall_at_k` is the average of per-question recall values.

`avoided_doc_ids` are reported separately as a retrieval-noise diagnostic. They do not change recall@k and are not part of the regression gate; they identify cases where retrieval pulled documents the eval author expected to be unrelated for that question.

## Faithfulness judging

For each question, the pipeline generates an answer from retrieved evidence and sends the question, answer, and evidence to the faithfulness judge prompt in `prompts/faithfulness_judge_v1.txt`. This is an LLM-as-judge score, so it should be read as a structured review signal rather than an authoritative ground-truth label.

The judge returns structured JSON with:

- `faithfulness_score` between `0.0` and `1.0`
- `is_faithful`
- `unsupported_claims`
- `rationale`

The reported `average_faithfulness_score` is the average judge score across questions. Citation presence and citation-number validity are checked separately in code. Expected answer points are checked with lightweight keyword overlap, so missing-point counts are a heuristic review aid rather than a semantic grading system.

## Latency and cost reporting

Latency and estimated cost are included to make experiment tradeoffs visible, not to claim production performance.

- `latency_ms` measures retrieval time for a question.
- `answer_latency_ms` measures answer generation plus faithfulness judging for a question.
- `average_latency_ms` averages those recorded phase timings across the run; it is not p95 latency and not a production service SLO.
- `estimated_cost_usd` is calculated from approximate token assumptions in `src/cloudsec_rag/metrics.py`; it is not provider billing data.

## Limitations of the 25-question eval

The current eval is a small local sanity check, not a broad benchmark:

- only three official-source note documents are represented
- the official-source notes are concise summaries, not full upstream docs
- the 25 questions were written for this repository and are not an external benchmark
- faithfulness is model-judged and can miss or overstate issues
- expected-answer-point matching is keyword based
- avoided-doc checks are diagnostic and do not replace a precision metric
- latency and estimated cost are local run observations, not stable performance claims or billing records
- higher top-k can improve recall while increasing prompt context and estimated cost

The checked-in example reports prove only that those specific local runs produced the recorded metrics with the checked-in config and eval set.

## Report review checklist

When reviewing a run, check recall misses before prompt wording: a faithful answer cannot cite evidence that retrieval failed to return. Then inspect unsupported claims, missing expected answer points, avoided-doc hits, and the estimated-cost delta for the selected top-k setting.

## Expanding the eval set

To expand coverage without weakening credibility:

1. Add or update source notes in `data/raw_docs/`.
2. Add matching metadata in `data/doc_manifest.json`, including `source_type`, `source_url`, and `is_official`.
3. Add eval rows to a new versioned JSONL file under `data/eval_sets/` rather than overwriting historical results.
4. Include a mix of single-source, multi-source, ambiguous, not-enough-information, and avoided-document questions.
5. Keep `expected_doc_ids` tied to document IDs from the manifest.
6. Use `expected_answer_points` for important answer content, but manually review misses because the checker is heuristic.
7. Run the baseline and candidate configs, export reports, and commit only sanitized examples that are supported by the generated local artifacts.
