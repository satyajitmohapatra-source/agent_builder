# Companion agent review

**Resume point:** All five design layers are closed. Implementation readiness is next. See the [visual review](visual-review.md) for the current decisions and diagrams.

| Layer | Status |
| --- | --- |
| 1. Agent identity and objectives | Closed |
| 2. Orchestration and decision-making | Closed |
| 3. Skills and capabilities | Closed |
| 4. User interaction and conversation management | Closed |
| 5. Memory, state, and execution | Closed |

## Workflow bug · Agent generated before design review

The Port 0 prototype was generated and evaluated before the engineer was prompted to review and close the five layers. The code and test results are retained as prototype evidence. At the time of generation, no layer had been approved. Resume with the full [architecture draft](architecture.md), ask for explicit closure in order, and keep further generation pending until the generation gate is satisfied.

## Layer 1 decision

Port 0 provides companionship through light conversation and shared activities:

- Tell short stories the listener can continue, stop, or discuss.
- Talk about the weather, including local conditions or forecasts when a trusted source is available.
- Discuss movies and TV series, and check before revealing major plot details.
- Play songs the listener requests through a supported playback integration, with a way to stop playback.
- Offer gentle wellbeing check-ins. Let the listener decline or change the subject. Keep check-ins conversational and follow the platform's policy if a response calls for escalation.

Open for later layers: weather data and location handling, music playback and its permissions, user-initiated versus proactive check-ins, and language coverage.


The reviewer approved the expanded scope.

## Layer 2 decision

Use one Port 0 companion with a coordinator that routes each turn to storytelling, weather, movies and TV, music, or wellbeing. Treat an answer to an active question as a follow-up when it fits that question. Route clear topic changes to the new capability and preserve story progress so the listener can return to it. Direct a stop request to the activity it names. If the target is unclear and more than one activity could match, ask which one to stop.

The conversation host owns the speaking floor and conversation routing. Port 0 owns the five capabilities, including search, song selection, playback commands through Android utils, and wellbeing dialogue. Whether to offer proactive check-ins remains open.


The reviewer approved the routing and interruption model.

## Layer 3 decision

| Capability | Proposed behavior |
| --- | --- |
| Storytelling | Tell a short story, pause for continuation or discussion, and keep the listener's place when they switch topics. |
| Weather | Use Tavily to find current, location-specific information from trusted weather sources. Ask for the location when it is unclear. Say when current conditions or forecasts are unavailable. |
| Movies and TV | Discuss titles, characters, and themes. Use Tavily to look up factual details when needed. Ask before major spoilers. Clarify an ambiguous title. |
| Music | Resolve a requested song and ask for the artist if needed. Resolve the song to a YouTube video. Use Android utils to control the YouTube player, or Android MediaPlayer for supported media sources. Report playback after the player confirms it. |
| Wellbeing | Ask a gentle question, acknowledge the reply, and let the listener decline or change topics. Follow the platform policy for escalation if applicable. Proactive initiation remains open. |

These capabilities belong to one Port 0 agent and can be evaluated independently. Port 0 needs a Tavily turn secret. The pinned SDK requires external side effects to go through the action gate and Port 0 currently lacks an execution grant and playback action kinds. The Android utility bridge and an SDK-compatible play/stop path still need to be verified. YouTube videos use the official embedded player. Language coverage remains open.


The reviewer accepted end-to-end voice playback as the first release milestone. Verify the player controls in Chrome first, then verify that a spoken song request reaches the correct Chrome session and starts playback. Chrome is the interim client while Android is being built. The SDK playback grant and device command channel remain implementation dependencies.

## Layer 4 decision

- For a clear song request, aim for one user voice turn. Show the track when the player confirms playback. If Chrome blocks autoplay, show a Play button. For an ambiguous match, ask for the missing title or artist.
- Handle on-screen pause, resume, stop, and volume locally. These controls use zero LLM calls and zero spoken replies.
- Give a brief weather answer when the location and time are known. If a lookup needs clarification, ask for the missing details together. Preserve story progress across topic changes. Let the listener decline a wellbeing check-in or change topics.

Measure voice turns and LLM calls per completed request. The one-turn playback target depends on the approved SDK action path.


The reviewer approved the interaction rules.

## Layer 5 decision

- Keep story progress and unresolved questions in SDK session state. Restore them when the host resumes the session. Keep wellbeing answers within the conversation under the host's existing policy.
- For voice playback, propose the resolved video ID through the SDK action path. The execution path sends a short-lived command with a unique ID to the authenticated Chrome session. Chrome ignores duplicate or expired commands.
- Correlate player results with the command ID. Show the track once the player reports Playing. If autoplay is blocked, show Play. If the connection drops or the result is unknown, check the existing command status before considering a retry.
- Chrome keeps player state and handles on-screen playback controls locally. Measure voice turns and LLM calls per completed request.

Implementation readiness still depends on a Port 0 playback action grant and a verified command and status channel. The existing Chrome page exercises local controls with a simulated command.


The reviewer approved the state and execution design.

## Implementation readiness

1. Verify play, pause, resume, stop, and volume in Chrome with a known embeddable video. The Codex in-app browser loaded the live YouTube player. Play, pause, resume, and stop were confirmed by player events. The volume slider moved from 70 to 69. Chrome desktop and audible volume were not verified.
2. Define and verify an SDK-approved Port 0 playback action and a command and status channel bound to the authenticated browser session. The inspected Port 0 grants currently contain no playback action or execution capability.
3. Run a named song request through the authorized path and confirm that the intended tab reports Playing. Exercise autoplay blocked, expiry, duplicate delivery, and status recovery on disconnect. Measure voice turns and LLM calls.

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
