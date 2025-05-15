# Middleware Requirements Document

## 1. Overview
This document outlines the functional requirements for the Legion middleware component. It specifies embedding validation, context indexing via Chroma, and directive compliance mechanisms.

## 2. Embedding Validation
### 2.1 Purpose
Ensure that incoming agent requests semantically align with existing context and directives by comparing embeddings.
### 2.2 Functional Requirements
- Generate embeddings for each agent request using the configured embedding model.
- Retrieve relevant context embeddings from Chroma.
- Compute cosine similarity between request embeddings and stored embeddings.
- Compare similarity scores against predefined thresholds to accept or flag anomalies.
### 2.3 Thresholds
- similarity ≥ 0.85: Acceptable
- 0.60 ≤ similarity < 0.85: Requires manual review
- similarity < 0.60: Flag as anomaly
### 2.4 Error Handling
- Implement retries with exponential backoff on Chroma timeouts or transient errors.
- Fallback to an in-memory cache if Chroma is unavailable.

## 3. Context Indexing
### 3.1 Purpose
Provide rapid retrieval of semantically relevant context chunks to support agent validation and orchestration.
### 3.2 Functional Requirements
- Upsert and index context embeddings in Chroma with appropriate metadata.
- Support batch embedding creation and incremental updates.
- Implement efficient caching layer to minimize redundant calls.
### 3.3 API Endpoints
- init_client(config)
- upsert_embeddings(records: List[EmbeddingRecord])
- query_embeddings(query_emb: List[float], top_k: int) → List[ContextItem]

## 4. Directive Compliance
### 4.1 Purpose
Enforce that agent requests strictly adhere to predefined directives and policies.
### 4.2 Functional Requirements
- Load agent-specific directive definitions at runtime.
- Validate request payloads against directive rules (schemas, prohibited content, etc.).
- Integrate therapist agent oversight for dynamic directive overrides.
### 4.3 Logging
- Record all compliance failures with timestamps, agent IDs, and reason codes.
- Expose logs for audit and monitoring.

## 5. Interaction Protocol (Middleware ⇄ Chroma)
### 5.1 API Patterns
- connect(): Initialize or validate Chroma connection.
- add_embedding(id, embedding, metadata)
- query_embeddings(embedding, top_k)
- delete_embeddings(ids)
### 5.2 Error Handling
- Retry failed Chroma operations (max 3 attempts).
- On persistent failure, emit warning and fallback to cache or sandbox mode.

## 6. Security & Performance
- Encrypt embeddings at rest if required by policy.
- Monitor latency metrics; aim for ≤50ms per Chroma call.
- Enforce rate limits to protect Chroma service.

## 7. Acceptance Criteria
- All embedding validation, indexing, and compliance functions implemented with unit and integration tests.
- End-to-end demonstration of middleware integrating with Chroma and directive validation.
