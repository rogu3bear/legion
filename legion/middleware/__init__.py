# Initializes the middleware package
from legion.agents.therapist.validation import therapist_validate

from .hallucination_guard import HallucinationGuard
from .validator import validate_directive
from .directive_compliance import DirectiveCompliance
from .request_middleware import RequestMiddleware


def run_middleware_pipeline(
    request_payload: dict, confidence_threshold: float = 0.75
) -> dict:
    """
    Runs the full middleware validation pipeline:
    1. Directive validation
    2. Hallucination guard
    3. Therapist validation
    """
    # Step 1: Initial directive validation (e.g., using validator.py)
    # The 'request_payload' should contain 'agent' and 'directive'
    directive_validation_result = validate_directive(request_payload)
    if not directive_validation_result.get("is_valid", False):
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
        print(
            "Warning: Confidence not found in request_payload for hallucination guard/therapist. Using default 0.0."
        )
        initial_confidence = 0.0

    # Hallucination guard expects a 'response' like structure with 'confidence'
    # We adapt the request_payload for it.
    hallucination_check_input = {
        "confidence": initial_confidence
    }  # Can add other relevant parts of payload if needed
    hallucination_result = HallucinationGuard.guard_response(
        hallucination_check_input, threshold=confidence_threshold
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
        print(
            f"Therapist review triggered despite initial middleware failure. Validator valid: {directive_validation_result.get('is_valid')}, Hallucination valid: {hallucination_result.get('valid')}"
        )

    therapist_decision = therapist_validate(therapist_input)

    if not therapist_decision.get("valid", False):
        return {
            "final_valid": False,
            "reason": therapist_decision.get("reason", "Therapist rejected"),
            "source": "therapist",
        }

    # If all checks pass
    return {
        "final_valid": True,
        "directive": therapist_decision.get("directive"),
        "source": "all_middleware_approved",
    }


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
