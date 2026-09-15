import unittest

from cells_agent.workflow import route_work


class WorkflowTests(unittest.TestCase):
    def test_question_has_no_artifacts_memory_or_agents(self):
        result = route_work("question", delegation=True)
        self.assertEqual(result["mode"], "fast-path")
        self.assertFalse(result["delegation"])
        self.assertFalse(result["artifacts_required"])
        self.assertFalse(result["memory_required"])

    def test_test_command_does_not_load_coverage_or_authoring(self):
        self.assertEqual(route_work("test-command")["skills"], ["cells-cli-usage"])

    def test_direct_edit_requires_no_governed_chain(self):
        result = route_work("edit")
        self.assertEqual(result["mode"], "scoped-change")
        self.assertEqual(result["governed_phases"], [])

    def test_governed_chain_has_spec_before_design(self):
        result = route_work("feature", governed=True, delegation=True)
        self.assertTrue(result["delegation"])
        self.assertEqual(result["governed_phases"][:4], ["proposal", "spec", "design", "tasks"])

    def test_large_work_is_not_automatically_delegated(self):
        self.assertFalse(route_work("feature")["delegation"])
