# Agent Builder IDE

Run from the Agent Builder workspace with Python 3.10 or newer.

```sh
python3 ide/server.py
```

Open [the local IDE](http://127.0.0.1:8765/). Use `--port` to change the port or `--db` to choose another SQLite file. By default, IDE run state is stored in `ide/.state/runs.sqlite3`. Mermaid previews require access to the pinned CDN dependency. Diagram source remains available if the renderer cannot load.

Select Companion or Reminder. Open the project files and visual review, then select **Start or resume run** and **Begin layer review**. Answer the pending question and approve the layer explicitly. To exercise recovery, expand **Skills**, select **Simulate skill failure**, inspect the log, and select **Retry skill**.

The project artifacts, skill definitions, and stored conformance reports come from the workspace. Run conversation, revision requests, approvals, and skill execution are fixture interactions saved separately in SQLite. Companion has an architecture and decision record. The Reminder project also has a standalone PRD. Fixture generation stays blocked even when all five fixture approvals are recorded.

## Connect the builder

In `server.py`, replace `FixtureBuilder` at `Workspace.builder` with an adapter for the real builder runtime. The current entry points are `start(project)` and `apply(run, project, data)`. Keep approval and revision checks on the server before enabling generation. Run actions enter through `POST /api/run?project=...`, project state through `GET /api/project?project=...`, and events through `GET /api/events?project=...&after=...`. The event stream uses monotonic sequence IDs for reconnects. A real adapter must provide authoritative blocker status and emit actual skill, artifact, and verification events.

## Verification

- Opened the IDE in the Codex browser and verified project navigation, the companion architecture, diagram entries, and the stored 12-check offline SDK report were visible.
- Exercised the HTTP API with an isolated SQLite database. Verified pending-question recovery, stale and duplicate answer rejection, rejection of approval before an answer, explicit approval persistence and advancement, generation rejection with open layers, fixture skill failure and retry, and event delivery.
- Interactive Mermaid expansion and a real model-backed builder run remain unverified.
