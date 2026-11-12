# Enterprise RAG: From Documents to Governed Answers

This volume follows the actual chat about the public Intel/OPEA Enterprise RAG project, but separates durable RAG concepts from release-specific deployment details.

| Chapter | Focus |
| --- | --- |
| [1. RAG foundations](01_RAG_Foundations_and_Retrieval.md) | Ingestion, embeddings, retrieval, reranking, prompting |
| [2. Data and evaluation](02_Data_Governance_and_Evaluation.md) | Versioning, permissions, citations, deletion, quality metrics |
| [3. Intel project architecture](03_Intel_Project_Architecture_and_Deployment.md) | Repository migration, layers, pipelines, hardware assumptions |
| [4. Operations and capstone](04_Operations_TCO_and_Capstone.md) | Observability, capacity, TCO, failure analysis, glossary |

**Prerequisites:** basic HTTP, services, storage, and containers. Kubernetes knowledge is needed for operating the referenced platform, not for understanding Chapter 1.

Sources: [legacy OPEA repository](https://github.com/opea-project/Enterprise-RAG), [current Intel repository](https://github.com/intel/enterprise-rag), [current architecture](https://github.com/intel/enterprise-rag/blob/main/docs/reference/architecture.md), [solutions platform](https://github.com/intel/enterprise-ai-solutions).

Only public project material is used. The text does not describe any employer's private RAG deployment or upload internal documents to external services.
