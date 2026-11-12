# © 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its
# contents are confidential and proprietary to the Owners. No part of this document, including
# its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial
# proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to
# create any identical, substantially similar, or derivative material without the prior written
# consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is
# prohibited and may result in legal action under applicable Indian law. Subject to applicable
# law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha,
# where legally maintainable.

"""An offline Port 0 story companion for the Chotu SDK."""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Literal

from chotu_agent_sdk import (
    ChotuAgent,
    Manifest,
    Status,
    TurnContext,
    TurnOutput,
    TurnResult,
)
from pydantic import BaseModel


class StoryTask(BaseModel):
    stage: Literal["idle", "invited", "opening", "finished"] = "idle"


class StoryCompanion(ChotuAgent[StoryTask]):
    manifest = Manifest.from_file(Path(__file__).with_name("manifest.yaml"))

    async def on_turn(self, ctx: TurnContext[StoryTask]) -> AsyncIterator[TurnOutput]:
        phrase = " ".join(re.findall(r"[a-z]+", ctx.utterance.lower()))
        if phrase in {"stop", "stop the story", "no", "never mind", "no thanks"}:
            ctx.task.stage = "idle"
            yield "Of course."
            yield TurnResult(Status.DONE)
            return

        if (
            re.search(
                r"\b(?:tell me a story|start the story|restart the story)\b",
                phrase,
            )
            or phrase == "story"
            or (ctx.task.stage == "invited" and ctx.speech.is_yes(ctx.utterance))
        ):
            ctx.task.stage = "opening"
            yield "Mira found a paper boat beside the river."
            yield "A tiny note inside asked for help."
            yield "Would you like to hear what she did?"
        elif ctx.task.stage == "opening" and (
            ctx.speech.is_yes(ctx.utterance)
            or phrase in {"continue", "go on", "what happened next", "tell me more"}
        ):
            ctx.task.stage = "finished"
            yield "Mira followed the river to an old bridge."
            yield "A child there had lost their kitten."
            yield "Mira heard a meow beneath the bridge."
            yield "Together they brought the kitten home."
            yield "What did you think of Mira?"
        elif ctx.task.stage == "finished" and any(
            word in phrase.split()
            for word in ("mira", "kitten", "helpful", "kind", "brave", "moral")
        ):
            yield "Mira noticed someone needed help."
            yield "Even a small act of kindness can matter."
            yield TurnResult(Status.DONE)
            return
        elif ctx.task.stage == "opening":
            yield "Would you like me to continue the story?"
        elif phrase in {"hi", "hello", "hey", "good morning", "good evening"}:
            yield "Hello."
            yield "Would you like to hear a story?"
            ctx.task.stage = "invited"
            yield TurnResult(Status.NEEDS_INPUT)
            return
        elif ctx.task.stage == "finished":
            yield "Thanks for listening."
            yield TurnResult(Status.DONE)
            return
        else:
            yield "You can ask me to tell you a story."
            yield TurnResult(Status.DONE)
            return

        yield TurnResult(Status.NEEDS_INPUT)

    async def on_resume(self, ctx: TurnContext[StoryTask]) -> str:
        if ctx.task.stage == "opening":
            return "Mira had just found the paper boat."
        return "I'm here if you'd like to keep chatting."

    async def on_cancel(self, ctx: TurnContext[StoryTask]) -> None:
        ctx.task.stage = "idle"
