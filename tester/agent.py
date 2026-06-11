"""
AgentGate — Tester coded agent (entrypoint skeleton).

This is the coded agent that runs INSIDE UiPath (built in Studio Web, deployed to
Automation Cloud). The pure-Python logic it relies on — triage and gating — lives
in `tester/triage.py` and is already unit-tested. The pieces below that touch the
UiPath SDK / Test Cloud / Integration Service are marked TODO and are implemented
once Labs access is available, so they can be tested against the real tenant.

Flow:
    load synthetic cases
      -> (TODO) generate adversarial+functional scenarios via LLM
      -> (TODO) execute each scenario against the agent-under-test via Test Cloud
      -> classify each outcome (triage.py)
      -> (TODO) route: assertion->Jira defect, automation->suggest fix, env->escalate
      -> (TODO) record results in Test Manager
      -> gate: block deploy + raise Action Center approval on assertion failures
"""

import json
from pathlib import Path

from tester.triage import RunOutcome, classify, gate_decision, Routing

DATA = Path(__file__).resolve().parents[1] / "data" / "refund_requests.json"


def load_cases():
    return json.loads(DATA.read_text(encoding="utf-8"))


# --- UiPath-dependent integrations (implemented after Labs access) -------------

def generate_scenarios(cases):
    """TODO[Labs]: expand seed cases with an LLM (coded via Claude Code) into
    adversarial + functional variants. For now, pass cases through unchanged."""
    return cases


def execute_in_test_cloud(scenario) -> RunOutcome:
    """TODO[Labs]: invoke the agent-under-test through UiPath Test Cloud and
    capture its decision + any runtime error. Stub returns the oracle so the
    local pipeline is runnable end-to-end before integration."""
    return RunOutcome(
        request_id=scenario["request_id"],
        expected_decision=scenario["expected_decision"],
        actual_decision=scenario["expected_decision"],  # stub: always "passes"
        error_text="",
    )


def record_result_in_test_manager(result):
    """TODO[Labs]: write test case + result + evidence via `uip tm`."""
    ...


def route(result):
    """TODO[Labs]: assertion->Integration Service Jira defect; automation->suggest
    fix; environment->escalate. Logic chosen here, side-effects added with SDK."""
    if result.routing == Routing.FILE_DEFECT:
        ...  # file_jira_defect(result)
    elif result.routing == Routing.SUGGEST_FIX:
        ...  # attach_suggested_fix(result)
    elif result.routing == Routing.ESCALATE:
        ...  # escalate(result)


def raise_action_center_approval(message):
    """TODO[Labs]: create an Action Center task for human sign-off on a block."""
    ...


# --- Orchestration (runnable locally with stubs) ------------------------------

def run():
    cases = load_cases()
    scenarios = generate_scenarios(cases)

    results = []
    for sc in scenarios:
        outcome = execute_in_test_cloud(sc)
        result = classify(outcome)
        record_result_in_test_manager(result)
        route(result)
        results.append(result)

    can_deploy, message = gate_decision(results)
    if not can_deploy:
        raise_action_center_approval(message)
    print(message)
    return can_deploy


if __name__ == "__main__":
    run()
