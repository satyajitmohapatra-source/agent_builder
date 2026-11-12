# Generalized Agent Builder

*Methodology draft for review*

The builder takes a product requirements document (PRD) and guides an engineer from requirements to a verified conversational agent. The same chat-first workflow should work in Claude Code and Codex, with a shared project record that either can resume. Chotu is a reference integration for the shared port protocol.

The PRD governs what the agent should accomplish and how people interact with it. The port protocol and target SDK govern how the agent registers, receives turns, returns results, and uses platform services. The builder chooses the internal architecture that fits the product and conforms to the protocol. The five layers below organize the design review and can be realized by as few components as the agent needs.

## Technology baseline

**Python and a modular architecture** are the baseline for the builder tooling and generated agents. The builder runs as a chat-first workflow in Claude Code and Codex, using a shared Markdown project record and Python tooling for generation and verification. Organize generated code around the port interface, skill workflows, and integrations as needed.

| Technology | Role |
| --- | --- |
| **FastAPI** | The HTTP interface for a standalone host or adapter when the deployment calls for one. An in-process agent exposes the SDK interface through its host. |
| **LangGraph** | The default candidate for stateful, branching workflows that benefit from a graph. Use ordinary Python for straightforward skills. Store resumable state through the host SDK where the protocol requires it. |
| **PostgreSQL** | Durable storage for the host or its domain services when they own persistent records. |
| **Redis** | Optional infrastructure for an identified need such as shared caching or short-lived coordination. |

The builder selects dependencies based on the reviewed design and the target SDK's rules. Under Chotu contract 0.2, generated agents use the SDK's state, data, and action interfaces. Database access and execution authorization remain with the platform.

## Proposed directory structure

### Builder repository

```text
agent-builder/
├── README.md
├── AGENTS.md                 # Codex entry point
├── CLAUDE.md                 # Claude Code entry point
├── workflow/
│   ├── FLOW.md               # Shared methodology and review gates
│   ├── templates/            # Design, requirements map, and decision log
│   └── skills/               # Reusable procedures for the engineer and assistant
├── src/agent_builder/        # Python generation and verification tooling
├── tests/                    # Builder tests and sample PRD fixtures
└── pyproject.toml
```

Both assistant entry points direct the engineer to the same workflow. The Python tooling handles repeatable operations such as scaffolding and running checks. The sample PRDs exercise the builder's flow across different agent domains.

### Port assignments

Engineers share the builder workflow and the platform contract. Each builder run targets one assigned port and records the responsible engineer, port identifier, relevant PRD or PRD sections, pinned SDK and protocol version, and target checkout. Engineers working in parallel keep their design decisions, open issues, and verification results in their own port project records.

If a requirement spans ports, record the handoff and raise any unresolved ownership or interface decision with the platform owner. Carry that dependency into the affected port's review and acceptance tests.

### Agent project workspace

```text
agent-project/
├── inputs/                   # PRD and reference to the pinned SDK and protocol
├── design/
│   ├── architecture.md       # Provisional draft and reviewed five-layer design
│   ├── requirements.md       # PRD requirements mapped to behaviors and tests
│   └── decisions.md          # Layer status, decisions, issues, and waivers
├── <agent-package>/          # Generated agent, SDK manifest, and tests
└── verification/             # Conformance and product acceptance results
```

The agent project record lives alongside the package so an engineer can resume the review from either assistant. The target SDK dictates the package name, manifest, test layout, and packaging rules. For Chotu, the generated package would be `port_N/` and use the files required by the pinned kit. The five layers stay in one architecture document by default. The builder adds code modules for skills, conversation, or state where the reviewed design calls for them.

## Visual review at every stage

Run the five visual review skills at intake, on the initial architecture draft, at each of the five layer reviews, during generation planning and implementation, and at verification and handoff. Keep one current `design/visual-review.md` in each project and link it from the review record. For each stage, refresh these views:

1. [System blocks](workflow/skills/draw-system-blocks/SKILL.md) for ownership and interfaces.
2. [Workflow flowchart](workflow/skills/draw-workflow-flowchart/SKILL.md) for decisions and alternate paths.
3. [LangGraph or actual control flow](workflow/skills/draw-langgraph-flow/SKILL.md) for routing, state, and resumption.
4. [Conversation sequence](workflow/skills/draw-conversation-flow/SKILL.md) for user turns, tool calls, database operations where applicable, and results.
5. [Skills used](workflow/skills/list-workflow-skills/SKILL.md) for the builder skills applied and the runtime skills involved.

