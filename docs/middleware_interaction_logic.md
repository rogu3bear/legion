# Middleware Interaction Logic

This document outlines the refined interaction logic and precedence for combining embedding validation and directive compliance outcomes within the `RequestMiddleware`.

## 1. Core Principles

- **Early Rejection:** Critical failures in embedding or severe breaches in directives should lead to immediate rejection.
- **Therapist Escalation:** Semantic ambiguity or specific directive triggers should escalate to a therapist agent.
- **Clear Source Tracking:** The final decision payload should indicate whether embedding validation or directive compliance was the primary source of the status.

## 2. Thresholds & Statuses

### 2.1. Embedding Validation Statuses & Thresholds:
- `ACCEPTABLE_SIMILARITY = 0.85`
- `THERAPIST_AGENT_THRESHOLD = 0.70`
- `REVIEW_SIMILARITY = 0.60` (Rejection threshold for similarity)

- **Possible Outcomes from Embedding Check:**
    - `approved_embedding`: Similarity ≥ `ACCEPTABLE_SIMILARITY`
    - `escalate_therapist_embedding`: `THERAPIST_AGENT_THRESHOLD` ≤ Similarity < `ACCEPTABLE_SIMILARITY`
    - `needs_review_embedding`: `REVIEW_SIMILARITY` ≤ Similarity < `THERAPIST_AGENT_THRESHOLD` (Note: This state is effectively overridden if `THERAPIST_AGENT_THRESHOLD` is higher, as per current code. If `THERAPIST_AGENT_THRESHOLD` is *lower* than `REVIEW_SIMILARITY` for some reason, this band would exist distinctly).
        - *Clarification based on current code logic:* If `THERAPIST_AGENT_THRESHOLD` (0.70) is used as a primary escalation point, then any similarity < 0.70 (and >= 0.60) would trigger `escalated_therapist` before `needs_review` if `needs_review` is for scores like 0.70-0.84.
        - *Proposed Refined Embedding Outcomes based on code and user spec:*
            - Similarity ≥ 0.85: `approved_embedding`
            - 0.70 ≤ Similarity < 0.85: `escalate_therapist_embedding` (as per user spec "Slightly below threshold: Therapist oversight")
            - 0.60 ≤ Similarity < 0.70: `needs_review_embedding` (This fills the gap and aligns with "Far below threshold: Reject" being < 0.60)
            - Similarity < 0.60: `rejected_embedding`
- **System Failures:**
    - `rejected_system_error_embedding`: Failure to create or retrieve embeddings.
    - `rejected_empty_input`: Empty request text.

### 2.2. Directive Compliance Statuses:
- `compliant_directive`: All directive checks passed.
- `escalate_therapist_directive`: Specific directive rules trigger therapist oversight (e.g., critical keyword).
- `non_compliant_directive_reject`: Severe directive breach leads to rejection (e.g., prohibited action).
- `non_compliant_directive_review`: Minor directive breach that might need review but not outright rejection or therapist (Optional, could also fall under therapist).

## 3. Combined Logic Flow & Precedence

The `process_request` method in `RequestMiddleware` will follow this sequence:

1.  **Input Validation:**
    *   If `request_text` is empty:
        *   Return: `status="rejected"`, `details={"reason": "Empty request text", "source": "input_validation"}`

2.  **Embedding Generation:**
    *   Attempt to create embedding for `request_text`.
    *   If `chroma_client.create_embedding()` fails:
        *   Return: `status="rejected"`, `details={"reason": "Failed to create embedding: <error>", "source": "embedding_system"}`

