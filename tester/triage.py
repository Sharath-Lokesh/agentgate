"""
AgentGate — failure triage.

When the agent-under-test produces a decision for a test case, AgentGate compares
it to the oracle (expected_decision) and, on failure, classifies WHY the test
failed into one of three buckets (the Track-3 "house favourite" taxonomy):

  - assertion   : the software under test is wrong (real defect)  -> file Jira defect
  - automation  : the test/automation itself broke (locator, tool, harness) -> suggest fix
  - environment : an external/infra problem (timeout, service down) -> escalate

This module is deliberately free of any UiPath SDK dependency so it can be
unit-tested locally before being wired into the coded agent inside UiPath.
"""

from dataclasses import dataclass
from enum import Enum


class Triage(str, Enum):
    ASSERTION = "assertion"
    AUTOMATION = "automation"
    ENVIRONMENT = "environment"


class Routing(str, Enum):
    FILE_DEFECT = "file_jira_defect"
    SUGGEST_FIX = "suggest_fix"
    ESCALATE = "escalate"


# Signals that indicate the failure is NOT the agent's fault.
ENVIRONMENT_SIGNALS = (
    "timeout", "timed out", "connection refused", "503", "502",
    "service unavailable", "unreachable", "network", "dns",
)
AUTOMATION_SIGNALS = (
    "element not found", "locator", "selector", "no such element",
    "stale element", "nullreference", "test harness", "assertion setup",
    "malformed test", "parse error in test",
)


@dataclass
class RunOutcome:
    request_id: str
    expected_decision: str
    actual_decision: str | None      # None if the run did not complete
    error_text: str = ""             # any runtime error captured during the run


@dataclass
class TriageResult:
    request_id: str
    passed: bool
    triage: Triage | None
    routing: Routing | None
    rationale: str


def classify(outcome: RunOutcome) -> TriageResult:
    """Classify a single test outcome into pass / fail + triage bucket + routing."""
    err = (outcome.error_text or "").lower()

    # 1) Infra/environment problems first — never blame the agent for these.
    if any(sig in err for sig in ENVIRONMENT_SIGNALS):
        return TriageResult(outcome.request_id, False, Triage.ENVIRONMENT,
                            Routing.ESCALATE,
                            "External/infrastructure signal detected; escalating.")

    # 2) Test/automation breakage — the harness failed, not the product.
    if any(sig in err for sig in AUTOMATION_SIGNALS):
        return TriageResult(outcome.request_id, False, Triage.AUTOMATION,
                            Routing.SUGGEST_FIX,
                            "Automation/harness signal detected; suggesting fix.")

    # 3) Run did not complete and we have no recognised infra/automation signal.
    if outcome.actual_decision is None:
        return TriageResult(outcome.request_id, False, Triage.AUTOMATION,
                            Routing.SUGGEST_FIX,
                            "Run did not complete and error is unrecognised; "
                            "treating as automation issue for review.")

    # 4) Run completed — compare against the oracle.
    if outcome.actual_decision == outcome.expected_decision:
        return TriageResult(outcome.request_id, True, None, None,
                            "Actual decision matches expected.")

    # 5) Completed but wrong answer => real defect in the software under test.
    return TriageResult(outcome.request_id, False, Triage.ASSERTION,
                        Routing.FILE_DEFECT,
                        f"Expected {outcome.expected_decision}, got "
                        f"{outcome.actual_decision}; filing defect.")


def gate_decision(results: list[TriageResult]) -> tuple[bool, str]:
    """The release gate: block deployment if any assertion-class failure exists."""
    assertion_failures = [r for r in results
                          if not r.passed and r.triage == Triage.ASSERTION]
    if assertion_failures:
        ids = ", ".join(r.request_id for r in assertion_failures)
        return False, f"BLOCKED: assertion failures require human sign-off ({ids})."
    return True, "PASSED: no assertion failures; release may proceed."