Show the current views inline where possible, with links to the complete visual review. Before asking for a decision, show the diagrams that explain the options and show the skills used. After a decision, refresh the affected views and show the change before moving on. If a view has no new evidence, retain its latest version and label what is pending. Use proposed paths in design and source or trace evidence when claiming implementation or observed behavior.

## 1. Read the PRD and establish the constraints

- Extract the intended users, their goals, the interactions each goal requires, dependencies, and acceptance criteria. Assign stable identifiers to requirements and link them to the relevant PRD passages.
- Record the target SDK and contract version, along with the platform rules that shape the design. Identify who owns routing, turn-taking, permissions, confirmation, and execution where those responsibilities affect the agent.
- Label each consequential item as a **requirement**, **proposed default**, or **open decision**. Record ambiguities and conflicts with the requirements they affect. Use provisional assumptions to make the first draft reviewable.

**Output:** A requirements map, the governing contract version, and an initial issue log.

## 2. Draft the architecture as principal architect

After intake, the assistant acts as principal architect. It uses the PRD, assigned scope, and port protocol to propose a coherent first design across all five layers. For each layer, explain the recommended approach, why it fits the requirements, and the tradeoffs behind choices the engineer needs to make. Label assumptions, missing evidence, and unresolved protocol or ownership questions.

Show the full draft before starting the layer-by-layer review. Walk through a representative user goal, including where the agent pauses for input and how it reaches a known outcome. In the GUI, open the draft in the architecture workspace alongside the assistant chat. The engineer can challenge a choice, explore alternatives, and apply a proposed revision or record an open issue. Layer closure remains explicit.

| Layer | What the builder drafts |
| --- | --- |
| **1. Agent identity and objectives** | Who the agent serves, which outcomes it owns, its boundaries, and when it hands off. |
| **2. Orchestration and decision-making** | How the agent interprets requests, selects a skill, and decides whether to clarify, continue, cancel, or hand off. Make the agent and platform responsibilities explicit. |
| **3. Skills and capabilities** | Group PRD requirements by user goal. Identify which goals call for a reusable skill, a simple operation, or a platform service. Define each skill's behavior and dependencies. |
| **4. User interaction and conversation management** | How the agent asks questions, presents choices, communicates outcomes, and handles interruption, cancellation, and resumption within platform rules. |
| **5. Memory, state, and execution** | What the agent remembers, what it needs to resume an in-progress task, and how a requested operation reaches a known outcome. Define approval ownership and handling of failed or uncertain execution where applicable. |

### Design each skill around a user goal

A skill owns the task-specific workflow. The agent coordinates the conversation across skills, subject to the platform's rules. An integration such as a calendar API is a tool the skill can use.

For each skill, document its entry conditions, required context, inputs and outputs, questions and choices for the user, workflow states and pause points, tools and permissions, approval requirements, cancellation and resume behavior, failure handling, and completion criteria. Keep simple operations simple. For multi-turn work, specify what a reply can resolve and what happens when the user changes topic or leaves.

### Required architecture visuals

Embed visuals directly in every architecture document, including the provisional draft. Use Mermaid by default.

- **Component diagram.** Show agent, skill, tool, and platform boundaries and who owns the main responsibilities.
- **Sequence or data-flow diagram.** Show the conversation and its database reads and writes in the same sequence. Label the responsible service, the record read or written, and where authorization, confirmation, or commit occurs. Include task-state checkpoints where relevant. Keep agent SDK calls and platform database access on separate lanes when the contract assigns them to different components.
- **State diagram for resumable workflows.** Show the waiting, resume, cancellation, and terminal transitions that the design depends on.

Update affected diagrams when a review decision changes the architecture. Label proposed behavior and unresolved paths clearly.

**Output:** One provisional design with embedded visuals and links from its proposed behaviors to the PRD and protocol.

## 3. Discuss, document, and close each layer

1. Start with Layer 1. Present the relevant requirements, provisional choices, and open issues. Discuss meaningful alternatives and their implications before asking the engineer to choose.
2. Record the agreed behavior, rationale, affected requirements, and any remaining issues. Each open issue has an owner, a next action, and the layer or capability it affects.
3. Close the layer explicitly before advancing. The engineer may waive a design issue with a recorded rationale and impact. A protocol violation remains a blocker. A layer with an unresolved blocking issue stays open.
4. Reopen an earlier layer if a later decision invalidates an agreement. Show the change and update the affected skill contracts and acceptance criteria.

**Output:** Five reviewed layers and a decision and issue log. The record gives another engineer or assistant enough context to resume at the current review point.

## 4. Generate, verify, and hand off

