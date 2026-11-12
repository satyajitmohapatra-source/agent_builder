"""Local Agent Builder IDE and fixture runtime."""
import argparse
import hashlib
import json
import mimetypes
import re
import sqlite3
import time
from contextlib import closing
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

LAYERS = (
    "Identity and objectives", "Orchestration and decision-making",
    "Skills and capabilities", "Interaction and conversation management",
    "Memory, state, and execution",
)
STATIC = Path(__file__).resolve().parent / "static"
ALLOWED_SUFFIXES = {".md", ".json", ".py", ".yaml", ".html", ".js", ".css"}
VISUAL_SKILL = "draw-system-blocks"


def artifact_files(project):
    return {
        p.relative_to(project).as_posix(): p
        for p in sorted(project.rglob("*"))
        if p.is_file() and p.suffix in ALLOWED_SUFFIXES
        and not any(part.startswith(".") for part in p.relative_to(project).parts)
        and p.resolve().is_relative_to(project.resolve())
    }


def read_artifact(path):
    if path.stat().st_size > 1_000_000:
        raise ValueError("Artifact exceeds the preview size limit.")
    return path.read_text(encoding="utf-8")


def revision(project):
    digest = hashlib.sha256()
    for name in ("design/architecture.md", "design/decisions.md", "design/visual-review.md"):
        path = artifact_files(project).get(name)
        if path:
            digest.update(name.encode())
            digest.update(read_artifact(path).encode())
    return digest.hexdigest()


def event(run, kind, message, **details):
    run["events"].append({
        "seq": len(run["events"]) + 1,
        "time": datetime.now(timezone.utc).isoformat(),
        "kind": kind, "message": message, "stage": run["stage"], **details,
    })


class FixtureBuilder:
    """Replace with a runtime adapter that emits the same run events."""

    def start(self, project):
        run = {"id": uuid4().hex, "project": project.name, "stage": 0, "pending": None,
               "approvals": [], "events": [], "skill": None, "mode": "fixture"}
        event(run, "assistant", "Review the full architecture draft before opening Layer 1.")
        event(run, "artifact", "Architecture draft available.", path="design/architecture.md")
        return run

    def ask(self, run, current_revision):
        run["pending"] = {"id": uuid4().hex, "revision": current_revision, "answer": None}
        layer = LAYERS[run["stage"] - 1]
        event(run, "question", f"What should we keep or revise for {layer.lower()}?")

    def apply(self, run, project, data):
        action = data.get("action")
        current = revision(project)
        pending = run["pending"]
        if action == "begin" and run["stage"] == 0:
            if data.get("revision") != current:
                raise ValueError("The draft changed. Reload it before starting review.")
            run["stage"] = 1
            self.ask(run, current)
        elif action in {"answer", "approve", "revision"}:
            if not pending or data.get("requestId") != pending["id"]:
                raise ValueError("This question is no longer current.")
            if data.get("revision") != current or pending["revision"] != current:
                raise ValueError("The artifacts changed. Refresh the review before responding.")
            if action == "answer":
                answer = data.get("text")
                if pending["answer"] is not None or not isinstance(answer, str) or not answer.strip():
                    raise ValueError("Enter an answer to an unanswered question.")
                pending["answer"] = answer.strip()[:4000]
                event(run, "user", pending["answer"])
                event(run, "assistant", "Answer recorded. Review the proposed outcome and approve explicitly.")
            elif action == "revision":
                note = data.get("text")
                if not isinstance(note, str) or not note.strip():
                    raise ValueError("Describe the requested revision.")
                event(run, "user", note.strip()[:4000])
                event(run, "assistant", "Revision requested in fixture mode. The project files require a real builder revision.")
                run["pending"] = None
                run["needsRevision"] = current
            else:
                if pending["answer"] is None:
                    raise ValueError("Answer the review question first.")
                run["approvals"].append({"layer": run["stage"], "revision": current,
                                         "answer": pending["answer"], "requestId": pending["id"]})
                event(run, "approval", f"Layer {run['stage']} approved for revision {current[:12]}.")
                run["pending"] = None
                run["stage"] += 1
                if run["stage"] <= len(LAYERS):
                    self.ask(run, current)
                else:
                    event(run, "assistant", "Layer review complete. Check generation readiness.")
        elif action == "refresh":
            if not 1 <= run["stage"] <= len(LAYERS) + 1:
                raise ValueError("No layer is in review.")
            if run.get("needsRevision") == current:
                raise ValueError("Update the project artifacts before reopening the decision.")
            if pending and pending["revision"] == current:
                raise ValueError("The review already uses the current artifact revision.")
            run.pop("needsRevision", None)
            stale = next((a["layer"] for a in run["approvals"] if a["revision"] != current), None)
            if stale is not None:
                run["approvals"] = [a for a in run["approvals"] if a["layer"] < stale]
                run["stage"] = stale
            if run["stage"] > len(LAYERS):
                raise ValueError("All current layers are approved.")
            self.ask(run, current)
        elif action in {"fail_skill", "retry_skill"}:
            if action == "retry_skill" and run["skill"] != "failed":
                raise ValueError("There is no failed skill to retry.")
            event(run, "skill_start", "Started fixture visual review.", skill=VISUAL_SKILL)
            failed = action == "fail_skill" or not (project / "design/visual-review.md").is_file()
            run["skill"] = "failed" if failed else "passed"
            event(run, "error" if failed else "skill_finish",
                  "Fixture failed while loading visual evidence. Use Retry skill."
                  if failed else "Fixture loaded the existing visual review.",
                  skill=VISUAL_SKILL, path="design/visual-review.md")
        elif action == "generate":
            if len(run["approvals"]) != len(LAYERS):
                raise ValueError("Generation blocked. All five layers require explicit approval.")
            if any(a["revision"] != current for a in run["approvals"]):
                raise ValueError("Generation blocked. Approvals refer to an older artifact revision.")
            raise ValueError("Generation blocked. Fixture mode has no verified blocker resolution or code generator.")
        else:
            raise ValueError("That action is unavailable at this stage.")


