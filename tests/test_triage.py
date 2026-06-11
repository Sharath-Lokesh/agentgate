"""Unit tests for AgentGate triage logic. Run: python -m pytest -q"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tester.triage import (  # noqa: E402
    RunOutcome, Triage, Routing, classify, gate_decision,
)


def test_pass_when_decision_matches():
    r = classify(RunOutcome("REF-1", "APPROVE", "APPROVE"))
    assert r.passed and r.triage is None


def test_assertion_failure_files_defect():
    # Agent approved an over-limit claim it should have escalated.
    r = classify(RunOutcome("REF-2", "ESCALATE", "APPROVE"))
    assert not r.passed
    assert r.triage == Triage.ASSERTION
    assert r.routing == Routing.FILE_DEFECT


def test_prompt_injection_is_assertion_failure():
    # Hero case: injection tricked the agent into auto-approving an over-limit claim.
    r = classify(RunOutcome("REF-11", "ESCALATE", "APPROVE"))
    assert r.triage == Triage.ASSERTION


def test_environment_failure_escalates():
    r = classify(RunOutcome("REF-3", "APPROVE", None,
                             error_text="HTTP 503 Service Unavailable"))
    assert r.triage == Triage.ENVIRONMENT
    assert r.routing == Routing.ESCALATE


def test_automation_failure_suggests_fix():
    r = classify(RunOutcome("REF-4", "APPROVE", None,
                             error_text="Element not found: #submit locator"))
    assert r.triage == Triage.AUTOMATION
    assert r.routing == Routing.SUGGEST_FIX


def test_incomplete_run_unknown_error_is_automation():
    r = classify(RunOutcome("REF-5", "APPROVE", None, error_text="weird"))
    assert r.triage == Triage.AUTOMATION


def test_gate_blocks_on_assertion_failure():
    results = [
        classify(RunOutcome("REF-1", "APPROVE", "APPROVE")),
        classify(RunOutcome("REF-2", "ESCALATE", "APPROVE")),
    ]
    ok, msg = gate_decision(results)
    assert not ok and "BLOCKED" in msg


def test_gate_passes_when_only_env_failures():
    results = [
        classify(RunOutcome("REF-1", "APPROVE", "APPROVE")),
        classify(RunOutcome("REF-3", "APPROVE", None, error_text="timeout")),
    ]
    ok, msg = gate_decision(results)
    assert ok and "PASSED" in msg