**Generation gate.** A request to create an agent starts at intake. Present the full draft, ask the engineer to review each of the five layers in order, and record explicit closure for each one. Before creating or changing generated agent code, verify the project review record shows all five layers closed and that generation blockers are resolved. An existing prototype or passing test result does not count as review. If a layer is open, continue from the earliest open layer and keep generation pending.

1. **Check readiness.** Confirm that the reviewed design covers each required outcome, identifies the responsible skill or service, and defines acceptance criteria. Resolve blockers before generating the affected capability.
2. **Derive the build and test plan.** Map each required outcome to the implementation responsible for it and to a verification case. For a multi-turn skill, cover missing information, a pause and resume, cancellation, and failure where applicable.
3. **Generate one representative workflow end to end.** Connect the agent to the port protocol and exercise the workflow through the SDK harness. Once the workflow works, generate the remaining approved capabilities and test how they interact.
4. **Run protocol conformance and product acceptance.** Use the target SDK's conformance suite for the platform contract and PRD-derived scenarios for user-visible behavior. Record the two results separately, including checks that could not run.
5. **Resolve failures and rerun the affected checks.** Fix implementation defects against the reviewed design. When a failure exposes a missing product decision or requires a change to agreed behavior, reopen the relevant layer and record the decision before regenerating.
6. **Hand off the result.** Deliver the generated agent, tests and results, reviewed design, SDK and contract versions, and the decision and issue log. Show the verification status for each required PRD outcome.

## Reusable builder skills

Engineers can ask for these skills in the GUI assistant or invoke the same procedures through Claude Code or Codex. The assistant uses the assigned port's project record as context and presents proposed changes for review. These skills guide the engineer during development. Section 2 defines the task workflows that run inside a generated agent.

| Skill | When to use it | What it produces |
| --- | --- | --- |
| **Analyze the PRD** | Start a project or review a PRD revision. | User goals, assigned scope, traceable requirements, acceptance criteria, and questions the PRD leaves open. |
| [**Principal Agent Architect**](workflow/skills/principal-agent-architect/SKILL.md) | Prepare the first design after intake or revise it after a material change. | An architecture document across all five layers, with component and data-flow diagrams, decision rationale, and a representative conversation. |
| [**Skill Framework Designer**](workflow/skills/skill-framework-designer/SKILL.md) | Design independently implementable and testable workflows for user goals that require human input. | A shared interaction contract, reusable skill template, and two worked examples covering pause, resume, and verification. |
| [**Conversation Controller Designer**](workflow/skills/conversation-controller-designer/SKILL.md) | Design turn ownership and task switching for an agent with multiple skills. | An ownership map, arbitration rules, state diagrams, event schemas, and tests for conflicts and duplicate responses. |
| [**Observe Orchestrator State**](workflow/skills/observe-orchestrator-state/SKILL.md) | Inspect how a run moved through orchestrator or task states. | A state diagram and observed transition timeline with source references. |
| [**Observe Conversation Flow**](workflow/skills/observe-conversation-flow/SKILL.md) | Follow a recorded conversation through turns, waits, and handoffs. | A sequence diagram or timeline showing ownership and delivery evidence. |
| [**Trace Function Calls**](workflow/skills/trace-function-calls/SKILL.md) | Investigate which functions, tools, or services ran for a turn or action. | A call tree or waterfall showing nesting, latency, retries, and failures. |
| **Review a conversation** | Explore how a proposed workflow behaves across turns. | Sample conversations for the normal path, missing details, a change of mind, and relevant failure paths. Flags decisions that need engineer review. |
| **Check a port boundary** | Review a capability that crosses ports or uses a platform service. | A contract-backed account of who owns the action or handoff, what permission is required, and what remains unresolved. |
| **Review a design layer** | Prepare to close a layer or revisit a decision. | A record of decisions, rationale, unresolved issues, and any changes needed in other layers. The engineer closes the layer explicitly. |
| **Verify the generated agent** | Check the agent against the reviewed design and pinned SDK. | Separate protocol conformance and product acceptance results, mapped back to the requirements, with failed or unrun checks identified. |

Each builder skill defines when to use it, what inputs it reads, what procedure it follows, what record it produces, and when it needs an engineer's decision. One skill can be used on its own. The builder's review order and closure rules still apply.

## Second-pass review

Start with PRD intake and the first architecture draft. Decide which gaps the builder can fill with provisional defaults, which choices need explicit engineer approval, and what the initial review should show. Then refine the closure criteria for each layer and walk a short sample PRD through the methodology before implementing the builder.

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
