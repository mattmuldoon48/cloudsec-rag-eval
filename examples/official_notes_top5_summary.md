# Example RAG Evaluation Report: official_notes_top5

This is a legacy-location copy of the sanitized Markdown report example now documented under `reports/examples/`.

It shows the report shape produced by:

```bash
python scripts/export_report.py reports/runs/run_official_notes_top5_<timestamp>_<run_id>.json
```

It is included so reviewers can see the report shape without running OpenAI calls locally.

## Summary

- Experiment: `official_notes_top5`
- Run basis: 25-question eval run from `2026-05-25`
- Source set: concise official-source notes for AWS IAM, AWS CloudTrail, and NIST SP 800-61 Rev. 3
- Eval set: `data/eval_sets/cloudsec_official_notes_eval_v1.jsonl`
- Questions: `25`
- Retrieval recall@k: `0.9733`
- Average faithfulness score: `1.0`
- Average latency: `2873.9 ms`
- Estimated cost: `$0.05144`
- Failed retrievals: `2`
- Missing expected answer points: `7`

These metrics come from the small 25-question official-source-notes eval set and should be read as a local sanity check, not a broad benchmark claim.

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
| `official_q2` | AWS IAM | `1.0` | `1.0` | yes | roles for workloads |
| `official_q3` | AWS CloudTrail | `1.0` | `1.0` | yes | none |
| `official_q4` | AWS CloudTrail | `1.0` | `1.0` | yes | none |
| `official_q5` | NIST SP 800-61 Rev. 3 | `1.0` | `1.0` | yes | none |
| `official_q6` | NIST SP 800-61 Rev. 3 | `1.0` | `1.0` | yes | none |
| `official_q7` | AWS IAM + AWS CloudTrail | `1.0` | `1.0` | yes | none |
| `official_q8` | AWS CloudTrail + NIST SP 800-61 Rev. 3 | `1.0` | `1.0` | yes | none |
| `official_q9` | AWS IAM | `1.0` | `1.0` | yes | none |
| `official_q10` | AWS IAM | `1.0` | `1.0` | yes | none |
| `official_q11` | AWS CloudTrail | `1.0` | `1.0` | yes | none |
| `official_q12` | AWS CloudTrail | `1.0` | `1.0` | yes | none |
| `official_q13` | NIST SP 800-61 Rev. 3 | `1.0` | `1.0` | yes | none |
| `official_q14` | NIST SP 800-61 Rev. 3 | `1.0` | `1.0` | yes | none |
| `official_q15` | AWS IAM + AWS CloudTrail | `1.0` | `1.0` | yes | none |
| `official_q16` | AWS CloudTrail + NIST SP 800-61 Rev. 3 | `1.0` | `1.0` | yes | none |
| `official_q17` | AWS IAM + NIST SP 800-61 Rev. 3 | `1.0` | `1.0` | yes | none |
| `official_q18` | Ambiguous prevention/detection/response | `0.6667` | `1.0` | yes | least privilege |
| `official_q19` | Unexpected IAM policy change response | `0.6667` | `1.0` | yes | none |
| `official_q20` | Not enough information: exact key-rotation days | `1.0` | `1.0` | yes | rotate or update when needed; remove inactive keys |
| `official_q21` | Not enough information: required SIEM product | `1.0` | `1.0` | yes | logs should be queryable or searchable |
| `official_q22` | Not enough information: 24-hour regulatory deadline | `1.0` | `1.0` | yes | not enough information for a 24 hour regulatory deadline; coordination mechanisms |
| `official_q23` | Avoid unrelated NIST retrieval for IAM credential risk | `1.0` | `1.0` | yes | none |
| `official_q24` | Avoid unrelated IAM/NIST retrieval for CloudTrail API records | `1.0` | `1.0` | yes | none |
| `official_q25` | Avoid unrelated IAM/CloudTrail retrieval for NIST coordination | `1.0` | `1.0` | yes | none |

## Comparison Context

The `official_notes_top5` run was compared against the `official_notes` top-3 baseline.

| Experiment | Top-k | Recall@k | Faithfulness | Avg latency ms | Est. cost USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| `official_notes` | `3` | `0.9067` | `1.0` | `3401.76` | `$0.036722` |
| `official_notes_top5` | `5` | `0.9733` | `1.0` | `2873.9` | `$0.05144` |

Observed result: top-5 improved recall on the harder 25-question eval set and passed the regression gate, but it still missed expected sources on two questions. Estimated cost increased because more retrieved evidence was included.
