# Review record

**Resume point:** Layer 5 is in review. Close it explicitly before moving to generation readiness.

| Layer | Status |
| --- | --- |
| 1. Agent identity and objectives | Closed |
| 2. Orchestration and decision-making | Closed |
| 3. Skills and capabilities | Closed |
| 4. User interaction and conversation management | Closed |
| 5. Memory, state, and execution | In review |

## Layer 1 decision

The agent helps people create, list, and cancel their own one-time reminders. Scheduled delivery belongs to the host. Recurring reminders, medical schedules, and reminders for other people are outside scope. These boundaries come from the PRD. The reviewer approved this scope.

## Layer 2 decision

Use one agent with a small turn coordinator. When the host routes a turn to this agent, the coordinator handles an allowed cancellation or a reply to the active task, then routes eligible new requests to create, list, or cancel. Clarify an ambiguous reply before advancing a task or proposing a change. The host controls cross-port routing, access to the speaking floor, and whether an unrelated request can be handled while a task is open.

This keeps one coordinator for three closely related capabilities. The pinned SDK will determine exact open-task and handoff behavior. The reviewer approved the single-agent coordinator.

## Layer 3 decision

- **Create reminder (R1, R4, R6).** Use a resumable skill. Collect the message and time, clarify missing details, and propose creation. Complete after a confirmed creation result.
- **List reminders (R2).** Use a scoped read operation. Return upcoming reminders in due-time order.
- **Cancel reminder (R3, R4, R6).** Use a resumable skill. Resolve the intended reminder, ask the user to choose when multiple reminders match, and propose cancellation. Complete after a confirmed cancellation result.
- **Scheduled delivery (R5).** The host scheduler owns delivery and its outcome records.

Create and cancel each have their own contract and acceptance scenarios. The pinned SDK will determine the concrete read and action interfaces. The reviewer approved this capability split.

## Layer 4 decision

The agent can ask for all missing details in one turn. For example, “What should I remind you about, and when?” Keep track of the fields requested for the active task. Accept a partial answer, save the valid details, and follow up only on fields still missing or ambiguous. Ask for clarification if a reply could refer to multiple reminders. When the host allows resumption, restore the draft and ask only for what is still needed. An explicit cancellation can abandon an unsubmitted draft. For an unrelated request, follow the host's task-switching policy.

The host owns the speaking floor and any required action confirmation. Selecting a reminder identifies the target for cancellation. The configured response path reports success after the host confirms the action outcome. The exact interruption, timeout, and confirmation rules remain open until the target SDK is pinned.

The reviewer approved this interaction model, including asking for all missing details in one turn and retaining partial answers.

## Layer 5 proposal

- **Task state.** Save the active skill, validated draft details, fields still needed, and any action reference through the host SDK. Restore the draft when the host permits resumption. Revalidate dates and selections that may have become stale.
- **Memory.** The host reminder service stores the scheduled reminders. This example needs no long-term conversational memory.
- **Execution.** Propose creation or cancellation through the host and use a stable action key for the intended change. If the outcome is uncertain, check the existing action before retrying. Report success only once the host confirms the change.

The project targets Chotu Port 2 using SDK `v0.3.0-dev.9` and contract `0.2`. Use `ctx.task` for the draft, `ctx.now` for relative times, and `ctx.actions.propose()` and `ctx.actions.status()` for governed changes and their results. The host owns confirmation and execution. The exact reminder read and action payloads still need verification. Layer 5 is pending review.

## Open issues

| Issue | Affects | Owner | Next action |
| --- | --- | --- | --- |
| Confirm host support for personal-reminder reads and writes. | Layers 3–5 and generation | Engineer and platform owner | The SDK declares `reminder.read` but exposes no typed personal-reminder read. Verify how list and cancel target resolution are supported, plus the host payloads and execution for `personal.reminder.create` and `personal.reminder.cancel`. |
| Verify when an unfinished draft can resume or expires. | Layers 4–5 | Engineer and platform owner | Check the host lifecycle and refine R4 acceptance tests. |

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
