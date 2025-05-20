# Initializes the middleware package
"""High level middleware pipeline for directive and hallucination checks.

The functions in this module orchestrate the individual middleware
components documented in ``docs/middleware.md``. ``run_middleware_pipeline``
is intended to be called by the orchestrator before a request reaches the
Therapist agent.
"""

import logging

from legion.agents.therapist.validation import therapist_validate
from legion.utils.agent_feed import post_agent_feed

from .hallucination_guard import guard_response
from .validator import validate_directive

logger = logging.getLogger(__name__)


def run_middleware_pipeline(
    request_payload: dict, confidence_threshold: float = 0.75
) -> dict:
    """Run directive and hallucination checks before invoking the Therapist.

    Parameters
    ----------
    request_payload:
        Payload from the agent containing at least ``agent`` and ``directive``.
    confidence_threshold:
        Minimum confidence score accepted by ``guard_response``.

    Returns
    -------
    dict
        Dictionary with ``final_valid`` and ``source`` keys describing the
        overall decision. Additional details may be included by the Therapist
        agent.
    """
    # Step 1: Initial directive validation (e.g., using validator.py)
    # The 'request_payload' should contain 'agent' and 'directive'
    logger.info("Starting middleware pipeline", extra={"payload_agent": request_payload.get("agent")})
    directive_validation_result = validate_directive(request_payload)
    logger.info(
        "Directive validation result", extra={"result": directive_validation_result}
    )
    if not directive_validation_result.get("is_valid", False):
        post_agent_feed("Directive validation failed")
        return {
            "final_valid": False,
            "reason": directive_validation_result.get(
                "reason", "Directive validation failed"
            ),
            "source": "validator",
        }

    # Step 2: Hallucination check (e.g., using hallucination_guard.py)
    # The 'request_payload' must also contain 'confidence' for this step.
    # If it's an agent *request*, confidence might not be present yet.
    # The example shows therapist receiving confidence, implying it's available *before* therapist.
    # Let's assume 'request_payload' contains 'confidence'.
    # If not, this step might need to be conditional or adapt.

    initial_confidence = request_payload.get("confidence")
    if initial_confidence is None:
        # If confidence isn't part of the initial agent request,
        # this step might be more applicable to agent *responses*.
        # For now, if no confidence, we can't run hallucination guard or therapist effectively based on it.
        # However, the therapist example *requires* confidence.
        # Let's assume for a request flow, confidence is provided or defaulted.
        # For this example, we'll pass a default if not present to allow therapist to run.
        # In a real system, this would need careful consideration.
        logger.warning(
            "Confidence missing in payload; defaulting to 0.0"
        )
        post_agent_feed("middleware missing confidence")
        initial_confidence = 0.0

    # Hallucination guard expects a 'response' like structure with 'confidence'
    # We adapt the request_payload for it.
    hallucination_check_input = {
        "confidence": initial_confidence
    }  # Can add other relevant parts of payload if needed
    hallucination_result = guard_response(
        hallucination_check_input, threshold=confidence_threshold
    )
    logger.info(
        "Hallucination guard result",
        extra={"result": hallucination_result, "threshold": confidence_threshold},
    )

    middleware_passed_initial_checks = True  # From directive_validation_result

    if not hallucination_result.get("valid", False):
        # Even if hallucination guard fails, therapist might still review,
        # but we should note the middleware's preliminary finding.
        # The diagram implies Therapist gets "middleware_validation: true" only if both pass.
        # Let's adjust: if hallucination fails, middleware_validation is false.
        middleware_passed_initial_checks = False
        # We could return early here, or let therapist make the final call on low confidence.
        # The user flow says "Therapist Approval" AFTER "Middleware Validation".
        # So if middleware (validator + hallucination) fails, therapist might not even be called
        # or is called with middleware_validation: false.
        # Let's stick to the diagram: if initial middleware fails, therapist is informed.

    # Step 3: Therapist validation
    # Prepare payload for therapist as per the example
    therapist_input = {
        "agent": request_payload.get("agent"),
        "directive": request_payload.get("directive"),
        "confidence": initial_confidence,  # Pass the original confidence
        "middleware_validation": middleware_passed_initial_checks
        and hallucination_result.get(
            "valid", True
        ),  # True if directive AND hallucination checks passed
    }

    # If initial middleware (validator or hallucination) failed, therapist input reflects this.
    # The therapist may still choose to override.
    if not therapist_input["middleware_validation"]:
        logger.info(
            "Therapist review triggered despite initial middleware failure",
            extra={
                "directive_valid": directive_validation_result.get("is_valid"),
                "hallucination_valid": hallucination_result.get("valid"),
            },
        )
        post_agent_feed("Therapist review due to middleware failure")

    # Delegate the final decision to the Therapist agent which may apply
    # additional business rules beyond this middleware's scope.
    therapist_decision = therapist_validate(therapist_input)
    logger.info("Therapist decision", extra={"result": therapist_decision})

    if not therapist_decision.get("valid", False):
        post_agent_feed("Therapist rejected request")
        return {
            "final_valid": False,
            "reason": therapist_decision.get("reason", "Therapist rejected"),
            "source": "therapist",
        }

    # If all checks pass
    final_result = {
        "final_valid": True,
        "directive": therapist_decision.get("directive"),
        "source": "all_middleware_approved",
    }
    logger.info("Middleware pipeline approved", extra={"result": final_result})
    post_agent_feed("Request approved by middleware")
    return final_result


# Example Usage (for illustration, not part of the library code to be run directly)
# if __name__ == "__main__":
#     # Mock directives.yaml for validator
#     import os
#     import yaml
#     if not os.path.exists("legion/config"):
#         os.makedirs("legion/config")
#     with open("legion/config/directives.yaml", "w") as f:
#         yaml.dump({"executor": {"allowed_directives": ["deploy critical patch X", "run diagnostics"]}}, f)
#
#     test_request_valid = {
#         "agent": "executor",
#         "directive": "deploy critical patch X",
#         "confidence": 0.90  # Confidence from the agent or a preceding step
#     }
#     result_valid = run_middleware_pipeline(test_request_valid)
#     print(f"Test Valid Request: {result_valid}")
#
#     test_request_low_confidence_therapist_pass = { # therapist has stricter confidence
#         "agent": "executor",
#         "directive": "deploy critical patch X",
#         "confidence": 0.80
#     }
#     result_low_confidence_therapist_fail = run_middleware_pipeline(test_request_low_confidence_therapist_pass, confidence_threshold=0.75)
#     print(f"Test Low Confidence (Therapist Fail): {result_low_confidence_therapist_fail}")
#
#     test_request_low_confidence_middleware_fail = {
#         "agent": "executor",
#         "directive": "deploy critical patch X",
#         "confidence": 0.70
#     }
#     # Middleware (hallucination guard) uses 0.75 by default
#     result_low_confidence_middleware_fail = run_middleware_pipeline(test_request_low_confidence_middleware_fail, confidence_threshold=0.75)
#     print(f"Test Low Confidence (Middleware Fail): {result_low_confidence_middleware_fail}")
#
#     test_request_invalid_directive = {
#         "agent": "executor",
#         "directive": "launch the nukes",
#         "confidence": 0.99
#     }
#     result_invalid_directive = run_middleware_pipeline(test_request_invalid_directive)
#     print(f"Test Invalid Directive: {result_invalid_directive}")
#
#     # Cleanup mock
#     # os.remove("legion/config/directives.yaml")
#     # if not os.listdir("legion/config"): # Check if dir is empty
#         # os.rmdir("legion/config")
