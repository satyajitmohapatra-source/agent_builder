"use strict";

/** @typedef {{seq:number, time:string, kind:string, message:string, stage:number, skill?:string, path?:string}} RunEvent */
/** @typedef {{id:string, revision:string, answer:string|null}} PendingQuestion */
/** @typedef {{id:string, stage:number, pending:PendingQuestion|null, approvals:{layer:number,revision:string}[], events:RunEvent[], skill:string|null}} Run */
const el = id => document.getElementById(id);
const query = params => new URLSearchParams(params).toString();
const stages = ["PRD intake and draft"];
let project = "";
let revision = "";
/** @type {Run|null} */
let run = null;
let stream;
let reviewNotes = "";
let busy = false;
let diagramsLoaded = false;
let previewToken = 0;

async function api(path, params = {}, payload) {
  const response = await fetch("/api/" + path + "?" + query(params), payload ? {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload),
  } : undefined);
  const value = await response.json();
  if (!response.ok) throw new Error(value.error);
  return value;
}

function node(tag, text) {
  const result = document.createElement(tag);
  result.textContent = text;
  return result;
}

function option(select, value, label) {
  const item = node("option", label);
  item.value = value;
  select.append(item);
}

function button(label, click) {
  const result = node("button", label);
  result.type = "button";
  result.addEventListener("click", click);
  return result;
}

function artifactButton(path) {
  return button(path, () => preview(path).catch(showError));
}

function showError(error) {
  el("error").textContent = error.message;
}

async function preview(path) {
  const token = ++previewToken;
  const data = await api("artifact", {project, path});
  if (token !== previewToken) return;
  el("artifact-title").textContent = path;
  el("artifact").textContent = data.text;
  el("artifact-panel").open = true;
}

