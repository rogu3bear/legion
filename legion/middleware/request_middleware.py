"""
Middleware for request processing, embedding validation, and directive compliance.
"""

from typing import Any, Dict, Optional, Tuple

from legion.core.utils.async_chroma_client import AsyncChromaClient

from .directive_compliance import DirectiveCompliance

# Threshold constants for embedding similarity validation
THERAPIST_AGENT_THRESHOLD = 0.70  # Similarity below 0.70 triggers therapist review
ACCEPTABLE_SIMILARITY = 0.85  # Similarity at or above 0.85 is acceptable
REVIEW_SIMILARITY = 0.60  # Similarity below 0.60 is rejected outright


class RequestMiddleware:
    def __init__(
        self, chroma_client: AsyncChromaClient, directive_checker: DirectiveCompliance
    ):
        self.chroma_client = chroma_client
        self.directive_checker = directive_checker

    def process_request(
        self, request_text: str, request_metadata: Dict[str, Any]
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Processes an incoming request, performs embedding validation and directive compliance.

        Returns a tuple: (status, details_dict)
        Status can be: "approved", "rejected", "needs_review", "escalated_therapist"
        """
        # 1. Input Validation
        if not request_text:
            return "rejected", {
                "reason": "Empty request text",
                "source": "input_validation",
            }

        # 2. Embedding Generation
        try:
            request_embedding = self.chroma_client.create_embedding(request_text)
        except Exception as e:
            # Log exception e
            return "rejected", {
                "reason": f"Failed to create embedding: {e}",
                "source": "embedding_system",
            }

        # 3. Embedding Retrieval & Initial Validation
        try:
            similar_embeddings = self.chroma_client.retrieve_similar_embeddings(
                query_embedding=request_embedding,
                top_k=1,  # Get the most similar for validation
            )
        except Exception as e:
            # Log exception e
            return "rejected", {
                "reason": f"Failed to retrieve similar embeddings: {e}",
                "source": "embedding_system",
            }

        # Initialize embedding-derived status and details
        embedding_derived_status = "approved"
        embedding_details: Dict[str, Any] = {}

        # Calculate embedding outcome based on top_similarity
        if not similar_embeddings:
            embedding_derived_status = "needs_review_embedding"
            embedding_details["reason"] = "No similar context found"
        else:
            top_similarity = similar_embeddings[0].get("similarity", 0.0)
            embedding_details["top_similarity"] = top_similarity

            # Apply threshold logic for embedding validation
            if top_similarity < REVIEW_SIMILARITY:
                # Immediate rejection for very low similarity
                return "rejected", {
                    "reason": f"Similarity {top_similarity:.2f} below rejection threshold {REVIEW_SIMILARITY}",
                    "source": "embedding_validation",
                    "similarity": top_similarity,
                }
            elif top_similarity < THERAPIST_AGENT_THRESHOLD:
                # Needs review for similarity between REVIEW_SIMILARITY and THERAPIST_AGENT_THRESHOLD
                embedding_derived_status = "needs_review_embedding"
                embedding_details["reason"] = (
                    f"Similarity {top_similarity:.2f} below therapist threshold {THERAPIST_AGENT_THRESHOLD}, needs review"
                )
            elif top_similarity < ACCEPTABLE_SIMILARITY:
                # Escalate to therapist for similarity between THERAPIST_AGENT_THRESHOLD and ACCEPTABLE_SIMILARITY
                embedding_derived_status = "escalate_therapist_embedding"
                embedding_details["reason"] = (
                    f"Similarity {top_similarity:.2f} below acceptable threshold {ACCEPTABLE_SIMILARITY}, escalating to therapist"
                )
                embedding_details["escalation_trigger"] = "low_semantic_similarity"
            else:
                # Approved for similarity at or above ACCEPTABLE_SIMILARITY
                embedding_derived_status = "approved_embedding"
                embedding_details["reason"] = (
                    f"Similarity {top_similarity:.2f} meets acceptable threshold {ACCEPTABLE_SIMILARITY}"
                )

        # 4. Directive Compliance Check
        agent_id = request_metadata.get("agent_id")
        directive_status, directive_details = self.directive_checker.check(
            request_text, request_metadata, agent_id=agent_id
        )

        # 5. Combine Outcomes & Final Decision
        final_status = embedding_derived_status
        final_details = embedding_details.copy()
        final_details["source"] = "embedding_validation"

        # 5.1 Directive Rejection Precedence
        if directive_status == "non_compliant":
            final_status = "rejected"
            final_details.update(directive_details)
            final_details["source"] = "directive_compliance"
            return final_status, final_details

        # 5.2 Therapist Escalation Precedence
        if directive_status == "therapist_triggered":
            final_status = "escalated_therapist"
            final_details.update(directive_details)
            final_details["source"] = "directive_compliance"
            return final_status, final_details
        elif embedding_derived_status == "escalate_therapist_embedding":
            final_status = "escalated_therapist"
            final_details["source"] = "embedding_validation"
            return final_status, final_details

        # 5.3 Needs Review (if applicable)
        if (
            embedding_derived_status == "needs_review_embedding"
            and directive_status == "compliant"
        ):
            final_status = "needs_review"
            final_details["source"] = "embedding_validation"
            return final_status, final_details

        # 5.4 Approval
        if (
            embedding_derived_status == "approved_embedding"
            and directive_status == "compliant"
        ):
            final_status = "approved"
            final_details.update(directive_details)
            final_details["source"] = "combined_approval"
            return final_status, final_details

        # Default fallback (should be caught by logic above, but just in case)
        # Retain the more severe status
        if directive_status != "compliant":
            final_status = "rejected"
            final_details.update(directive_details)
            final_details["source"] = "directive_compliance"

        return final_status, final_details


# Example usage (will be refined)
# if __name__ == '__main__':
#     # This setup is illustrative. ChromaClient would be configured and passed.
#     # DirectiveCompliance likewise.
#     client = ChromaClient(persist_directory=".test_chroma_mw")
#     # dummy_directive_checker = DirectiveCompliance() # Replace with actual
#     directive_checker_instance = DirectiveCompliance()
#     middleware = RequestMiddleware(chroma_client=client, directive_checker=directive_checker_instance)

#     test_req = "Tell me about quantum field theory."
#     status, details = middleware.process_request(test_req, {})
#     print(f"Request: '{test_req}' -> Status: {status}, Details: {details}")

#     # Example of storing an embedding to test against
#     emb_to_store = client.create_embedding("An inquiry about advanced physics topics.")
#     client.store_embedding("physics_query_1", emb_to_store, {"topic": "physics"})

#     status, details = middleware.process_request(test_req, {})
#     print(f"Request (after storing similar): '{test_req}' -> Status: {status}, Details: {details}")
