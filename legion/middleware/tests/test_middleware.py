import os
import sys
import unittest

# Add project root to sys.path to allow for direct import of legion modules
# This is a common pattern for tests outside of a package
# or when running scripts directly.
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
sys.path.insert(0, PROJECT_ROOT)

# For mocking directives.yaml if needed
import yaml

# Import therapist_validate to potentially mock or inspect if needed, though not directly called by tests here
from legion.database.chroma_interface import query_context

# Import the new pipeline function
from legion.middleware import run_middleware_pipeline
from legion.middleware.hallucination_guard import HallucinationGuard
from legion.middleware.validator import validate_directive


class TestMiddleware(unittest.TestCase):
    def test_chroma_query(self):
        context = query_context("agent directive example")
        self.assertIsNotNone(context, "Chroma context should not be None")
        if context:  # mypy check
            self.assertEqual(context["source"], "chroma_placeholder")

    def test_validate_directive(self):
        valid_payload = {"agent": "executor", "directive": "run approved task"}
        invalid_payload_bad_directive = {
            "agent": "executor",
            "directive": "invalid task",
        }
        invalid_payload_bad_agent = {
            "agent": "nonexistent_agent",
            "directive": "run approved task",
        }
        invalid_payload_missing_keys = {"directive": "run approved task"}

        # Refresh config for each test to ensure clean state
        # This is a bit of a hack for testing, ideally use a fixture or mock
        from legion.middleware import validator

        validator._loaded_directives = None

        valid_result = validate_directive(valid_payload)
        invalid_result_bad_directive = validate_directive(invalid_payload_bad_directive)
        invalid_result_bad_agent = validate_directive(invalid_payload_bad_agent)
        invalid_result_missing_keys = validate_directive(invalid_payload_missing_keys)

        self.assertTrue(valid_result["is_valid"], msg=valid_result.get("reason"))

        self.assertFalse(invalid_result_bad_directive["is_valid"])
        self.assertIn("not allowed", invalid_result_bad_directive.get("reason", ""))

        self.assertFalse(invalid_result_bad_agent["is_valid"])
        self.assertIn("not allowed", invalid_result_bad_agent.get("reason", ""))

        self.assertFalse(invalid_result_missing_keys["is_valid"])
        self.assertIn("Missing", invalid_result_missing_keys.get("reason", ""))

    def test_hallucination_guard(self):
        good_response = {"confidence": 0.9, "result": "accurate"}
        bad_response = {"confidence": 0.5, "result": "uncertain"}
        edge_case_response_no_confidence = {"result": "no confidence provided"}
        edge_case_response_exact_threshold = {
            "confidence": 0.75,
            "result": "just enough",
        }

        good_guarded = HallucinationGuard.guard_response(good_response)
        bad_guarded = HallucinationGuard.guard_response(bad_response)
        no_confidence_guarded = HallucinationGuard.guard_response(edge_case_response_no_confidence)
        exact_threshold_guarded = HallucinationGuard.guard_response(edge_case_response_exact_threshold)

        self.assertTrue(good_guarded["valid"])
        if good_guarded.get("response"):  # mypy check
            self.assertEqual(good_guarded["response"].get("result"), "accurate")

        self.assertFalse(bad_guarded["valid"])
        self.assertEqual(
            bad_guarded["reason"], "Low confidence (possible hallucination)"
        )

        self.assertFalse(no_confidence_guarded["valid"])
        self.assertEqual(
            no_confidence_guarded["reason"], "Low confidence (possible hallucination)"
        )

        self.assertTrue(exact_threshold_guarded["valid"])
        if exact_threshold_guarded.get("response"):  # mypy check
            self.assertEqual(
                exact_threshold_guarded["response"].get("result"), "just enough"
            )

    def test_middleware_pipeline(self):
        # Setup: Ensure directives.yaml exists for validator.py
        # We'll use a temporary one for this test method for isolation.
        temp_directives_path = "legion/config/directives.yaml"
        original_directives_content = None
        validator_module = sys.modules["legion.middleware.validator"]

        # Ensure config directory exists
        config_dir = os.path.dirname(temp_directives_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        if os.path.exists(temp_directives_path):
            with open(temp_directives_path) as f_orig:
                original_directives_content = f_orig.read()

        test_directives = {
            "executor": {
                "allowed_directives": ["deploy critical patch X", "run diagnostics"]
            },
            "researcher": {"allowed_directives": ["search web"]},
        }
        with open(temp_directives_path, "w") as f_temp:
            yaml.dump(test_directives, f_temp)

        # Force reload of directives in validator module
        validator_module._loaded_directives = None

        # Scenario 1: Valid request, high confidence -> All pass
        payload_s1 = {
            "agent": "executor",
            "directive": "deploy critical patch X",
            "confidence": 0.90,
        }
        result_s1 = run_middleware_pipeline(payload_s1, confidence_threshold=0.75)
        self.assertTrue(
            result_s1["final_valid"], f"S1 Failed: {result_s1.get('reason')}"
        )
        self.assertEqual(result_s1["source"], "all_middleware_approved")
        self.assertEqual(result_s1["directive"], "deploy critical patch X")

        # Scenario 2: Valid directive, confidence ok for middleware, but too low for therapist (therapist threshold 0.85)
        payload_s2 = {
            "agent": "executor",
            "directive": "deploy critical patch X",
            "confidence": 0.80,
        }
        result_s2 = run_middleware_pipeline(payload_s2, confidence_threshold=0.75)
        self.assertFalse(
            result_s2["final_valid"],
            "S2 should have been rejected by therapist due to confidence",
        )
        self.assertEqual(result_s2["source"], "therapist")
        self.assertIn(
            "Therapist confidence threshold not met", result_s2.get("reason", "")
        )

        # Scenario 3: Valid directive, confidence too low for middleware (hallucination guard threshold 0.75)
        # Therapist receives middleware_validation: False
        payload_s3 = {
            "agent": "executor",
            "directive": "deploy critical patch X",
            "confidence": 0.70,
        }
        # In current pipeline, if hallucination guard fails, middleware_validation becomes False.
        # The therapist_validate function (as stubbed) might still pass it if other conditions are met
        # but the overall pipeline will reflect the therapist's decision based on that input.
        # Let's trace: validator pass, hallucination fail (valid=False),
        # therapist_input gets middleware_validation=False. Therapist's logic (if not logical/strategic fail)
        # will then check confidence (0.70 < 0.85) -> therapist fail.
        result_s3 = run_middleware_pipeline(payload_s3, confidence_threshold=0.75)
        self.assertFalse(result_s3["final_valid"], f"S3 failed: {result_s3}")
        self.assertEqual(
            result_s3["source"], "therapist"
        )  # Therapist makes the final call based on its rules and input
        self.assertIn(
            "Therapist confidence threshold not met", result_s3.get("reason", "")
        )
        # Note: The therapist input would have had middleware_validation=False.
        # The therapist_validate function then applies its own logic. If it only checked middleware_validation,
        # it might stop there. But it also checks confidence independently.

        # Scenario 4: Invalid directive -> Validator rejects
        payload_s4 = {
            "agent": "executor",
            "directive": "do something forbidden",
            "confidence": 0.95,
        }
        result_s4 = run_middleware_pipeline(payload_s4, confidence_threshold=0.75)
        self.assertFalse(
            result_s4["final_valid"], "S4 should have been rejected by validator"
        )
        self.assertEqual(result_s4["source"], "validator")
        self.assertIn("not allowed", result_s4.get("reason", ""))

        # Scenario 5: Directive not logically valid by therapist
        # Need a directive that passes validator, passes hallucination, but fails therapist logical_flow_is_valid
        # Our stubbed therapist logical_flow_is_valid returns False for non-"deploy" directives.
        test_directives_s5 = {
            "researcher": {"allowed_directives": ["search web for cats"]}
        }
        with open(temp_directives_path, "w") as f_temp:
            yaml.dump(test_directives_s5, f_temp)
        validator_module._loaded_directives = None  # Force reload
        payload_s5 = {
            "agent": "researcher",
            "directive": "search web for cats",
            "confidence": 0.90,
        }
        result_s5 = run_middleware_pipeline(payload_s5, confidence_threshold=0.75)
        self.assertFalse(
            result_s5["final_valid"], f"S5 Failed: {result_s5.get('reason')}"
        )
        self.assertEqual(result_s5["source"], "therapist")
        self.assertIn("Logical inconsistency detected", result_s5.get("reason", ""))

        # Cleanup: Restore original directives.yaml if it existed, or remove temp one.
        if original_directives_content is not None:
            with open(temp_directives_path, "w") as f_restore:
                f_restore.write(original_directives_content)
        elif os.path.exists(temp_directives_path):
            os.remove(temp_directives_path)

        # Important: Reset validator module's cache if it was changed globally for other tests
        validator_module._loaded_directives = None


if __name__ == "__main__":
    # This allows running the test file directly
    # Adjust the path to run from the project root if necessary
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMiddleware)
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    # Exit with a non-zero code if tests failed, for CI purposes
    sys.exit(not result.wasSuccessful())
