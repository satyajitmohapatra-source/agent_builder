---
name: observe-conversation-flow
description: Visualize a conversation across user turns, agent replies, skill handoffs, and background events. Use to inspect turn ownership, pauses, interruptions, and delivery.
---

# Observe Conversation Flow

Scope the view to one conversation or a named segment. Reconstruct it from authorized, redacted transcripts, turn events, and delivery receipts. Link tasks, actions, and events to their turns using correlation IDs when available.

- Draw a Mermaid sequence diagram or an interactive timeline with lanes for the user, host, agent, and relevant skills or services. Show the current turn owner, questions and replies, task waits, handoffs, interruption or deferral, and resumption.
- Distinguish proposed, queued, sent, played, and acknowledged responses when the source records these separately. Mark missing delivery evidence as unknown.
- Flag ambiguous reply routing, overlapping speaking intervals, duplicate responses, and tasks left waiting. Include the relevant turn or event ID for inspection.
- If only a scripted dialogue or design is available, label the flow as simulated or expected and identify what runtime evidence would confirm it.

Use existing read-only evidence. Keep identifiers scoped to the selected run and omit secrets, raw payloads, and personal data from the visual. For an interactive view, expose source references on selection so the engineer can verify the sequence.

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
