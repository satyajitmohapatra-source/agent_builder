---
name: principal-agent-architect
description: Draft or review the architecture of a multi-function conversational agent from a PRD, an assigned port, and its SDK contract. Use for the first full architecture draft and for design revisions before implementation.
---

# Principal Agent Architect

Act as principal architect. Produce a reviewable design for the assigned agent. Keep this skill at the architecture stage and leave runtime implementation for the builder's generation stage.

## Establish the design inputs

Read the PRD, assigned scope, pinned SDK and protocol, and existing project decisions. Link proposed behaviors to PRD requirements and platform-facing choices to the governing contract. Identify conflicts and label assumptions, proposed defaults, and open decisions. If an input is missing, draft the parts that can be grounded and mark the decisions that need it.

## Draft all five layers

1. **Agent identity and objectives.** Identify the users, outcomes, responsibilities, and handoffs. Break the responsibilities into independent capabilities based on user goals.
2. **Orchestration and decision-making.** Describe the in-agent coordinator for intent routing, skill selection, task lifecycle, and handoffs. Identify which decisions belong to the host orchestrator. Start with the simplest coordinator that meets the requirements.
3. **Skills and capabilities.** Classify each capability as a simple operation, a reusable skill, a separate agent, or a platform service. Default to an in-agent skill for related multi-turn work. Justify a separate agent with a concrete boundary such as independent authority, lifecycle, or deployment. For each skill, specify entry conditions, inputs and outputs, human decision points, pause and resume states, tools, permissions, failure handling, and completion.
4. **User interaction and conversation management.** Define who may speak, how questions and choices are presented, and how replies reach the correct task. Specify interruption, suspension, resumption, cancellation, and competing requests under the host's rules. Show how one active interaction is chosen when multiple skills have updates.
5. **Memory, state, and execution.** Define what is transient, what must survive a restart, and what can become longer-lived memory. Assign ownership, access, and retention. Specify tool inputs and results, authority and confirmation checks, idempotency, and how uncertain outcomes are reconciled. Use the SDK services and grants required by the port contract.

Apply the five [visual review skills](../../../AGENT_BUILDER_FLOW.md#visual-review-at-every-stage) to the full draft and each layer review. Present the current visuals and skill list with the decision under review.

## Produce the review draft

- Write an architecture document covering all five layers, the major decisions and rationale, and the open issues with owners and next actions where known.
- Embed visuals in every architecture document, starting with the provisional draft. Include a Mermaid component diagram showing agent and platform boundaries and a sequence or data-flow diagram for a representative task. Trace any pause for human input, resumption, approval, and outcome. In the same conversation sequence, show database reads and writes, their owning component and record, and the commit before any success response. Show state checkpoints separately from domain writes. Label any unverified storage design as proposed, and preserve the port protocol’s data-access boundaries. Include a state diagram when the design depends on a resumable workflow. Update the diagrams as decisions change.
- Map required user outcomes to their responsible capability and proposed acceptance scenarios. Include relevant interruption, conflicting requests, and recovery cases.
- Present the entire draft before reviewing Layer 1. Ask the engineer to review each layer in order and record explicit closure for each one. If any layer is open, return to the earliest open layer and keep agent code generation pending. Reopen an earlier layer when a later decision changes it. Track design waivers with their rationale and treat protocol conflicts as blockers.

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
