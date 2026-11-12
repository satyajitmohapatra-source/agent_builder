# Conversation-aware skill contract template

| Field | Define |
| --- | --- |
| **Name and purpose** | Stable skill ID, user outcome, scope, and PRD requirements. |
| **Activation conditions** | Entry intents or events, prerequisites, exclusions, and handoff conditions. |
| **Input schema** | Field names, types, required fields, validation, and trusted sources. Distinguish partially collected inputs from validated execution inputs. |
| **Output schema** | Typed intermediate and terminal outcomes, required result fields, and failure information. |
| **Required context** | Trusted identity or session context, locale and time zone if relevant, and scoped records. |
| **Conversation workflow** | Steps from entry to outcome, including questions, choices, confirmation, and result communication. |
| **Questions** | When each question is asked, what answer it accepts, and how ambiguous answers are handled. |
| **State transitions** | Current state, triggering event, guard, next state, emitted result, and what must be saved. Identify every human input checkpoint. |
| **Tool dependencies** | Each tool's typed request and response, side effects, failure modes, and test double. |
| **Permissions and confirmation** | Required grants, confirmation owner, and what approval covers. Distinguish selecting an option from authorizing an action. |
| **Error handling** | Validation errors, denials, timeouts, duplicate delivery, and uncertain execution. Specify what the skill reports and how it checks or retries. |
| **Cancellation and interruption** | When the skill can suspend, abandon a draft, resume, or hand off. Describe what happens if an action is already pending or committed. |
| **Resume behavior** | Checkpoint key and scope, saved fields, expiry, validity checks, and how the skill restores the pending question or checks an action result. |
| **Completion criteria** | Evidence required for success and terminal conditions for cancellation, expiry, or failure. |
| **Independent tests** | Scripted inputs and expected transitions, checkpoint round trips, and assertions on tool calls and user-facing outcomes. |

Use a transition table when the skill has multiple wait states.

| From | Event and guard | To | Effect and checkpoint |
| --- | --- | --- | --- |
| Awaiting input | Valid reply matches the pending question | Next workflow state | Save validated input and clear the pending question. |

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
