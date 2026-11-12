# Companion playback test

From this directory, start a local server:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open [localhost:8000](http://localhost:8000/) in Chrome. The prefilled video ID is YouTube's API sample. You can replace it with an embeddable song URL or video ID.

1. Select **Simulate play command**. The event log shows command receipt separately from the player reporting **Playing**.
2. If Chrome blocks autoplay, select **Play / Resume**. Verify the player reports **Playing**.
3. Check **Pause**, **Play / Resume**, **Stop**, and the volume slider.
4. Try an invalid ID and verify the form rejects it. If YouTube rejects a valid ID, try a video that allows embedding.

## Test routing across tabs

1. Open the same URL in three tabs. Wait for the target tab's player to become ready and copy its tab ID.
2. In the sender tab, enter that ID under **Target tab ID** and select **Send to tab**. Only the target should load the video. The third tab should remain idle. If the target reports `needs_tap`, select **Play / Resume** there.
3. Select **Replay command** in the sender tab. It should report `duplicate` without restarting the target video. After 30 seconds, replay should report `expired`.

The routing test uses the browser's same-origin BroadcastChannel. Tab IDs route messages for the test. Production authentication and a cloud connection are separate integration work.

The form simulates a Port 0 command locally. The page logs YouTube callbacks for inspection. An authenticated Port 0 command and status channel is still needed for cloud integration. The local controls need no voice turn, LLM call, or API key. The embedded player requires an internet connection.

[YouTube player API](https://developers.google.com/youtube/iframe_api_reference) · [Chrome autoplay policy](https://developer.chrome.com/blog/autoplay/)

