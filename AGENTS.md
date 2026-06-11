# AGENTS.md — AgentGate

Guidance for coding agents (Claude Code / UiPath for Coding Agents) working in this repo.

## What this project is
An agentic test-and-release gate for AI-infused automations, built on the UiPath
Platform for UiPath AgentHack 2026 (Track 3 — Test Cloud). It tests a refund-approval
agent, triages failures (assertion/automation/environment), files Jira defects,
and blocks deployment pending human sign-off.

## Ground rules
- Keep all UiPath-SDK-dependent code inside `tester/agent.py` behind the `TODO[Labs]`
  markers until a Labs tenant is available; do not fabricate SDK calls that cannot run.
- Keep `tester/triage.py` free of UiPath imports — it must stay locally unit-testable.
- All test data is synthetic and PII-free; never introduce real customer data.
- Determinism matters: preserve the fixed SEED in the data generator.

## How to verify your changes
```
python data/generate_synthetic_data.py   # regenerate fixtures
python -m pytest -q                       # all triage/gating tests must pass
python -m tester.agent                    # pipeline runs end-to-end with stubs
```

## Conventions
- Python 3.11+, standard library only for core logic where possible.
- Decision vocabulary: APPROVE | ESCALATE | REJECT.
- Triage vocabulary: assertion | automation | environment.
- Document any coding-agent contribution in docs/CODING_AGENT.md (bonus evidence).
