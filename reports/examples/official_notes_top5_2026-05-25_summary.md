# RAG Evaluation Report: official_notes_top5

This is a sanitized checked-in example copied from a real local run:

```text
reports/runs/run_official_notes_top5_2026-05-25T22-27-41Z_2590bdc2-a9d8-4a25-bd6b-7ff3cec8bbd0.json
```

It is included to support the README metrics without committing generated answers.

## Summary

- Run ID: `2590bdc2-a9d8-4a25-bd6b-7ff3cec8bbd0`
- Timestamp: `2026-05-25T22:27:41Z`
- Experiment: `official_notes_top5`
- Top-k: `5`
- Source set: concise official-source notes for AWS IAM, AWS CloudTrail, and NIST SP 800-61 Rev. 3
- Eval set: `data/eval_sets/cloudsec_official_notes_eval_v1.jsonl`
- Questions: `25`
- Retrieval recall@k: `0.9733`
- Average faithfulness score: `1.0`
- Average latency: `2873.9 ms`
- Estimated cost: `$0.05144`
- Failed retrievals: `2`
- Missing expected answer points: `7`
- Avoided-doc checks passed: `2 / 3`

These metrics are a local sanity check over a small 25-question eval set, not a broad benchmark claim.

## Per-question retrieval misses

| ID | Expected docs found | Recall@k | Missing expected answer points |
| --- | ---: | ---: | --- |
| `official_q18` | 2 / 3 | `0.6667` | least privilege |
| `official_q19` | 2 / 3 | `0.6667` | none |

## Comparison context

Compared with the top-3 `official_notes` run, this top-5 run improved average recall@k from `0.9067` to `0.9733` and kept average faithfulness at `1.0`. It also increased estimated cost from `$0.036722` to `$0.05144` because more retrieved context was included.
