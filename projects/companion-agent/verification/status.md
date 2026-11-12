# Port 0 evaluation

SDK v0.3.0-dev.9, draft contract 0.2, offline host harness. These results apply to the existing prototype. Design approval is pending in the [review record](../design/decisions.md).

- Conformance passed all 12 checks executed by this SDK build, including the story dialogue with traffic.
- Three focused tests passed for story continuation after a harness restart and turn replay, stopping the story, and accepting a greeting's story invitation.
- Running the companion and reminder focused suites together passed all seven tests.
- The prototype uses one original English story and scripted follow-ups. It requests no data scopes or actions. This run did not exercise live voice, the production host, or a database.

From this project, with the pinned SDK and test dependencies installed:

```sh
python -m pytest -q -o asyncio_default_fixture_loop_scope=function port_0/tests
chotu-agent conformance port_0 --no-db --log-dir verification/conformance-run
```

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
