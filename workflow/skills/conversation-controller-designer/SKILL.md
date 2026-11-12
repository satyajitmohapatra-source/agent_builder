---
name: conversation-controller-designer
description: Design or review a central conversation controller for multi-skill agents. Use for turn ownership, voice arbitration, background events, task switching, or duplicate response prevention under a host protocol.
---

# Conversation Controller Designer

Use the PRD, approved skill contracts, and pinned port protocol to draft the controller design. Start with the smallest controller that can enforce ownership and route replies reliably. Keep implementation for the builder's generation stage.

## Define ownership and arbitration

- Assign one active conversational turn to one owner. Skills may perform permitted work concurrently and return results or requests to interact. All speech and microphone control go through the interaction boundary and the host's voice controls. Skills have no direct microphone or speaker access.
- Specify who grants and releases the turn and how the controller correlates a reply to the active task and question. Distinguish the agent's choice of a skill from the host's authority to listen or speak. Treat a task waiting for an answer as distinct from active playback.
- Define a deterministic decision policy for simultaneous candidates, including which requests are eligible, the tie-breaker, and whether each is queued, deferred, coalesced, or dropped. Use the host's speaking opportunities, interruption, safety, and expiry rules. Derive scheduling from the protocol before using event severity as a scheduling input.
- Route background results and events through host-approved ingress or internal state updates. Specify when an event can request user interaction and what happens when the session is busy or offline.

## Design task lifecycle and recovery

- Specify how to tell an answer from an unrelated request, a task switch, or a cancellation. Handle ambiguous replies without advancing the wrong task. Apply host limits on open tasks and on switching or resuming them.
- Define when a task can be suspended, what it checkpoints, and how it resumes with its pending question or a refreshed choice. State what happens after timeout, disconnect, cancellation, or expiry. Explain how late results are handled when their task has changed owners or closed.
- Assign stable correlation and deduplication identities to incoming events, turns, and intended responses. Specify where the design checks duplicates and records the response decision, including concurrent processing and restarts. Distinguish a replayable response record from playback acknowledgement. Describe recovery when delivery is uncertain using the host's guarantees.

## Produce the design for review

1. Write an ownership map and arbitration table with triggers, eligibility, ordering, and decisions for conflicts.
2. Include Mermaid state diagrams for the conversation turn and the task lifecycle. Show where the two interact and which transitions the host owns.
3. Define event schemas for the interactions the design uses, such as a user turn, skill interaction request, background result, task-control command, and response delivery receipt. For each, identify its producer, consumer, required fields, and correlation or deduplication identity. Map platform-facing events to the existing protocol and mark agent-internal events as such.
4. Provide test scenarios for competing skill responses, a background event during speech, a task switch and resume, ambiguous or stale replies, cancellation followed by a late result, and duplicate input or delivery callbacks. For each, state the expected owner, state transition, and number of effective responses. Include recovery after restart or uncertain playback when supported.
5. Record assumptions, unresolved protocol or product decisions, and any changes needed in the orchestration, conversation, or state layers.

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
