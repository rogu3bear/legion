# Therapist Agent Integration Plan

This document outlines the plan for integrating a "Therapist Agent" with the `RequestMiddleware`. The therapist agent is responsible for reviewing and potentially remediating requests flagged by the middleware due to semantic ambiguity or minor directive compliance issues.

## 1. Purpose of Therapist Agent Integration

- Provide a human-in-the-loop or advanced AI review for requests that are not clearly approvable or rejectable by automated checks.
- Offer a mechanism for nuanced decision-making, corrective actions, or gathering more context before a request proceeds to an orchestrator or is finally rejected.
- Reduce false positives from automated checks and improve overall system robustness.

## 2. Conditions Triggering Therapist Intervention

The `RequestMiddleware` will escalate a request to the Therapist Agent under the following conditions:

**From Embedding Validation:**
1.  **Low Semantic Similarity (but not rejectable outright):**
    *   If `top_similarity` of the request embedding (compared to relevant context in Chroma) falls within a specific range defined by `THERAPIST_AGENT_THRESHOLD` and `ACCEPTABLE_SIMILARITY`.
    *   Example: `0.70 <= top_similarity < 0.85` (as per current `RequestMiddleware` code).
    *   The `middleware_interaction_logic.md` refines this to: `0.60 <= top_similarity < 0.85` should trigger therapist if the lower end of this is not just "needs review". The key is that it's below fully acceptable but not an outright semantic mismatch.

**From Directive Compliance:**
2.  **Specific Keyword Triggers:**
    *   Detection of certain predefined keywords or patterns in the `request_text` that are deemed sensitive or indicative of potential misuse, but not severe enough for automatic rejection.
    *   Example: The `DirectiveCompliance` class currently has a placeholder: `if keyword in ["sudo rm -rf"]: status = "therapist_triggered"` (this example is actually for a *critical* keyword; true therapist triggers would be for less severe but still concerning patterns).
3.  **Partial Non-Compliance / Suspicious Patterns:**
    *   Minor directive breaches that don't warrant outright rejection but require further scrutiny.
    *   Example: A request that is slightly over a soft length limit, or uses an unusual combination of allowed parameters.
    *   The `DirectiveCompliance` class needs to be enhanced to define and detect these states, returning a specific `"therapist_triggered"` status.

## 3. Data Payload from Middleware to Therapist Agent

When a request is escalated, the `RequestMiddleware` (or an intermediary routing mechanism) will pass the following data payload to the Therapist Agent:

```json
{
  "request_id": "<unique_request_identifier>",
  "timestamp_mw_processed": "<iso_timestamp>",
  "original_request": {
    "text": "<full_request_text>",
    "metadata": {
      "agent_id": "<agent_identifier_if_available>",
      "user_id": "<user_identifier_if_available>",
      // ... other relevant original request metadata
    }
  },
  "middleware_assessment": {
    "triggering_condition": "<enum: low_semantic_similarity | directive_keyword_alert | directive_partial_noncompliance | other_reason>",
    "embedding_validation_details": {
      "top_similarity_score": "<float_or_null>",
      "similarity_threshold_acceptable": "<float>", // e.g., 0.85
      "similarity_threshold_therapist": "<float>", // e.g., 0.70
      "reasoning": "<textual_summary_from_embedding_check>"
    },
    "directive_compliance_details": {
      "checks_passed": ["<check_description>", ...],
      "checks_failed": [{"check": "<check_name>", "details": "<failure_details>"}, ...],
      "breach_type": "<string_summary_of_breaches>",
      "therapist_reason_directive": "<textual_summary_from_directive_check_if_applicable>"
    }
  },
  "suggested_actions_by_middleware": [
    // Optional: e.g., ["review_for_clarification", "check_user_history"]
  ],
  "escalation_context": {
    // Optional: e.g., relevant snippets from similar documents found by Chroma
    "similar_docs_preview": [
      {"id": "doc1", "snippet": "...", "similarity": 0.72},
      ...
    ]
  }
}
```

## 4. Expected Actions & Responses from Therapist Agent

The Therapist Agent is expected to process the payload and return a structured response to the middleware (or the calling system). The response should indicate a clear disposition for the original request.

**Possible Therapist Agent Actions:**
1.  **Approve Request:** The request is deemed safe/compliant after review.
    *   Optionally provide modified text or metadata if minor safe edits were made.
2.  **Reject Request:** The request is deemed unsafe/non-compliant after review.
3.  **Request Clarification / More Information:** (If interacting with a user directly or via another agent)
    *   Specify what information is needed.
4.  **Modify Request (and Approve):** Make safe modifications (e.g., remove a problematic keyword, rephrase) and then approve.
5.  **Log and Monitor:** Log the event for auditing and potentially flag the user/agent for future monitoring without rejecting this specific request.

**Therapist Agent Response Payload Structure:**

```json
{
  "request_id": "<original_request_identifier>",
  "therapist_agent_id": "<therapist_agent_instance_id>",
  "timestamp_therapist_processed": "<iso_timestamp>",
  "disposition": "<enum: approved | rejected | needs_clarification | modified_approved>",
  "remediation_details": {
    "original_request_text": "<if_modified_or_relevant>",
    "modified_request_text": "<text_or_null>",
    "modified_metadata": "<dict_or_null>",
    "reasoning": "<textual_summary_of_therapist_decision>",
    "confidence_score": "<float_optional_0.0_to_1.0>"
  },
  "follow_up_actions_recommended": [
    // Optional: e.g., ["log_for_audit", "notify_admin", "add_to_user_watch_list"]
  ]
}
```

## 5. Integration Points in Middleware

- The `RequestMiddleware.process_request()` method, when it determines a status of `"escalated_therapist"`, will be responsible for:
    1.  Constructing the payload as defined in Section 3.
    2.  Dispatching this payload to the Therapist Agent (e.g., via a message queue, direct API call, or by returning a specific status that an orchestrator interprets).
    3.  Potentially waiting for a response if the interaction is synchronous, or handling asynchronous callbacks/events if it's asynchronous.
- The exact mechanism for dispatch and response handling (sync/async) will depend on the overall system architecture and the Therapist Agent's design.

## 6. Future Considerations
-   **Learning Loop:** Can therapist decisions be used to fine-tune middleware thresholds or directive rules?
-   **Dynamic Loading of Therapist Triggers:** Allow new therapist triggers to be defined without code changes.
-   **Multi-level Therapists:** Different therapists for different types of issues.
