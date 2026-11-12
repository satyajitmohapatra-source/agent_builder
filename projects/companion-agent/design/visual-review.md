# Port 0 visual review

All five design layers are closed. The project is checking implementation readiness. End-to-end voice playback is the first release milestone. The diagrams show the proposed expanded companion. The current agent implements storytelling and scripted follow-up. The Chrome test page has local player controls and simulates receipt of a play command. The cloud command channel and SDK playback grant are pending.

## System blocks

```mermaid
flowchart LR
    U[Listener] <--> H[Conversation host]
    H <--> P[Cloud Port 0 companion]
    P --> T[Tavily lookup]
    P --> L[LLM for open-ended conversation]
    P -. Proposed SDK action and device channel .-> C[Chrome test client]
    U -->|Local controls| C
    C <--> Y[YouTube embedded player]
    C -. Proposed player status .-> P
```

## Capability workflow

```mermaid
flowchart TD
    A[User request] --> B{Local player control?}
    B -->|Yes| C[Chrome handles it]
    B -->|No| D{Port 0 intent}
    D -->|Weather or factual lookup| E[Tavily and short answer]
    D -->|Story, discussion, or check-in| F[Conversation response]
    D -->|Play song| G{Clear song match?}
    G -->|No| H[Ask one focused question]
    G -->|Yes| I[Send play command through approved action path]
    I --> J{Player result}
    J -->|Playing| K[Show track without spoken confirmation]
    J -->|Autoplay blocked| M[Show Play button]
    J -->|Error| N[Show playback error]
```

## Candidate LangGraph flow

This is a design view. The storytelling prototype uses an SDK turn handler. Graph adoption remains open.

```mermaid
flowchart LR
    S([Start]) --> R[Read session context and route]
    R -->|Conversation| L[Story, entertainment, or wellbeing]
    R -->|Lookup| T[Tavily]
    R -->|Music| M[Resolve song]
    M -->|Ambiguous| Q[Ask for title or artist]
    M -->|Resolved| P[Propose playback]
    Q --> W[Save pending question]
    W --> E([End turn])
    P --> E
    T --> E
    L --> E
    W -. Next turn restores context .-> R
```

## Conversation and playback

```mermaid
sequenceDiagram
    actor User
    participant Chrome
    participant Host as Conversation host
    participant Port as Cloud Port 0
    participant Player as YouTube player
    User->>Host: Play the named song by the named artist
    Host->>Port: Route user turn
    Port->>Port: Resolve song
    Port-->>Chrome: Proposed command with ID and expiry via SDK
    Chrome->>Player: Load video ID
    alt Playback starts
        Player-->>Chrome: Playing
        Chrome-->>Port: Proposed Playing status with command ID
        Chrome-->>User: Show the track on screen
    else Autoplay is blocked
        Player-->>Chrome: Autoplay blocked
        Chrome-->>User: Show Play
        User->>Chrome: Tap Play
    end
    User->>Chrome: Tap Stop
    Chrome->>Player: Stop locally
    Note over User,Chrome: On-screen controls require zero voice turns
```

This scenario has no proposed database read or write. The cloud command and callback arrows represent interfaces still to be verified.

## Playback command state

```mermaid
stateDiagram-v2
    [*] --> Pending: Dispatch with command ID and expiry
    Pending --> Playing: Player confirms playback
    Pending --> NeedsTap: Autoplay blocked
    NeedsTap --> Playing: User taps Play and player confirms
    Pending --> Unknown: Connection drops or status times out
    Unknown --> Playing: Existing command status confirms playback
    Pending --> Failed: Player rejects command
    Pending --> Expired: Deadline passes before command starts
    NeedsTap --> Expired: Deadline passes before user taps Play
    Playing --> Stopped: User stops playback locally
```

The proposed status check looks up the original command when its result is unknown. The browser deduplicates commands and rejects expired requests.

## Implementation readiness

```mermaid
flowchart LR
    A[Five layers approved] --> B[Verify live Chrome player controls]
    B --> C[Verify SDK playback action and browser channel]
    C --> D[Run one voice request end to end]
    D --> E[Check failures, retries and voice turn count]
```

The Codex in-app browser reported Playing, Paused, Playing, and Stopped with the live YouTube player. The volume slider moved from 70 to 69. Chrome desktop and cloud dispatch remain unverified.

## Browser channel readiness

The inspected Chotu gateway accepts utterances over its conversation socket and requires a senior ID header. A browser's native WebSocket constructor cannot set that header. The gateway has no browser playback result message, and Port 0 has no playback action grant.

```mermaid
sequenceDiagram
    participant Browser as Chrome session
    participant Gateway as Proposed device channel
    participant Port as Port 0
    participant Gate as SDK action gate
    Browser->>Gateway: Connect using browser session authentication
    Gateway-->>Browser: Bind to current conversation
    Port->>Gate: Propose playback for resolved video ID
    Gate->>Gateway: Dispatch authorized command with ID and expiry
    Gateway->>Browser: Deliver command to bound session
    Browser-->>Gateway: Report Playing, NeedsTap, or Failed with command ID
    Gateway-->>Port: Return correlated status
```

For the first integration test, use the existing known video ID. Verify that a second session cannot receive or acknowledge the command, and that duplicate or expired commands do not restart playback. Run the same test with a spoken song request after the channel works.

## Skills used

| Builder skill applied | Output |
| --- | --- |
| Draw System Blocks | System blocks above |
| Draw Workflow Flowchart | Capability decisions and playback command state above |
| Draw LangGraph Flow | Candidate LangGraph flow above |
| Draw Conversation Flow | Conversation sequence above |
| List Workflow Skills | This inventory |

| Agent capability | Status |
| --- | --- |
| Storytelling and follow-up | Implemented and tested in the offline prototype |
| Weather, movies and TV, wellbeing | Proposed |
| Song playback | Live player controls verified in the Codex in-app browser. Chrome desktop and cloud routing are unverified. |

---

*© 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its contents are confidential and proprietary to the Owners. No part of this document, including its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to create any identical, substantially similar, or derivative material without the prior written consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is prohibited and may result in legal action under applicable Indian law. Subject to applicable law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha, where legally maintainable.*
