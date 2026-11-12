---
name: skill-framework-designer
description: Design a reusable framework and independently testable contracts for conversation-aware runtime skills in a multi-function agent. Use when defining skill interfaces, human input checkpoints, or interruption and resumption behavior.
---

# Skill Framework Designer

Read the PRD, reviewed architecture, and pinned port protocol. Design at the contract level. Use the [skill contract template](references/skill-contract.md) for each skill and the [worked examples](references/examples.md) when illustrating the framework. Treat example policy and tools as illustrative.

1. Group requirements by user outcome. Give each skill a clear activation boundary, typed inputs and outputs, and explicit dependencies that can be replaced by test doubles. Document overlap and handoff with other skills.
2. Define a common interaction contract. On each invocation, a skill receives the relevant input and saved state and returns an updated state with a next step, such as asking a question, presenting options, requesting a tool operation, or reporting an outcome. The agent coordinates user interaction and the host governs permissions, confirmation, execution, and lifecycle where the protocol assigns those duties.
3. Define state transitions for missing information, user choices, and any required approval. Persist the minimum needed to resume, including the workflow stage, validated inputs, the expected reply, and relevant action references. On resume, recheck stale options and unresolved operations. Prevent duplicate effects after repeated replies, callbacks, or restarts.
4. Define cancellation, interruption, timeouts, permission denial, and known versus uncertain outcomes. Separate cancellation of an unfinished interaction from any authorized reversal of a committed action.
5. Provide test scenarios for each skill using scripted turns, a replaceable state store or fixture, and test doubles for its declared dependencies. Include a save-and-reload test at each kind of human input checkpoint and tests for the failure and interruption paths that apply.

Deliver the shared framework, a reusable contract template, and two worked skill contracts. If the PRD supplies suitable capabilities, use two of those for the examples. Record protocol conflicts and unresolved product choices for engineer review.

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
