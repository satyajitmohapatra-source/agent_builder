"use strict";

const form = document.querySelector("#track-form");
const video = document.querySelector("#video");
const status = document.querySelector("#status");
const events = document.querySelector("#events");
const volume = document.querySelector("#volume");
const controls = ["send", "play", "pause", "stop"].map(id => document.getElementById(id));
const [send, play, pause, stop] = controls;
let player;
let activeCommand;
let stopRequested = false;
let lastSentCommand;
const acceptedCommands = new Map();
const remoteStatus = document.querySelector("#remote-status");
const replayRemote = document.querySelector("#replay-remote");
const tabId = location.protocol === "file:" ? null : crypto.randomUUID();
const channel = tabId ? new BroadcastChannel("chotu-playback-test") : null;

function playerStatus(state, message) {
  report(message);
  if (!activeCommand || !activeCommand.sender) return;
  sendStatus(activeCommand, state);
}

function sendStatus(command, state) {
  channel.postMessage({
    type: "status",
    id: command.id,
    sender: tabId,
    target: command.sender,
    state,
  });
}

function report(message) {
  status.textContent = message;
  const row = document.createElement("li");
  row.textContent = activeCommand ? `${activeCommand.id}: ${message}` : message;
  events.prepend(row);
  if (events.children.length > 12) events.lastElementChild.remove();
}

function videoId(value) {
  const valid = /^[A-Za-z0-9_-]{11}$/;
  if (valid.test(value)) return value;
  try {
    const url = new URL(value);
    if (url.protocol !== "https:" && url.protocol !== "http:") return null;
    const [, route, segment] = url.pathname.split("/");
    let id = null;
    if (url.hostname === "youtu.be") id = route;
    if (["youtube.com", "www.youtube.com", "m.youtube.com"].includes(url.hostname)) {
      id = route === "watch" ? url.searchParams.get("v") : null;
      if (route === "shorts" || route === "embed") id = segment;
    }
    return id && valid.test(id) ? id : null;
  } catch {
    return null;
  }
}

function onStateChange({ data }) {
  const state = YT.PlayerState;
  if (data === state.PLAYING && !stopRequested) playerStatus("playing", "Playing.");
  if (data === state.PAUSED && !stopRequested) playerStatus("paused", "Paused.");
  if (data === state.BUFFERING && !stopRequested) playerStatus("buffering", "Buffering…");
  if (data === state.CUED) playerStatus(stopRequested ? "stopped" : "ready", stopRequested ? "Stopped." : "Ready to play.");
  if (data === state.UNSTARTED && stopRequested) playerStatus("stopped", "Stopped.");
  if (data === state.ENDED) playerStatus(stopRequested ? "stopped" : "ended", stopRequested ? "Stopped." : "Playback ended.");
}

window.onYouTubeIframeAPIReady = () => {
  player = new YT.Player("player", {
    playerVars: { origin: location.origin, playsinline: 1 },
    events: {
      onReady: ({ target }) => {
        target.getIframe().title = "YouTube playback";
        target.setVolume(Number(volume.value));
        send.disabled = false;
        volume.disabled = false;
        report("Player ready. Submit a play command to begin.");
      },
      onStateChange,
      onAutoplayBlocked: () => {
        if (!stopRequested) playerStatus("needs_tap", "Chrome blocked autoplay. Select Play / Resume.");
      },
      onError: ({ data }) => playerStatus("failed", `YouTube playback failed (error ${data}).`),
    },
  });
};

function selectedVideoId() {
  const id = videoId(video.value.trim());
  if (!id) {
    video.setCustomValidity("Enter a YouTube URL or an 11-character video ID.");
    video.reportValidity();
  }
  return id;
}

function loadCommand(command) {
  activeCommand = command;
  stopRequested = false;
  for (const control of [play, pause, stop]) control.disabled = false;
  playerStatus("accepted", `Play command received for ${command.videoId}.`);
  player.loadVideoById(command.videoId);
}

form.addEventListener("submit", event => {
  event.preventDefault();
  const id = selectedVideoId();
  if (id && !send.disabled) loadCommand({ id: crypto.randomUUID(), videoId: id });
});

if (channel) {
  document.querySelector("#tab-id").textContent = tabId;
  document.querySelector("#send-remote").disabled = false;
  document.querySelector("#remote-form").addEventListener("submit", event => {
    event.preventDefault();
    const id = selectedVideoId();
    const target = document.querySelector("#target-tab").value.trim();
    if (!id || !target || target === tabId) {
      remoteStatus.textContent = "Enter a valid video and another tab’s ID.";
      return;
    }
    lastSentCommand = {
      type: "play", id: crypto.randomUUID(), videoId: id,
      sender: tabId, target, expiresAt: Date.now() + 30000,
    };
    channel.postMessage(lastSentCommand);
    remoteStatus.textContent = "Command sent. Waiting for target tab.";
    replayRemote.disabled = false;
  });
  replayRemote.addEventListener("click", () => channel.postMessage(lastSentCommand));

  channel.addEventListener("message", ({ data: message }) => {
    if (!message || message.target !== tabId) return;
    if (message.type === "status") {
      if (lastSentCommand && message.id === lastSentCommand.id && message.sender === lastSentCommand.target) {
        remoteStatus.textContent = `Target tab reported: ${message.state}.`;
      }
      return;
    }
    if (message.type !== "play" || typeof message.id !== "string" ||
        typeof message.sender !== "string" || !Number.isFinite(message.expiresAt) ||
        typeof message.videoId !== "string" || videoId(message.videoId) !== message.videoId) return;
    const now = Date.now();
    for (const [id, expiry] of acceptedCommands) {
      if (expiry <= now) acceptedCommands.delete(id);
    }
    if (message.expiresAt <= now) {
      sendStatus(message, "expired");
    } else if (acceptedCommands.has(message.id)) {
      sendStatus(message, "duplicate");
    } else if (send.disabled) {
      sendStatus(message, "player_not_ready");
    } else {
      acceptedCommands.set(message.id, message.expiresAt);
      loadCommand(message);
    }
  });
}

video.addEventListener("input", () => video.setCustomValidity(""));
play.addEventListener("click", () => {
  stopRequested = false;
  player.playVideo();
});
pause.addEventListener("click", () => player.pauseVideo());
stop.addEventListener("click", () => {
  stopRequested = true;
  report("Stopping…");
  player.cueVideoById(activeCommand.videoId);
});
volume.addEventListener("input", () => player.setVolume(Number(volume.value)));

if (location.protocol === "file:") {
  report("Serve this page on localhost. See README.md.");
} else {
  const script = document.createElement("script");
  script.src = "https://www.youtube.com/iframe_api";
  script.addEventListener("error", () => report("Could not load the YouTube player."));
  document.head.append(script);
}
