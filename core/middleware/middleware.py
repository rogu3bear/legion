"""
Middleware for request processing, embedding validation, and directive compliance.
"""
from typing import Any, Dict, Tuple, Optional
from core.utils.chroma_client import ChromaClient
from core.middleware.directive_compliance import DirectiveCompliance

# Placeholder for actual therapist agent integration
THERAPIST_AGENT_THRESHOLD = 0.70 # Example: similarity < 0.70 might trigger therapist
ACCEPTABLE_SIMILARITY = 0.85
REVIEW_SIMILARITY = 0.60

class RequestMiddleware:
    def __init__(self, chroma_client: ChromaClient, directive_checker: DirectiveCompliance):
        self.chroma_client = chroma_client
        self.directive_checker = directive_checker

    def process_request(self, request_text: str, request_metadata: Dict[str, Any]) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Processes an incoming request, performs embedding validation and directive compliance.

        Returns a tuple: (status, details_dict)
        Status can be: "approved", "rejected", "needs_review", "escalated_therapist"
        """
        # 1. Embedding Validation
        if not request_text:
            return "rejected", {"reason": "Empty request text", "source": "embedding_validation"}

        try:
            request_embedding = self.chroma_client.create_embedding(request_text)
        except Exception as e:
            # Log exception e
            return "rejected", {"reason": f"Failed to create embedding: {e}", "source": "embedding_validation"}

        # Retrieve relevant embeddings. For validation, we might want a small number of very similar items.
        # The exact query for validation (e.g. against what collection/subset) needs definition.
        # For now, let's assume we query a general collection.
        try:
            similar_embeddings = self.chroma_client.retrieve_similar_embeddings(
                query_embedding=request_embedding,
                top_k=1 # Get the most similar for validation
            )
        except Exception as e:
            # Log exception e
            return "rejected", {"reason": f"Failed to retrieve similar embeddings: {e}", "source": "embedding_validation"}

        validation_status = "approved"
        validation_details: Dict[str, Any] = {}

        if not similar_embeddings:
            validation_status = "needs_review" # Or perhaps a specific policy for no similar context
            validation_details["embedding_reason"] = "No similar context found."
        else:
            top_similarity = similar_embeddings[0].get("similarity", 0.0)
            validation_details["top_similarity"] = top_similarity

            if top_similarity < REVIEW_SIMILARITY:
                validation_status = "rejected"
                validation_details["embedding_reason"] = f"Similarity {top_similarity:.2f} below rejection threshold {REVIEW_SIMILARITY}"
            elif top_similarity < ACCEPTABLE_SIMILARITY:
                validation_status = "needs_review"
                validation_details["embedding_reason"] = f"Similarity {top_similarity:.2f} below acceptable threshold {ACCEPTABLE_SIMILARITY}, needs review."
            
            if top_similarity < THERAPIST_AGENT_THRESHOLD and validation_status != "rejected":
                # This logic might need refinement: should it override 'needs_review'?
                # For now, if not outright rejected but below therapist, it's escalated.
                validation_status = "escalated_therapist"
                validation_details["embedding_reason"] = f"Similarity {top_similarity:.2f} below therapist threshold {THERAPIST_AGENT_THRESHOLD}. Escalating."
                validation_details["escalation_trigger"] = "low_semantic_similarity"

        # 2. Directive Compliance (if embedding validation didn't reject)
        final_status = validation_status
        final_details = validation_details
        final_details["source"] = "embedding_validation"

        # Only run directive checks if embedding validation didn't lead to outright rejection or therapist escalation based on similarity alone.
        # The policy here might be: if embedding is poor, don't even bother with directive checks, or
        # always run directive checks unless embedding creation itself failed.
        # Current: Run if not "rejected" by embedding similarity directly.
        if final_status not in ["rejected"]:
            agent_id = request_metadata.get("agent_id") # Assuming agent_id is in metadata
            compliance_status, compliance_details = self.directive_checker.check(request_text, request_metadata, agent_id=agent_id)

            # Combine results: If either is non-compliant, overall is non-compliant.
            # Therapist trigger from either takes precedence.
            if compliance_status == "therapist_triggered":
                final_status = "therapist_triggered"
                final_details.update(compliance_details)
                final_details["source"] = "directive_compliance"
            elif compliance_status == "non_compliant":
                if final_status == "approved" or final_status == "needs_review": # Directive non-compliance overrides weaker embedding statuses
                    final_status = "non_compliant"
                final_details.update(compliance_details) # Merge details
                final_details["source"] = "directive_compliance"
            elif final_status == "approved" and compliance_status == "compliant":
                final_status = "approved" # Both are good
                final_details.update(compliance_details) # Add compliance check details
            # If embedding was 'needs_review' or 'escalated_therapist' and compliance is 'compliant', retain the stronger embedding status.
            # This part of the logic might need further refinement based on desired precedence.

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