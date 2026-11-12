# 1. RAG Foundations and Retrieval

## 1.1 Why retrieve?

A language model can produce plausible text without knowing the current contents of your document collection. Retrieval-Augmented Generation supplies selected evidence at inference time.

```text
documents -> extraction -> chunks -> embeddings/index
question -> query embedding/search -> candidates -> reranker
 -> evidence + question + instructions -> generator -> answer/citations
```

RAG does not require fine-tuning the generator. It also does not guarantee truth: bad extraction, wrong retrieval, stale documents, or unsupported generation can still produce wrong answers.

## 1.2 Ingestion creates an information model

Document preparation should preserve title, source identity, version, section hierarchy, timestamps, permissions, and a linkable location. PDFs with tables and scanned pages can require layout-aware extraction or OCR.

Chunking trades context against retrieval precision. Very small chunks lose definitions; very large chunks dilute relevance and consume prompt budget. Overlap can preserve continuity but adds duplication.

For firmware documents, keeping a command with its prerequisites and warning is often more important than a universal fixed token count.

## 1.3 Embeddings and search

An embedding maps text into a vector space chosen by a model. Similarity can identify semantically related text, but it is not a truth or authorization score.

Document and query embeddings must be compatible. Changing the embedding model, normalization, or dimensionality usually requires a controlled index migration/rebuild.

Lexical search is useful for exact names, error strings, register symbols, and specification identifiers. Hybrid retrieval can combine lexical and vector candidates. Rerankers score candidates more carefully relative to the query, at additional cost.

Top-k retrieval must be tuned against relevant evidence coverage and context size, not maximized without limit.

## 1.4 Prompt construction

The prompt should distinguish trusted instructions from retrieved text. Evidence needs stable source identifiers so the output can cite actual passages.

Include only authorized, relevant context. Treat document text as data: an instruction embedded in a retrieved page should not become permission to run a command or reveal secrets.

A generator should abstain when evidence is insufficient or conflicting. Citations should support individual claims rather than merely decorate the last paragraph.

## 1.5 RAG versus summarization

Question answering retrieves evidence relevant to a question. Summarization compresses a specified document or set, sometimes through chunk summaries followed by aggregation.

Long-document summarization can lose cross-section constraints or overemphasize repeated text. It needs its own evaluation, not just the same top-k retrieval settings.

Conversational history is another input. It can help interpret follow-up questions, but must not silently override document evidence or leak another user's context.

## Worked example

Question: "Can this capsule be flashed directly?"

Relevant evidence includes target identity, package format, supported updater, authorization, and recovery instructions. A vector match to a generic sentence about firmware images is insufficient.

**Good answer:** explain what is known, cite the exact supported procedure, and decline to invent offsets or write commands when the target is unspecified.

## Review

Does a higher similarity score mean the answer is correct?

**Answer:** no. It estimates a model-specific relationship between text representations. Correctness also requires applicable sources, complete context, sound reasoning, and supported claims.

Next: [Data governance and evaluation](02_Data_Governance_and_Evaluation.md).
