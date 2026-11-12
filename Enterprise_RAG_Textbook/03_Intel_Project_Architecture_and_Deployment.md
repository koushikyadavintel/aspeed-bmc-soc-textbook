# 3. Intel's Public Project: Architecture and Deployment Context

## 3.1 Repository migration matters

The [OPEA repository](https://github.com/opea-project/Enterprise-RAG) states that 2.3.0 is its final release and directs new development to [intel/enterprise-rag](https://github.com/intel/enterprise-rag), starting with its 3.0.0 line.

Do not mix old commands, hardware profiles, storage assumptions, or pipeline limitations into a newer deployment merely because the project name remains similar.

The older conversation discussed Xeon and Gaudi configurations. Those statements belong to that older release context unless current documentation confirms them.

## 3.2 The current layered platform

The current public README describes Enterprise RAG as an application layer, not a standalone installer:

```text
infrastructure -> platform -> inference -> erag application
```

The platform supplies Kubernetes and shared services such as identity, gateway, storage, and observability. The inference layer supplies model serving. The RAG layer supplies document preparation, retrieval/vector databases, composed pipelines, chat history, and UI integration.

This split explains why running an old playbook from the new repository's directory can be wrong: the current documented commands run from the solutions-platform root.

## 3.3 Composition and reconciliation

The current architecture describes a component registry, Ansible roles, Helm charts, and pipeline flavours. A composer turns selected pipeline configuration into a `GMConnector` resource; the GMC operator reconciles the required services.

```text
chosen flavour/configuration
 -> rendered pipeline resource
 -> operator reconciliation
 -> microservices/dependencies
 -> ready application path
```

A Kubernetes resource existing does not prove every service is ready or that retrieval returns the intended evidence.

The public architecture lists conversational, summarization, audio, translation, and other configuration flavours. Treat available flavours and defaults as release-specific, not a permanent number.

## 3.4 Request path and shared services

A typical question crosses identity/gateway policy, a pipeline router, query embedding, retrieval, reranking, guardrail/prompt stages, and model serving before returning an answer.

Ingestion is a separate asynchronous path involving extraction, preparation, object storage, metadata, and index updates. A chat endpoint can be healthy while a newly uploaded document is still unsearchable.

Shared identity can use Keycloak; storage and databases serve different purposes for source documents, relational metadata, vectors, and history. Do not treat every database as an interchangeable cache.

Exact network policy, mTLS, secret generation, and document-role settings must be verified in the selected deployment. The phrase "secure by default" in a README is a claim to validate, not a substitute for an installation review.

## 3.5 Hardware and model choices

The current README emphasizes Xeon and platform-managed inference. Older Gaudi-oriented settings should not be carried forward without explicit support documentation.

For any release, confirm CPU features, RAM, storage, accelerator drivers/plugins if applicable, model license/access, image versions, and resource profiles. A large language model's weights, runtime buffers, KV cache, and concurrency can dominate memory.

A documented minimum is not a guarantee of required latency at your workload. Do not reuse old numerical requirements as timeless sizing rules.

## 3.6 Safe deployment sequence

1. Select a release/commit and matching platform documentation.
2. Verify hardware/software prerequisites.
3. Prepare approved DNS, certificates, identity, storage, secrets, and model access.
4. Deploy dependencies in documented order.
5. Validate readiness and a public test-document flow.
6. Test authorization, deletion, backup/restore, and failure handling.
7. Measure the intended workload before production approval.

This is a checklist, not an executable production installation. Installation scripts can require elevated privileges and significant resources; inspect their exact release behavior before running them.

Next: [Operations, TCO, and capstone](04_Operations_TCO_and_Capstone.md).
