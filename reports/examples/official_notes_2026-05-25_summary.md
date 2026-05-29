# RAG Evaluation Report: official_notes

This is a sanitized checked-in example copied from a real local run:

```text
reports/runs/run_official_notes_2026-05-25T22-25-06Z_efcf79b0-4b44-4a71-a48b-342aa8e000c3.json
```

It is included to support the README metrics without committing generated answers.

## Summary

- Run ID: `efcf79b0-4b44-4a71-a48b-342aa8e000c3`
- Timestamp: `2026-05-25T22:25:06Z`
- Experiment: `official_notes`
- Top-k: `3`
- Source set: concise official-source notes for AWS IAM, AWS CloudTrail, and NIST SP 800-61 Rev. 3
- Eval set: `data/eval_sets/cloudsec_official_notes_eval_v1.jsonl`
- Questions: `25`
- Retrieval recall@k: `0.9067`
- Average faithfulness score: `1.0`
- Average latency: `3401.76 ms`
- Estimated cost: `$0.036722`
- Failed retrievals: `4`
- Missing expected answer points: `10`
- Avoided-doc checks passed: `3 / 3`

These metrics are a local sanity check over a small 25-question eval set, not a broad benchmark claim.

## Per-question retrieval misses

| ID | Expected docs found | Recall@k | Missing expected answer points |
| --- | ---: | ---: | --- |
| `official_q8` | 1 / 2 | `0.5` | none |
| `official_q17` | 1 / 2 | `0.5` | none |
| `official_q18` | 1 / 3 | `0.3333` | least privilege; CloudTrail auditing |
| `official_q19` | 1 / 3 | `0.3333` | who made an API call |
