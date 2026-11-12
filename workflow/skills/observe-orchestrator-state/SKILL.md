---
name: observe-orchestrator-state
description: Visualize state transitions in an agent orchestrator from runtime events, checkpoints, or a reference state model. Use to inspect routing, task lifecycle, and stuck or invalid transitions.
---

# Observe Orchestrator State

Scope the view to the requested run, session, or task. Read the governing state definitions and match runtime events or checkpoints to them. Identify the host and in-agent coordinator separately when both have state. Show the current state only when the evidence supports it.

- Use a Mermaid state diagram for the allowed transitions. For an observed run, show the actual path as an ordered timeline with event time or sequence, triggering event, previous and next state, and owning component.
- Highlight repeated transitions, invalid edges, stale checkpoints, and tasks that entered a wait state without a recorded exit. Distinguish a state still waiting at the end of the capture from a confirmed timeout or fault.
- Report the last confirmed state and source reference for each task in scope. If timestamps disagree across components, prefer causal IDs or explicit sequence numbers and label unresolved ordering.
- When given only the design, show the expected state model and identify the runtime evidence needed to observe it.

Use existing read-only evidence. Keep identifiers scoped to the selected run and omit secrets, raw payloads, and personal data from the visual. For an interactive view, expose source references on selection so the engineer can verify the sequence.

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
