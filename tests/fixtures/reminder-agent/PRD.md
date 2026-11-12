# Sample PRD · Personal Reminder Agent

**Audience:** People who want to manage their own reminders through conversation.  
**Assignment:** One illustrative personal-reminder port on a host that provides scoped reads, governed actions, and scheduled delivery. Bind this fixture to a real SDK before generation.

## User goals

| ID | Requirement | Acceptance example |
| --- | --- | --- |
| R1 | Create a one-time reminder with a message and future date and time in the user's time zone. | “Remind me to water the plants tomorrow” prompts for the time. After the user supplies it and the host confirms creation, the agent reports when it is due. |
| R2 | List upcoming reminders owned by the user. | “What reminders do I have?” returns upcoming items in due-time order or says there are none when the authorized query returns an empty list. |
| R3 | Cancel an upcoming reminder. | “Cancel my plant reminder” asks which one when several match. The agent reports cancellation after the selected item is cancelled. |
| R4 | Preserve progress while waiting for a reply when the host permits resumption. | A resumed creation asks for the missing time and retains the reminder message. A cancelled draft creates nothing. |
| R5 | Deliver a reminder at its scheduled time under host delivery policy. | A successfully created reminder remains scheduled after the agent session ends. |
| R6 | Report whether a requested change succeeded, failed, or is still unresolved. | A timeout after submission does not produce a success message or a second reminder. |

Recurring reminders, medical schedules, and reminders for other people are outside this example's scope.

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
