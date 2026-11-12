Build a browser-based IDE for my existing AI Agent Builder. The builder generates agents from a PRD, follows a documented workflow, invokes reusable skills, asks the user for decisions, and produces code, diagrams, logs, and test results. The IDE should make that process visible and controllable from intake through handoff.

Start by inspecting the repository. Use the real workflow, skill definitions, project files, and run logs to determine what is already available. Where these files exist, read AGENT_BUILDER_FLOW.md, workflow/skills/, and the design and verification records under projects/. Identify how the builder is invoked, how it records user decisions, and what events or logs it emits. Then build a working vertical slice. If the builder has no callable runtime interface yet, create a small adapter boundary and demonstrate it with an explicitly labeled fixture run. Show which integrations are live and which are simulated.

## What the IDE should do

An engineer should be able to open an agent project, understand the proposed design, answer the builder’s questions, inspect the evidence behind a decision, and approve each stage. They should always be able to see where they are, what the builder is doing, and what needs their attention.

Use this workspace layout:

- Left sidebar: projects, project files, and workflow stages. Show which stage is active, waiting for input, approved, or failed.
- Center: conversation with the builder, beside or above the decision currently in review. Support free-text answers, choice buttons, and explicit approval. Show the effect of a proposed change before the engineer approves it.
- Right panel: visual review, skill runs, and evidence for the current stage. Make diagrams easy to expand and inspect.
- Bottom drawer: live logs and test results. Make it collapsible so it leaves room for design review.

Use an accessible, restrained desktop IDE layout. Make the panels resize or collapse and preserve a usable layout on narrower screens. Use real states and artifacts from the selected project wherever available.

## Workflow and human decisions

Read the workflow from the repository. The current Agent Builder workflow starts with PRD intake, presents a complete architecture draft, reviews the five layers in order, then moves through implementation planning, generation, verification, and handoff.

The five design layers are:
1. Identity and objectives
2. Orchestration and decision-making
3. Skills and capabilities
4. Interaction and conversation management
5. Memory, state, and execution

Show the full draft before the layer-by-layer review. For each layer, present the proposed decision, supporting diagrams, open questions, and relevant artifacts. Let the engineer request a revision or explicitly approve the layer. Record what they approved and which artifact revision they reviewed. Resume from the first open layer after refresh or restart.

Enforce the existing generation gate in the backend. The builder must verify that all five layers are closed and recorded generation blockers are resolved before it can create or change generated agent code. A casual chat reply, a finished model response, or a passing test must not implicitly approve a layer.

## Visual review and skills

At every workflow stage, surface the current versions of these five views:
- System block diagram for components, ownership, and interfaces
- Workflow flowchart for decisions, alternate paths, and failures
- LangGraph or actual control-flow diagram for routing, state, pause, and resumption
- Conversation sequence showing user turns, tool calls, outcomes, and database reads or writes where applicable
- Skills used, showing which builder skills actually ran and which runtime capabilities the generated agent uses

Read existing Mermaid blocks from the project’s visual-review.md when present. Render them inline and offer the source alongside the diagram. Make each diagram’s status clear, such as proposed, implemented, or observed in a test. Show the views relevant to the decision before asking for approval. After a decision, refresh the affected views and make the changes easy to review.

Discover existing skills from their SKILL.md files and expose their descriptions and usage. Show skill runs with status, inputs and outputs where safe, relevant artifact links, and errors. Distinguish a skill that is available or planned from one that actually ran. Allow manual invocation where the existing builder workflow supports it.

## Conversation, execution, and persistence

Make the IDE conversation the main interface for interacting with the builder. Put the model and builder execution behind a server-side adapter. Reuse existing integration points where possible. If the current workflow depends on GPT conversation state, inspect how that state is provided. Support importing user-provided context where needed. Do not assume automatic access to a user’s ChatGPT history.

Give each run a stable ID. Stream events for assistant messages, input requests, skill starts and finishes, artifact updates, approvals, errors, and test results. When the builder asks for input, persist the request and suspend that run until the user answers. Correlate the answer with the original request. After refresh or reconnect, restore the run history and any pending question without duplicating events or submitting an answer twice.

Use the repository’s project files as the source of truth for artifacts where appropriate. Store only the IDE state the builder does not already persist, such as run cursors or UI preferences. Scope file reads and writes to the selected workspace. Keep model credentials on the server, redact secrets in logs, and preserve the distinction between viewing a proposed change and applying it.

## Logs and verification

Show logs grouped by run and skill. Support filters for stage, skill, and severity, with timestamps and links to affected artifacts. Make failures and missing inputs actionable by showing the command, check, or decision that needs attention where that information is available.

Keep offline conformance, simulation, live browser tests, and production verification visibly distinct. Show each suite’s environment, pass/fail count, skipped checks, and report link. A passing SDK suite must not imply that an external integration works end to end.

## First working version

Build one vertical slice with an existing project, such as Port 0 Companion if it is available:

1. Open the project and load its PRD, architecture, decisions, and visual review.
2. Start or resume a builder run and display the full proposed draft.
3. Show the current design layer, diagrams, and skills used.
4. Ask a question, persist the pending request, and accept a user answer.
5. Record an explicit layer approval and restore the same state after a refresh.
6. Show the generation gate and the existing SDK test report.
7. Demonstrate a skill failure and show how the engineer inspects its log and retries where supported.

Use the repository’s existing stack if it has one. If it does not, choose a small maintainable web stack with a typed frontend, a server-side builder adapter, and local persistence. Favor existing Markdown and structured reports over migrating them into a new system. Keep the application runnable locally with clear setup instructions and no paid service required for the fixture demonstration.

Deliver the working IDE, instructions to run it, and a short verification report. Test the normal path and the failure paths that matter most: refresh while waiting for input, a stale or duplicate answer, a skill failure, and an attempt to generate with an open review layer. Include the exact files or endpoints where the real builder can be connected if the first version uses fixtures.
