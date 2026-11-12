# 4. Operations, TCO, and a Measurable Capstone

## 4.1 Observe the whole request

Measure ingestion delay, extraction errors, embedding time, retrieval latency, rerank time, model time to first token, generation throughput, end-to-end latency, and failure rate.

Correlate traces with bounded, privacy-aware identifiers. A trace should explain which stage was slow without retaining full confidential prompts by default.

Monitor resource saturation, queue depth, index availability, object storage, identity dependencies, model readiness, and certificate expiry. "All pods running" does not establish answer quality or recoverability.

## 4.2 Capacity and bottlenecks

At a basic steady-state level:

```text
average concurrent work ~= arrival rate * average time in system
```

This queueing relationship is not a sizing guarantee; bursts, tail latency, batching, admission control, and shared-resource contention matter.

Separate ingestion from interactive-query capacity when possible. A bulk re-embedding job can consume CPU/memory/storage bandwidth that the chat path needs.

More replicas do not improve a bottleneck in a single overloaded database or model server automatically. Autoscaling must target meaningful signals and respect stateful dependencies.

## 4.3 Total cost of ownership

TCO includes hardware amortization, power, cooling, network/storage, model-serving costs, licenses/support where applicable, operations, reliability, and engineering labor.

A useful comparison fixes quality and service objectives:

```text
cost per accepted grounded answer
 = attributable operating cost / answers meeting the evaluation criteria
```

Report corpus size, model, quantization, hardware, concurrency, context/output lengths, retrieval settings, quality thresholds, and latency targets. Without these, "cheaper per token" can hide worse answers or unacceptable wait times.

Intel hardware tuning can be valuable, but a repository or benchmark headline does not prove universal superiority over another CPU, accelerator, or cloud configuration.

## 4.4 Failure isolation

| Symptom | Candidate boundary |
| --- | --- |
| Upload accepted, no search result | Asynchronous ingestion/index completion |
| Relevant document not retrieved | Extraction, chunking, embedding mismatch, filter/ranking |
| Correct evidence, wrong answer | Prompt construction, context truncation, generation |
| Slow first token | Routing, retrieval/rerank, queueing, model prefill |
| Cross-user content | Authorization/filter/cache/history boundary |
| Source deleted, answer persists | Stale chunks/cache/derived state or retention behavior |

Each hypothesis should be tested with a known public fixture before exposing real enterprise data.

## 4.5 Capstone: a public-document assistant

Use a small collection of public manuals and original notes. Do not ingest internal firmware logs or private company documents.

1. Record document versions and licenses.
2. Define 20 questions with expected source passages.
3. Include at least four deliberately unanswerable questions.
4. Compare lexical, vector, and a chosen hybrid/rerank approach.
5. Measure retrieval recall, supported-answer rate, abstention, and latency.
6. Change a document version and test stale-result removal.
7. Use synthetic roles/documents to test authorization.
8. Record resource use and a workload-specific cost estimate.

**Success criteria:** every accepted answer cites applicable evidence; unsupported cases abstain under a stated rubric; forbidden fixture documents never enter the unauthorized model path; results are reproducible from recorded versions/settings.

**Answer guide:** inspect retrieval first when evidence is missing, generation when evidence is misused, and the data lifecycle when stale content persists. Do not solve every failure by selecting a larger LLM.

## Glossary

| Term | Meaning |
| --- | --- |
| RAG | Retrieval-Augmented Generation |
| Embedding | Model-produced vector representation |
| Reranker | Model/scorer reordering retrieval candidates |
| Grounded answer | Answer supported by the supplied applicable evidence |
| OIDC | OpenID Connect identity protocol |
| KV cache | Model attention state retained for token generation |
| TCO | Total cost of ownership |
| Recall@k | Fraction of required evidence retrieved within top k, under a defined metric |
| Flavour | Project-specific composed pipeline configuration |

Return to [contents](00_README.md) or the [library](../README.md).
