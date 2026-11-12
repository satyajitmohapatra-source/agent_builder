---
name: trace-function-calls
description: Visualize a function, tool, or service call chain from runtime spans or structured logs. Use to follow nested and concurrent calls, inspect retries and failures, and identify latency.
---

# Trace Function Calls

Scope to a named run, turn, action, or trace. Prefer parent and child span IDs or explicit call relationships. Correlate logs using stable IDs, and mark unmatched calls and inferred edges. Treat a static call graph as a separate view of possible calls.

- Use a call tree for nesting and a timeline or waterfall when timestamps support it. Show call names, start and end or duration, outcomes, retries, and correlation IDs. Use redacted input and output summaries only when needed to explain the behavior.
- Preserve concurrency and distinguish missing ends from confirmed timeouts. Flag the slowest recorded calls and identify the critical path only when causal and timing evidence is sufficient. Avoid double-counting overlapping spans.
- Separate tool invocation, action proposal, authorized execution, and reconciliation when those appear as different calls. A retried call does not by itself establish a duplicate effect.
- If instrumentation is incomplete, show the confirmed chain and name the missing spans or fields. Use a static diagram for code-only analysis and label it as such.

Use existing read-only evidence. Keep identifiers scoped to the selected run and omit secrets, raw payloads, and personal data from the visual. For an interactive view, expose source references on selection so the engineer can verify the sequence.

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
