# Interview Notes: cloudsec-rag-eval

## What I Built

I built a local Python CLI project for evaluating RAG over cloud security guidance. It ingests markdown docs, chunks them, embeds them with OpenAI, retrieves relevant chunks using a local vector index, generates cited answers, and evaluates both retrieval quality and answer faithfulness.

The project includes:

- document ingestion and source metadata
- deterministic chunking
- OpenAI embeddings and generation
- local cosine-similarity retrieval with scikit-learn
- cited answer generation
- retrieval recall@k evaluation
- LLM-as-judge faithfulness evaluation
- 25-question eval set
- multi-document eval questions
- ambiguous and not-enough-information questions
- avoided-doc checks for unrelated retrieval
- experiment configs
- report exports
- regression gates
- CI tests

## Why I Built It This Way

I intentionally kept this as a local CLI project instead of adding FastAPI, React, Docker, auth, or deployment. The purpose was to demonstrate the core AI engineering loop behind production RAG, not to build another chat UI.

The important production questions are:

- Did retrieval find the right evidence?
- Did the answer stay grounded in that evidence?
- Did a retrieval or prompt change improve quality?
- Did latency or estimated cost change?
- Can regressions be caught automatically?

I used the OpenAI SDK directly instead of LangChain so the pipeline mechanics are visible: chunking, embedding, retrieval, prompt construction, judging, metrics, and reports.

## Main Results

The official-source eval set now has 25 questions covering single-source, multi-source, ambiguous, not-enough-information, IAM-plus-CloudTrail, and avoided-doc retrieval cases.

The current checked-in comparison is top-3 vs top-5 retrieval on the same 25 questions:

- top-3 retrieval averaged `0.9067` recall@k with four retrieval misses
- top-5 retrieval averaged `0.9733` recall@k with two retrieval misses
- faithfulness stayed at `1.0` in both local runs
- estimated cost increased because more context was passed downstream

That is the core proof point: the project does not just generate answers, it measures retrieval tradeoffs and keeps the remaining misses visible.

## Biggest Weakness

The current corpus is still small. The official-source docs are concise local notes derived from AWS and NIST sources, not a large real documentation corpus.

The faithfulness judge is also model-based, so it is useful but not perfect. It should be treated as one signal, not absolute truth.

The cost estimate is approximate, and latency varies between runs. The README correctly avoids making broad benchmark claims.

## What I Would Improve Next

I would improve it by:

- adding more official-source documents
- adding harder adversarial eval questions
- expanding beyond the current 25-question eval and updating the public results table from checked-in artifacts
- adding chunk-size and prompt-variant experiments
- adding a small dashboard only after the CLI eval loop is mature
- improving expected-answer-point matching with a more robust semantic check
- adding separate retrieval-only eval mode for cheaper frequent testing

## What I Learned

I learned that RAG quality is mostly about the evaluation loop, not the chat interface.

The most useful part was seeing how changing `top_k` affects retrieval recall, cost, and answer context. Multi-document questions are especially valuable because they expose retrieval weaknesses that simple single-doc questions hide.

I also learned that a good RAG project needs source provenance, structured reports, regression checks, and honest caveats. Those pieces make the system easier to trust and easier to explain in an interview.

## One-Minute Explanation

I built a local RAG evaluation system for cloud security guidance. It ingests docs, chunks and embeds them, retrieves evidence with a local vector index, and generates cited answers. The main focus is evaluation: I measure retrieval recall@k against expected source documents, judge whether answers are faithful to retrieved evidence, track cost and latency, export reports, and use regression gates to catch quality drops. I expanded the eval set to 25 questions, including multi-source and not-enough-information cases, so the project tests the system rather than just demoing it.
