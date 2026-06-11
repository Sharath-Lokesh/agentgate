# AgentGate

**An agentic test-and-release gate for AI-infused automations, built on the UiPath Platform.**

---

## Project Description

Enterprises are deploying AI agents into business processes faster than they can
quality-check them. AgentGate is the missing quality gate. It treats an
AI-infused automation as a system under test, generates adversarial and
functional test scenarios, executes them through **UiPath Test Cloud**, triages
every failure into **assertion / automation / environment**, and then acts on
each: it files a **Jira defect** for real product defects (assertion failures),
suggests a fix for broken automation, and escalates environment problems. Any
assertion-class failure **blocks deployment** and raises an **Action Center**
task for human sign-off, so a flawed agent cannot reach production unreviewed.

The demonstrated system under test is an **insurance claims auto-adjudication
agent** that performs straight-through processing — auto-approving low-value
claims, routing larger ones to a human adjuster, and denying out-of-policy
claims. It carries a known, planted flaw; AgentGate catches it, blocks the
release, routes it to a human, and only lets the corrected agent through.

**Business problem solved:** in regulated, high-volume domains like insurance,
banking, and healthcare, an AI agent that wrongly approves a claim, loan, or
prior-authorisation at scale is a direct financial and regulatory loss.
AgentGate moves AI-agent quality from a late, manual, ungoverned checkpoint into
a continuous, intelligent, governed gate — the difference between a prototype on
a laptop and software running in production.

## UiPath Components

- **UiPath Studio Web** — authoring environment for the whole solution.
- **UiPath Test Cloud / Test Manager** — the spine: test cases, test sets,
  execution, results, and evidence.
- **Agent Builder (low-code agent)** — the agent under test (claims adjudication).
- **Coded Agent (Python SDK)** — the AgentGate Tester: scenario generation and
  failure-triage logic.
- **Maestro / Orchestrator** — governs the gate sequence (execute → triage →
  human approval → deploy/block).
- **Action Center** — human-in-the-loop sign-off on blocked releases.
- **Integration Service (Jira)** — files defects for assertion-class failures.

## Agent Type

**Both.** The solution combines a **low-code agent** (Agent Builder — the system
under test) with a **coded agent** (Python SDK — the AgentGate Tester, built with
the assistance of a coding agent; see *Coding Agent Usage* below).

## Setup Instructions

> Full, judge-ready steps are completed during the build. Outline:

1. **Prerequisites:** access to a UiPath Automation Cloud / Labs tenant with Test
   Cloud, Agent Builder, Orchestrator, Action Center, and Integration Service
   (Jira) enabled. Python 3.11+ for the local components.
2. **Generate the test data (local, no tenant needed):**
   ```
   python data/generate_synthetic_data.py
   ```
3. **Run the local logic tests:**
   ```
   python -m pytest -q
   ```
4. **Deploy the agent under test** (Agent Builder) and the **Tester coded agent**
   to the tenant via UiPath Studio Web / CLI (`uip agent ...`). *(Detailed
   per-tenant steps added during the build.)*
5. **Configure the gate** in Maestro/Orchestrator and connect Integration Service
   to a Jira project. *(Detailed steps added during the build.)*
6. **Run the end-to-end gate** and observe results in Test Manager, the Jira
   defect, the Action Center task, and the deploy block/allow outcome.

---

## Coding Agent Usage 

- **Tool used:** Claude Code (via UiPath for Coding Agents).
- **How it contributed:** scaffolding the Tester coded agent, authoring the
  scenario-generation and failure-triage logic, and generating integration code
  for Test Cloud / Integration Service.
- **Evidence:** see `docs/CODING_AGENT.md` for session exports and screenshots;
  the coding-agent output is substantively integrated into the working Tester
  agent in `tester/`.