3.  **Embedding Retrieval & Initial Validation:**
    *   Attempt to retrieve similar embeddings using `chroma_client.retrieve_similar_embeddings()`.
    *   If retrieval fails:
        *   Return: `status="rejected"`, `details={"reason": "Failed to retrieve similar embeddings: <error>", "source": "embedding_system"}`
    *   **Calculate Embedding Outcome based on `top_similarity`:**
        *   If no similar embeddings found: `current_embedding_status="needs_review_embedding"`, `embedding_details={"reason": "No similar context"}`
        *   Else if `top_similarity < REVIEW_SIMILARITY` (e.g., < 0.60):
            *   Return: `status="rejected"`, `details={"reason": "Similarity <_REJECTION_THRESHOLD>", "source": "embedding_validation", "similarity": top_similarity}`
        *   Else if `top_similarity < THERAPIST_AGENT_THRESHOLD` (e.g., < 0.70): `current_embedding_status="escalate_therapist_embedding"`
        *   Else if `top_similarity < ACCEPTABLE_SIMILARITY` (e.g., < 0.85): `current_embedding_status="needs_review_embedding"` (Adjusted based on user spec for therapist oversight for "slightly below")
            *   *Self-correction based on user request "Slightly below threshold: Therapist oversight" (for embedding):*
                If `ACCEPTABLE_SIMILARITY` is 0.85 and `THERAPIST_AGENT_THRESHOLD` is 0.70.
                - < 0.60 -> `rejected_embedding`
                - 0.60 to 0.69 -> `needs_review_embedding` (No, this should be therapist if "slightly below" means up to acceptable)
                - User: "Slightly below threshold [ACCEPTABLE_SIMILARITY]: **Therapist oversight**" implies range like 0.70-0.84 (assuming THERAPIST_AGENT_THRESHOLD marks this band's lower limit).
                - User: "Far below threshold: **Reject**" implies < 0.60 (REVIEW_SIMILARITY).
                - *Revised logic for embedding outcome determination:*
                    - If `top_similarity < REVIEW_SIMILARITY` (0.60): `final_status="rejected"`, `source="embedding_validation"`. **Return immediately.**
                    - Else if `top_similarity < ACCEPTABLE_SIMILARITY` (0.85): Set `embedding_derived_status="escalate_therapist_embedding"`. (This covers the "slightly below" case for therapist oversight directly from embedding).
                    - Else (`top_similarity >= ACCEPTABLE_SIMILARITY`): Set `embedding_derived_status="approved_embedding"`.
        *   Store `embedding_details` including similarity score and reason.

4.  **Directive Compliance Check:**
    *   Call `directive_checker.check(request_text, request_metadata, agent_id)`.
    *   Let `directive_status` and `directive_details` be the result.

5.  **Combine Outcomes & Final Decision:**
    *   Initialize `final_status = embedding_derived_status` and `final_details = embedding_details`.
    *   **Directive Rejection Precedence:**
        *   If `directive_status == "non_compliant_directive_reject"` (or a generic "non_compliant" that implies rejection):
            *   `final_status = "rejected"`
            *   `final_details.update(directive_details)`
            *   `final_details["source"] = "directive_compliance"`
            *   Return `(final_status, final_details)`
    *   **Therapist Escalation Precedence:**
        *   If `directive_status == "escalate_therapist_directive"`:
            *   `final_status = "escalated_therapist"`
            *   `final_details.update(directive_details)`
            *   `final_details["source"] = "directive_compliance"`
            *   Return `(final_status, final_details)`
        *   Else if `embedding_derived_status == "escalate_therapist_embedding"` (and directive didn't reject/escalate already):
            *   `final_status = "escalated_therapist"`
            *   `final_details["source"] = "embedding_validation"` (already set, or ensure it reflects primary trigger)
            *   Return `(final_status, final_details)`
    *   **Needs Review (if applicable):**
        *   The `needs_review_embedding` state from embedding outcome. If directives are compliant, this status would persist.
        *   If `embedding_derived_status == "needs_review_embedding"` and `directive_status == "compliant_directive"`:
            *   `final_status = "needs_review"`
            *    `final_details["source"] = "embedding_validation"`
            *   Return `(final_status, final_details)`
    *   **Approval:**
        *   If `embedding_derived_status == "approved_embedding"` AND `directive_status == "compliant_directive"`:
            *   `final_status = "approved"`
            *   `final_details.update(directive_details)`
            *   `final_details["source"] = "combined_approval"` (or keep as embedding/directive if one was borderline)
            *   Return `(final_status, final_details)`
    *   **Default/Fallback (should be covered by above logic):** If any combination is not explicitly handled, the more severe or cautious status should prevail. The `RequestMiddleware` code needs to be updated to reflect this new detailed flow.

## 4. Logging and Metrics
- Each step (embedding generation, retrieval, validation, directive check) should be logged with relevant details.
- The final decision (`status`, `source`, key `details`) must be logged clearly.
- Metrics should track counts for each final status and source.
