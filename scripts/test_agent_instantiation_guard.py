#!/usr/bin/env python3
import unittest
from argparse import Namespace

import libcst as cst

# Assuming the codemod script is saved as agent_instantiation_guard.py
# Adjust the import path if necessary
from scripts.agent_instantiation_guard import (
    AgentInstantiationCodemod,
    class_name_to_agent_key,
)
from scripts.legion_codemod_context import CodemodContext


# Helper to run the codemod on a string
def run_codemod_on_string(source_code, apply_fixes=False):
    Namespace(apply=apply_fixes)
    context = CodemodContext(filename="<string>")
    # Pass apply flag via codemod context scratch
    context.scratch["apply"] = apply_fixes
    # context.args.repo_root = Path.cwd()  # Assume running from repo root for tests
    codemod_instance = AgentInstantiationCodemod(context)
    input_tree = cst.parse_module(source_code)
    output_tree = codemod_instance.transform_module(input_tree)
    return output_tree.code, codemod_instance.warnings


class TestAgentInstantiationCodemod(unittest.TestCase):
    def test_class_name_to_agent_key(self):
        self.assertEqual(class_name_to_agent_key("ArchitectAgent"), "architect")
        self.assertEqual(class_name_to_agent_key("MetricsAgent"), "metrics")
        self.assertEqual(class_name_to_agent_key("UxDesignerAgent"), "ux_designer")
        self.assertEqual(class_name_to_agent_key("PingAgent"), "ping")

    def test_detection_only(self):
        code = """
from legion.agents.python.architect import ArchitectAgent
from legion.agents.python.therapist import TherapistAgent

def my_func():
    agent1 = ArchitectAgent()
    therapist = TherapistAgent(config={})
"""
        _, warnings = run_codemod_on_string(code, apply_fixes=False)
        self.assertEqual(len(warnings), 2)
        self.assertIn("Direct instantiation of ArchitectAgent detected", warnings[0])
        self.assertIn("orchestrator.load_agent('architect')", warnings[0])
        self.assertIn("Direct instantiation of TherapistAgent detected", warnings[1])
        self.assertIn("orchestrator.load_agent('therapist')", warnings[1])

    def test_apply_fix(self):
        code = """
from legion.agents.python.architect import ArchitectAgent
from legion.agents.python.therapist import TherapistAgent as TA

def my_func():
    agent1 = ArchitectAgent(conf=1)
    therapist = TA()
"""
        # We need to parse the expected code to compare CSTs for robustness,
        # but comparing code strings is simpler for this example.
        # Note: Whitespace and comments might differ slightly depending on CST formatting.

        fixed_code, warnings = run_codemod_on_string(code, apply_fixes=True)

        # Basic check: Assert the instantiations are replaced
        self.assertIn("orchestrator.load_agent('architect')", fixed_code)
        self.assertIn("orchestrator.load_agent('therapist')", fixed_code)
        # Check imports are removed (this is complex to assert perfectly on string level)
        self.assertNotIn(
            "from legion.agents.python.architect import ArchitectAgent", fixed_code
        )
        self.assertNotIn(
            "from legion.agents.python.therapist import TherapistAgent as TA",
            fixed_code,
        )
        self.assertEqual(len(warnings), 2)  # Warnings should still be generated

    def test_skip_orchestrator_file(self):
        # Simulate running on the orchestrator file
        code = """
from legion.agents.python.architect import ArchitectAgent

class Orchestrator:
    def load(self):
        # This instantiation should NOT be flagged or changed
        agent = ArchitectAgent(self, None)
"""
        Namespace(apply=True)  # Try applying fixes
        # Simulate the context having the orchestrator path
        context = CodemodContext(filename="legion/orchestrator.py")
        # context.args.repo_root = Path.cwd()
        codemod_instance = AgentInstantiationCodemod(context)
        input_tree = cst.parse_module(code)
        output_tree = codemod_instance.transform_module(input_tree)

        self.assertEqual(output_tree.code, code)  # Code should be unchanged
        self.assertEqual(len(codemod_instance.warnings), 0)  # No warnings

    def test_no_change_if_no_agents(self):
        code = """
import os
def another_func():
    x = 1
    print('Hello')
"""
        fixed_code, warnings = run_codemod_on_string(code, apply_fixes=True)
        self.assertEqual(fixed_code, code)
        self.assertEqual(len(warnings), 0)

    def test_ignore_non_target_imports(self):
        code = """
from other.module import SomeClass
from legion.agents.python.architect import ArchitectAgent

x = SomeClass()
y = ArchitectAgent()
"""
        fixed_code, warnings = run_codemod_on_string(code, apply_fixes=True)
        self.assertIn("from other.module import SomeClass", fixed_code)
        self.assertNotIn(
            "from legion.agents.python.architect import ArchitectAgent", fixed_code
        )
        self.assertIn("y = orchestrator.load_agent('architect')", fixed_code)
        self.assertEqual(len(warnings), 1)


if __name__ == "__main__":
    unittest.main()
