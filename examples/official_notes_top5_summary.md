# Example RAG Evaluation Report: official_notes_top5

This is a sanitized checked-in example of the Markdown report produced by:

```bash
python scripts/export_report.py reports/runs/run_official_notes_top5_<timestamp>_<run_id>.json
```

It is included so reviewers can see the report shape without running OpenAI calls locally.

## Summary

- Experiment: `official_notes_top5`
- Source set: concise official-source notes for AWS IAM, AWS CloudTrail, and NIST SP 800-61 Rev. 3
- Eval set: `data/eval_sets/cloudsec_official_notes_eval_v1.jsonl`
- Questions: `8`
- Retrieval recall@k: `1.0`
- Average faithfulness score: `1.0`
- Average latency: `2200.65 ms`
- Estimated cost: `$0.017195`
- Failed retrievals: `0`
- Missing expected answer points: `0`

These metrics come from a small starter eval set and should be read as a local sanity check, not a broad benchmark claim.

## Configuration

- Top-k: `5`
- Chunk size: `700`
- Chunk overlap: `100`
- Embedding model: `text-embedding-3-small`
- Generation model: `gpt-4.1-mini`

## Per-Question Results

| ID | Retrieval Target | Recall@k | Faithfulness | Citations | Missing Points |
| --- | --- | ---: | ---: | --- | --- |
| `official_q1` | AWS IAM | `1.0` | `1.0` | yes | none |
| `official_q2` | AWS IAM | `1.0` | `1.0` | yes | none |
| `official_q3` | AWS CloudTrail | `1.0` | `1.0` | yes | none |
| `official_q4` | AWS CloudTrail | `1.0` | `1.0` | yes | none |
| `official_q5` | NIST SP 800-61 Rev. 3 | `1.0` | `1.0` | yes | none |
| `official_q6` | NIST SP 800-61 Rev. 3 | `1.0` | `1.0` | yes | none |
| `official_q7` | AWS IAM + AWS CloudTrail | `1.0` | `1.0` | yes | none |
| `official_q8` | AWS CloudTrail + NIST SP 800-61 Rev. 3 | `1.0` | `1.0` | yes | none |

## Comparison Context

The `official_notes_top5` run was compared against the `official_notes` top-3 baseline.

| Experiment | Top-k | Recall@k | Faithfulness | Avg latency ms | Est. cost USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| `official_notes` | `3` | `0.9375` | `1.0` | `3136.98` | `$0.012721` |
| `official_notes_top5` | `5` | `1.0` | `1.0` | `2200.65` | `$0.017195` |

Observed result: top-5 recovered the missing expected source for a harder multi-document question and passed the regression gate. Estimated cost increased because more retrieved evidence was included.
