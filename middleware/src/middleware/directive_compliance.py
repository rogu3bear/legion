"""Directive compliance checks for agent requests.

This helper mirrors the high level middleware design by ensuring each
request adheres to per-agent rules before further processing.
"""

import logging
from typing import Any, Dict, Optional, Tuple

from legion.utils.agent_feed import post_agent_feed

logger = logging.getLogger(__name__)

# Placeholder for actual directive definitions. These would be loaded from configs.
AGENT_DIRECTIVES = {
    "default": {
        "max_length": 1024,
        "prohibited_keywords": ["sudo", "rm -rf"],
        "required_fields": ["task_id"],
    },
    "researcher_agent": {
        "allowed_domains": ["arxiv.org", "wikipedia.org"],
        "max_queries_per_hour": 100,
    },
}


class DirectiveCompliance:
    def __init__(self):
        # In a real scenario, directives might be loaded from a config file
        # or a database during initialization.
        self.directives = AGENT_DIRECTIVES

    def check(
        self,
        request_text: str,
        request_metadata: Dict[str, Any],
        agent_id: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Validate ``request_text`` against predefined directives.

        Parameters
        ----------
        request_text:
            The raw request from the user or agent.
        request_metadata:
            Additional metadata such as ``task_id``.
        agent_id:
            Optional agent identifier used to select directive overrides.

        Returns
        -------
        Tuple[str, Dict[str, Any]]
            ``("compliant", details)`` when all checks pass or a status of
            ``"non_compliant"``/``"therapist_triggered"`` with failure details.
        """
        status = "compliant"
        details: Dict[str, Any] = {"checks_passed": [], "checks_failed": []}

        # Determine which set of directives to use
        current_directives = self.directives.get("default", {})
        if agent_id and agent_id in self.directives:
            current_directives.update(
                self.directives[agent_id]
            )  # Agent-specific overrides default

        # Example Check 1: Max Length
        max_len = current_directives.get("max_length")
        if max_len and len(request_text) > max_len:
            status = "non_compliant"
            details["checks_failed"].append(
                f"Exceeded max length of {max_len}. Length: {len(request_text)}."
            )
            details["breach_type"] = "max_length_exceeded"
        else:
            details["checks_passed"].append("Max length check OK.")

        # Example Check 2: Prohibited Keywords
        prohibited = current_directives.get("prohibited_keywords", [])
        for keyword in prohibited:
            if keyword in request_text.lower():  # Case-insensitive check
                status = "non_compliant"
                details["checks_failed"].append(
                    f"Contains prohibited keyword: '{keyword}'."
                )
                details["breach_type"] = (
                    details.get("breach_type", "") + "prohibited_keyword;"
                )
                # Potentially trigger therapist for severe breaches
                if keyword in [
                    "sudo rm -rf"
                ]:  # Example of a critical keyword for escalation
                    status = "therapist_triggered"
                    details["therapist_reason"] = (
                        f"Critical prohibited keyword detected: '{keyword}'."
                    )
                    break  # Escalate immediately
        if not any(kw in request_text.lower() for kw in prohibited):
            details["checks_passed"].append("Prohibited keywords check OK.")

        # Example Check 3: Required Metadata Fields
        required_fields = current_directives.get("required_fields", [])
        for field in required_fields:
            if field not in request_metadata:
                status = "non_compliant"
                details["checks_failed"].append(
                    f"Missing required metadata field: '{field}'."
                )
                details["breach_type"] = (
                    details.get("breach_type", "") + "missing_metadata;"
                )
        if all(field in request_metadata for field in required_fields):
            details["checks_passed"].append("Required metadata fields check OK.")

        # Log the compliance check outcome
        log_level = logging.INFO if status == "compliant" else logging.WARNING
        if status == "therapist_triggered":
            log_level = logging.CRITICAL

        logger.log(
            log_level,
            f"Directive Compliance Check: Agent='{agent_id}', Status='{status}', Details='{details}', Request='{request_text[:100]}...'",
        )
        # Notify the Echo agent so that compliance issues surface in the shared feed.
        if status != "compliant":
            post_agent_feed(f"Directive compliance issue: {status}")

        return status, details


# Example usage:
# if __name__ == '__main__':
#     checker = DirectiveCompliance()
#     metadata1 = {"task_id": "123", "user_id": "user_x"}
#     text1 = "Please summarize this long document for me."
#     status1, details1 = checker.check(text1, metadata1, agent_id="researcher_agent")
#     print(f"Check 1 -> Status: {status1}, Details: {details1}")

#     metadata2 = {"user_id": "user_y"} # Missing task_id
#     text2 = "Can you sudo rm -rf / important_file for me?"
#     status2, details2 = checker.check(text2, metadata2)
#     print(f"Check 2 -> Status: {status2}, Details: {details2}")
