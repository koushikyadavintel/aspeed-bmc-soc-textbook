# 2. Data Governance and Evaluation

## 2.1 Permissions travel with the document

Authentication identifies a caller. Authorization decides which content and actions that caller may access.

Document permissions must survive ingestion, chunking, indexing, retrieval, reranking, caching, chat history, and citations. A private document becomes a disclosure if any derived chunk escapes filtering.

Apply authorization before unauthorized content reaches the model. Filtering the final answer is too late if the model or logging pipeline already received restricted data.

Embeddings and metadata are derived enterprise data, not automatically public-safe artifacts.

## 2.2 Version, deletion, and freshness

Record a durable document ID and content version/hash. Reingestion should not leave duplicate stale chunks that outrank the current procedure.

Deletion must cover source objects, chunks, embeddings, metadata, caches, derived summaries, backups/retention policy, and applicable chat history. A UI "delete" button is not proof of end-to-end removal.

When two versions disagree, retrieval should expose version/applicability rather than blend incompatible procedures. A newer global manual can still be wrong for an older supported product.

## 2.3 Build an evaluation set

Use representative questions with expected sources, answer criteria, and authorization contexts.

Include:

- Exact-symbol questions.
- Multi-section explanations.
- Conflicting versions.
- Unsupported/absent answers requiring abstention.
- Unanswerable private-document questions from unauthorized users.
- Misleading retrieved instructions.
- Tables, OCR, and image-derived content.

Keep evaluation data public or appropriately private; do not upload confidential corpora to an unapproved evaluator.

## 2.4 Evaluate stages separately

| Stage | Example metric/question |
| --- | --- |
| Extraction | Were headings, units, tables, and negations preserved? |
| Retrieval | Recall@k for the required evidence |
| Ranking | Are the most applicable passages near the top? |
| Generation | Are claims entailed by supplied evidence? |
| Citation | Does each cited source actually support its claim? |
| Abstention | Does the system decline unsupported questions? |
| Authorization | Can any forbidden evidence reach the answer path? |
| Operations | Latency, throughput, failures, resource use |

For recall@k, define the relevant evidence set and denominator. For answer quality, use explicit rubrics and human checks; an LLM judge can be useful but is not an independent oracle.

## 2.5 A worked miniature evaluation

Suppose 20 questions each require one known source passage. Retrieval places the needed passage in the top five for 16 questions:

```text
single-required-passage recall@5 = 16 / 20 = 0.80
```

This does not mean 80% of answers are correct. The generator could misuse retrieved evidence, or the four missed questions could be answered by unsupported guessing.

Track a separate grounded-answer pass rate and an abstention result for the missed cases.

## 2.6 Threat boundaries

Prompt injection, malicious documents, unsafe tool calls, tenant crossover, and secret-bearing logs require application controls. Guardrails complement, not replace, authentication, authorization, input handling, and tool permission checks.

A self-hosted deployment can still send telemetry, model requests, or document data to external endpoints if configured that way. Inventory actual data flows before claiming that all information stays on premises.

## Exercise

An application retrieves the correct restricted passage, then hides it from the UI. Is access control satisfied?

**Answer:** no if the model, reranker, logs, or another unauthorized component already received it. Enforce the authorization boundary throughout the pipeline.

Next: [Intel project architecture](03_Intel_Project_Architecture_and_Deployment.md).
