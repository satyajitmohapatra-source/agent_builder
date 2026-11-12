# Port 2 evaluation

**Target:** Chotu SDK v0.3.0-dev.9, contract 0.2, Port 2 (Daily Life). The prototype is English-only and accepts today or tomorrow with explicit clock times.

| Check | Result |
| --- | --- |
| SDK offline conformance | Passed all 12 checks executed by this SDK version. |
| Focused SDK harness tests | Four passed. Covered draft restart, host confirmation, duplicate turn replay, partial input, draft cancellation, and honest responses when reminder lookup is unavailable. |
| Production reminder creation | Unverified. The mock records one approved action. The host domain payload and persistent write still need integration verification. |
| Listing and cancelling scheduled reminders | Blocked on the typed host reminder read and cancellation integration. The prototype reports lookup as unavailable. |
| Scheduled delivery and production recovery | Unverified. No database or scheduler was exercised. |

## Host smoke test readiness

Checked the two upstream Chotu branches available on 2026-11-12. Both declare Port 2's reminder grants. Both still expect `SERVICE_UNAVAILABLE` for a create proposal and lack a personal-reminder domain implementation in the inspected backend and migrations. The pinned SDK lacks a typed personal-reminder read.

- [Chotu main gate test at 1f3285e](https://github.com/KingSardine/Chotu/blob/1f3285ed4f0c468d1a3122a28f26ae95b748af04/backend/tests/test_gate.py#L187)
- [Chotu phase-d gate test at a0443ca](https://github.com/KingSardine/Chotu/blob/a0443ca74ace395ccd5fe19fa8db4762488fa3d0/backend/tests/test_gate.py#L187)
- [Pinned SDK data interface](/home/user/projects/chotu-sdk/src/chotu_agent_sdk/services.py:65)

**Result:** The create, list, cancel, and scheduled-delivery smoke tests were not run. Resume with a host revision that provides reminder persistence, a scoped read, working create and cancel handlers, and a delivery path. Run against an isolated test database and scheduler.

With the pinned SDK and test dependencies installed, run these from the reminder project:

```sh
python -m pytest -q -o asyncio_default_fixture_loop_scope=function port_2/tests
chotu-agent conformance port_2 --no-db --log-dir verification/conformance-run
```

Layer 5 remains in review. This prototype exercises the approved conversation behavior and the SDK boundary.

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