function render() {
  const stage = run ? run.stage : 0;
  el("stage").textContent = stages[stage];
  el("workflow").replaceChildren(...stages.map((name, index) => {
    const status = index === stage ? (run?.pending?.answer == null && run?.pending ? "Waiting for input" : "Active")
      : index < stage ? (index ? "Approved" : "Reviewed") : "Pending";
    return node("li", name + " · " + status);
  }));
  el("start").hidden = Boolean(run);
  el("begin").hidden = !run || stage !== 0;
  el("generate").hidden = !run;
  el("refresh").hidden = !run || stage === 0 ||
    (!run.needsRevision && (!run.pending || run.pending.revision === revision) &&
      run.approvals.every(approval => approval.revision === revision));
  el("decision").hidden = !run?.pending;
  const section = reviewNotes.split(new RegExp("^## Layer " + stage + " (?:proposal|decision).*\\n", "m"))[1];
  el("proposal").textContent = section?.split(/^## |^---$/m)[0].trim() || "Review the architecture draft and the visual evidence for this layer.";
  const answered = run?.pending?.answer != null;
  el("send").disabled = busy || answered;
  el("keep").disabled = busy || answered;
  el("approve").disabled = busy || !answered;
  el("revise").disabled = busy;
  for (const id of ["start", "begin", "refresh", "generate", "fail-skill"]) {
    el(id).disabled = busy || (id === "fail-skill" && !run);
  }
  el("retry-skill").disabled = busy || run?.skill !== "failed";
  const messages = (run?.events || []).filter(e => ["assistant", "question", "user", "approval"].includes(e.kind));
  el("conversation").replaceChildren(...messages.map(e => node("p", e.kind + " · " + e.message)));
  const skillEvents = (run?.events || []).filter(e => e.skill);
  el("skill-runs").replaceChildren(...skillEvents.map(e => {
    const row = node("p", e.skill + " · " + e.message);
    if (e.path && !["error"].includes(e.kind)) row.append(" ", artifactButton(e.path));
    return row;
  }));
  renderLogs();
}

function renderLogs() {
  const stage = el("log-stage").value;
  const skill = el("log-skill").value;
  const severity = el("log-severity").value;
  const entries = (run?.events || []).filter(e => (!stage || String(e.stage) === stage) &&
    (!skill || e.skill === skill) && (!severity || (e.kind === "error" ? "Error" : "Info") === severity));
  el("logs").replaceChildren(...entries.map(e => {
    const row = node("p", new Date(e.time).toLocaleTimeString() + " · " + e.kind + " · " + e.message);
    if (e.path && e.kind !== "error") row.append(" ", artifactButton(e.path));
    return row;
  }));
}

async function act(action, text) {
  if (busy) return;
  busy = true;
  el("project").disabled = true;
  el("error").textContent = "";
  render();
  try {
    run = await api("run", {project}, {action, text, revision, runId: run?.id, requestId: run?.pending?.id});
    el("answer").value = "";
    if (action === "refresh" || action === "approve") await loadEvidence(project);
  } catch (error) {
    showError(error);
    revision = (await api("project", {project})).revision;
  } finally {
    busy = false;
    el("project").disabled = false;
    render();
  }
}

async function loadEvidence(current) {
  const files = (await api("project", {project: current})).files;
  const path = ["design/visual-review.md", "design/architecture.md"].find(file => files.includes(file));
  const markdown = path ? (await api("artifact", {project: current, path})).text : "";
  if (current !== project) return;
  el("diagrams").replaceChildren();
  el("visual-status").textContent = markdown ? markdown.split("\n").find(line => line && !line.startsWith("#")) || "" : "No visual review recorded.";
  const matches = [...markdown.matchAll(/^## (.+)$|^```mermaid\s*\n([\s\S]*?)^```/gm)];
  let title = "Architecture diagram";
  for (const match of matches) {
    if (match[1]) { title = match[1]; continue; }
    const detail = node("details", "");
    const diagram = node("div", "");
    diagram.className = "diagram";
    const source = node("details", "");
    source.append(node("summary", "Mermaid source"), node("pre", match[2]));
    detail.append(node("summary", title), diagram, source);
    el("diagrams").append(detail);
    detail.addEventListener("toggle", async () => {
      if (!detail.open || diagram.dataset.rendered) return;
      try {
        if (!diagramsLoaded) {
          const {default: mermaid} = await import("https://cdn.jsdelivr.net/npm/mermaid@11.12.0/dist/mermaid.esm.min.mjs");
          mermaid.initialize({startOnLoad:false, securityLevel:"strict", theme:"dark"});
          diagramsLoaded = mermaid;
        }
        const result = await diagramsLoaded.render("diagram-" + crypto.randomUUID(), match[2]);
        diagram.innerHTML = result.svg;
        diagram.dataset.rendered = "yes";
      } catch {
        diagram.textContent = "Diagram rendering unavailable. Open Mermaid source below.";
      }
    });
  }
  const inventory = markdown.split(/^## Skills used\s*$/m)[1]?.split(/^---$/m)[0];
  if (inventory) el("diagrams").append(node("h2", "Project skills used"), node("pre", inventory.trim()));
  if (!matches.some(match => match[2])) el("diagrams").append(node("p", "No Mermaid diagrams in this artifact."));
}

async function loadProject(name) {
  stream?.close();
  project = name;
  run = null;
  reviewNotes = "";
  el("answer").value = "";
  el("project-title").textContent = name;
  el("error").textContent = "";
  const data = await api("project", {project: name});
  if (name !== project) return;
  run = data.run;
  revision = data.revision;
  el("files").replaceChildren(...data.files.map(artifactButton));
  el("tests").replaceChildren();
  for (const path of data.files.filter(path => /^verification\//.test(path))) {
    el("tests").append(artifactButton(path));
    if (path.endsWith("conformance.json")) {
      const report = JSON.parse((await api("artifact", {project: name, path})).text);
      if (name !== project) return;
      const checks = report.boxes || [];
      el("tests").append(node("p", (report.used_db ? "SDK conformance with database" : "Offline SDK conformance") +
        " · " + checks.filter(c => c.passed).length + " passed · " +
        checks.filter(c => !c.passed && !c.not_run).length + " failed · " +
        checks.filter(c => c.not_run).length + " skipped"));
    }
  }
  if (data.files.includes("design/decisions.md")) {
    const notes = await api("artifact", {project: name, path: "design/decisions.md"});
    if (name !== project) return;
    reviewNotes = notes.text;
  }
  render();
  await Promise.all([preview("design/architecture.md"), loadEvidence(name)]);
  if (name !== project) return;
  const after = run?.events.length || 0;
  stream = new EventSource("/api/events?" + query({project: name, after}));
  stream.onmessage = async message => {
    const update = JSON.parse(message.data);
    if (name !== project || busy || update.seq <= (run?.events.length || 0)) return;
    try {
      const latest = await api("project", {project: name});
      if (name !== project || busy || (latest.run?.events.length || 0) < (run?.events.length || 0)) return;
      run = latest.run;
      revision = latest.revision;
      render();
    } catch (error) { showError(error); }
  };
}

async function main() {
  const workspace = await api("workspace");
  stages.push(...workspace.layers, "Implementation planning", "Generation", "Verification", "Handoff");
  option(el("log-stage"), "", "All");
  stages.forEach((name, index) => option(el("log-stage"), String(index), name));
  option(el("log-skill"), "", "All");
  for (const skill of workspace.skills) {
    option(el("log-skill"), skill.id, skill.id);
    const detail = node("details", "");
    detail.append(node("summary", skill.id), node("p", skill.description), node("pre", skill.source));
    el("skills").append(detail);
  }
  for (const name of workspace.projects) option(el("project"), name, name);
  el("project").addEventListener("change", () => loadProject(el("project").value).catch(showError));
  for (const id of ["log-stage", "log-skill", "log-severity"]) el(id).addEventListener("change", renderLogs);
  for (const [id, action] of Object.entries({
    start:"start", begin:"begin", refresh:"refresh", generate:"generate", approve:"approve",
    "fail-skill":"fail_skill", "retry-skill":"retry_skill",
  })) el(id).addEventListener("click", () => act(action).catch(showError));
  el("keep").addEventListener("click", () => act("answer", "Keep the current proposal.").catch(showError));
  el("revise").addEventListener("click", () => act("revision", el("answer").value).catch(showError));
  el("decision").addEventListener("submit", event => {
    event.preventDefault();
    act("answer", el("answer").value).catch(showError);
  });
  if (workspace.projects.length) await loadProject(workspace.projects[0]);
}
main().catch(showError);