class Workspace:
    def __init__(self, root, database):
        self.root = root.resolve()
        self.database = database
        self.builder = FixtureBuilder()
        database.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as db:
            db.execute("CREATE TABLE IF NOT EXISTS runs (project TEXT PRIMARY KEY, data TEXT NOT NULL)")
            db.commit()

    def connect(self):
        return sqlite3.connect(self.database, timeout=10)

    def projects(self):
        directory = self.root / "projects"
        return {p.name: p for p in sorted(directory.iterdir())
                if p.is_dir() and p.resolve().is_relative_to(directory.resolve())
                and (p / "design/architecture.md").is_file()}

    def get_run(self, project):
        with closing(self.connect()) as db:
            row = db.execute("SELECT data FROM runs WHERE project=?", (project.name,)).fetchone()
        return json.loads(row[0]) if row else None

    def change(self, project, data):
        with closing(self.connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT data FROM runs WHERE project=?", (project.name,)).fetchone()
            if data.get("action") == "start":
                if row:
                    return json.loads(row[0])
                run = self.builder.start(project)
            else:
                if not row:
                    raise ValueError("Start a run first.")
                run = json.loads(row[0])
                if data.get("runId") != run["id"]:
                    raise ValueError("This run is no longer current.")
                self.builder.apply(run, project, data)
            db.execute("INSERT OR REPLACE INTO runs VALUES (?,?)", (project.name, json.dumps(run)))
            return run

    def skills(self):
        result = []
        base = self.root / "workflow/skills"
        for path in sorted(base.glob("*/SKILL.md")):
            if not path.resolve().is_relative_to(base.resolve()):
                continue
            source = read_artifact(path)
            description = re.search(r"^description:\s*(.+)$", source, re.M)
            result.append({"id": path.parent.name, "description": description[1] if description else "",
                           "source": source})
        return result


class Handler(BaseHTTPRequestHandler):
    def respond(self, value, code=200, content_type="application/json"):
        body = json.dumps(value).encode() if content_type == "application/json" else value
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def route(self):
        url = urlsplit(self.path)
        params = {k: v[0] for k, v in parse_qs(url.query).items()}
        return url.path, params

    def local_request(self):
        allowed = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        if self.headers.get("Host") not in allowed:
            self.respond({"error": "Open the IDE through its loopback URL."}, 403)
            return False
        return True

    def do_GET(self):
        if not self.local_request():
            return
        path, params = self.route()
        workspace = self.server.workspace
        if path in {"/", "/app.js", "/style.css"}:
            file = STATIC / ("index.html" if path == "/" else path[1:])
            self.respond(file.read_bytes(), content_type=mimetypes.guess_type(file)[0])
            return
        projects = workspace.projects()
        if path == "/api/workspace":
            self.respond({"projects": list(projects), "skills": workspace.skills(), "layers": LAYERS})
            return
        project = projects.get(params.get("project"))
        if project is None:
            self.respond({"error": "Project not found."}, 404)
            return
        files = artifact_files(project)
        if path == "/api/project":
            self.respond({"files": list(files), "revision": revision(project), "run": workspace.get_run(project)})
        elif path == "/api/artifact" and params.get("path") in files:
            try:
                self.respond({"text": read_artifact(files[params["path"]])})
            except (ValueError, OSError) as exc:
                self.respond({"error": str(exc)}, 400)
        elif path == "/api/events":
            try:
                cursor = max(int(params.get("after", "0")), int(self.headers.get("Last-Event-ID", "0")))
            except ValueError:
                self.respond({"error": "Invalid event cursor."}, 400)
                return
            for _ in range(20):
                run = workspace.get_run(project)
                events = [e for e in (run or {}).get("events", []) if e["seq"] > cursor]
                if events:
                    break
                time.sleep(.25)
            body = "".join(f"id: {e['seq']}\ndata: {json.dumps(e)}\n\n" for e in events)
            self.respond(("retry: 500\n\n" + body).encode(), content_type="text/event-stream")
        else:
            self.respond({"error": "Artifact or endpoint not found."}, 404)

    def do_POST(self):
        if not self.local_request():
            return
        path, params = self.route()
        origin = self.headers.get("Origin")
        if (origin and origin != f"http://{self.headers.get('Host')}") or (
            self.headers.get_content_type() != "application/json"
        ):
            self.respond({"error": "Use a same-origin JSON request."}, 403)
            return
        workspace = self.server.workspace
        project = workspace.projects().get(params.get("project"))
        if path != "/api/run" or project is None:
            self.respond({"error": "Endpoint or project not found."}, 404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 16_384:
                raise ValueError("Invalid request size.")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object.")
            self.respond(workspace.change(project, data))
        except ValueError as exc:
            self.respond({"error": str(exc)}, 409)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--db", type=Path)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    workspace = Workspace(args.root, args.db or args.root / "ide/.state/runs.sqlite3")
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        server.workspace = workspace
        print(f"Agent Builder IDE at http://127.0.0.1:{args.port}", flush=True)
        server.serve_forever()
