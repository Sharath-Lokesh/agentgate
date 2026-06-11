# AgentGate — Architecture

```
                 ┌────────────────────────────────────────────────┐
                 │              UiPath Automation Cloud             │
                 │                                                  │
  synthetic   →  │  ┌───────────┐   executes    ┌───────────────┐  │
  test cases     │  │  Tester    │ ───────────▶ │ Agent-under-  │  │
  (data/)        │  │ coded agent│  via Test     │ test (claims) │  │
                 │  │ (Python SDK)│  Cloud       │ Agent Builder │  │
                 │  └─────┬──────┘               └───────────────┘  │
                 │        │ classify (triage.py)                    │
                 │        ▼                                          │
                 │  assertion ─▶ Jira defect (Integration Service)   │
                 │  automation ─▶ suggested fix                      │
                 │  environment ─▶ escalate                          │
                 │        │                                          │
                 │        ▼  results + evidence                      │
                 │  ┌───────────────┐   block?   ┌───────────────┐  │
                 │  │ Test Manager  │ ─────────▶ │ Action Center  │  │
                 │  └───────────────┘  approval  │ (human sign-off)│ │
                 │        │  gate_decision()      └───────┬───────┘  │
                 │        ▼                                ▼          │
                 │   Maestro / Orchestrator: deploy OR block         │
                 └────────────────────────────────────────────────┘
```

- **Spine:** Test Cloud / Test Manager hold cases, runs, results, evidence.
- **Decision core:** `tester/triage.py` (pure Python, unit-tested) decides
  pass/fail, triage bucket, routing, and the release gate.
- **Governance:** assertion failures block deploy and require Action Center
  approval; Maestro/Orchestrator sequences the whole gate.
