# © 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its
# contents are confidential and proprietary to the Owners. No part of this document, including
# its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial
# proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to
# create any identical, substantially similar, or derivative material without the prior written
# consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is
# prohibited and may result in legal action under applicable Indian law. Subject to applicable
# law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha,
# where legally maintainable.


"""Port 2 reminder prototype for the contract 0.2 SDK."""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal
from uuid import uuid4

from chotu_agent_sdk import (
    ActionProposal,
    ActionStatus,
    ChotuAgent,
    Manifest,
    Status,
    TurnContext,
    TurnOutput,
    TurnResult,
)
from pydantic import BaseModel

DAY = re.compile(r"\b(today|tomorrow)\b", re.IGNORECASE)
TIME = re.compile(
    r"\b(?:(?P<hour>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
    r"(?::(?P<minute>\d{2}))?\s*(?P<period>am|pm|in the morning|in the evening)\b"
    r"|(?P<clock_hour>\d{1,2}):(?P<clock_minute>\d{2})\b)",
    re.IGNORECASE,
)
HOURS = [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
]


class ReminderTask(BaseModel):
    key: str | None = None
    message: str | None = None
    day: datetime | None = None
    hour: int | None = None
    minute: int = 0
    submission_unknown: bool = False


class ReminderAgent(ChotuAgent[ReminderTask]):
    manifest = Manifest.from_file(Path(__file__).with_name("manifest.yaml"))

    async def on_turn(
        self, ctx: TurnContext[ReminderTask]
    ) -> AsyncIterator[TurnOutput]:
        text = ctx.utterance.strip()
        phrase = text.lower().rstrip(".?!")
        if ctx.task.submission_unknown:
            yield "The scheduling result is still unknown."
            yield TurnResult(Status.NEEDS_INPUT, task_open=True)
            return
        if phrase in {"cancel", "cancel that", "never mind"} and ctx.task.key:
            ctx.task = ReminderTask()
            yield "I left the draft unscheduled."
            yield TurnResult(Status.DONE)
            return

        request = classify(phrase)
        if request == "read":
            yield "I can't look up scheduled reminders here yet."
            status = Status.NEEDS_INPUT if ctx.task.key else Status.DONE
            yield TurnResult(status, task_open=ctx.task.key is not None)
            return
        if request == "create" and ctx.task.key is None:
            ctx.task.key = str(uuid4())
        if ctx.task.key is None:
            yield "You can ask me to set a personal reminder."
            yield TurnResult(Status.DONE)
            return

        draft = ctx.task
        collect(draft, text, ctx.now)
        question = missing_details(draft, ctx.now)
        if question:
            yield question
            yield TurnResult(Status.NEEDS_INPUT, task_open=True)
            return

        assert draft.day is not None and draft.hour is not None and draft.message
        due = draft.day.replace(hour=draft.hour, minute=draft.minute)
        # The pinned host has no domain payload schema for this kind yet.
        proposal = ActionProposal(
            kind="personal.reminder.create",
            params={"message": draft.message, "due_at": due.isoformat()},
            idempotency_key=draft.key,
            readback=f"Set a reminder to {draft.message} on {due:%B %d} at {due:%H:%M}?",
        )
        try:
            result = await ctx.actions.propose(proposal)
        except TimeoutError:
            draft.submission_unknown = True
            yield "I couldn't verify the request. Please check before trying again."
            yield TurnResult(Status.NEEDS_INPUT, task_open=True)
            return

        ctx.task = ReminderTask()
        match result.status:
            case ActionStatus.AWAITING_CONFIRMATION:
                pass  # The host voices the readback.
            case ActionStatus.SUCCEEDED:
                yield "Your reminder is scheduled."
            case ActionStatus.REJECTED | ActionStatus.FAILED | ActionStatus.EXPIRED:
                yield "I couldn't schedule your reminder."
            case _:
                yield "I'm waiting for the scheduling result."
        yield TurnResult(Status.DONE)

    async def on_cancel(self, ctx: TurnContext[ReminderTask]) -> None:
        ctx.task = ReminderTask()

    async def on_resume(self, ctx: TurnContext[ReminderTask]) -> str:
        if ctx.task.submission_unknown:
            return "The scheduling result is still unknown."
        return missing_details(ctx.task, ctx.now) or "Let's continue your reminder."


def classify(phrase: str) -> Literal["create", "read", "other"]:
    if phrase.startswith(("remind me", "set a reminder", "create a reminder")):
        return "create"
    if "reminder" in phrase and phrase.startswith(("what", "list", "show", "cancel")):
        return "read"
    return "other"


def collect(draft: ReminderTask, text: str, now: datetime) -> None:
    day = DAY.search(text)
    if day:
        offset = int(day.group().lower() == "tomorrow")
        draft.day = (now + timedelta(days=offset)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    time = TIME.search(text)
    if time:
        if time["period"]:
            raw_hour = time["hour"].lower()
            hour = int(raw_hour) if raw_hour.isdigit() else HOURS.index(raw_hour) + 1
            minute = int(time["minute"] or 0)
            if 1 <= hour <= 12 and minute < 60:
                afternoon = time["period"].lower() in {"pm", "in the evening"}
                draft.hour, draft.minute = hour % 12 + 12 * afternoon, minute
        else:
            hour, minute = int(time["clock_hour"]), int(time["clock_minute"])
            if hour < 24 and minute < 60:
                draft.hour, draft.minute = hour, minute

    if draft.message is None:
        if text.lower().startswith("remind me to "):
            message = re.split(
                r"\b(?:today|tomorrow|at)\b", text[13:], maxsplit=1, flags=re.IGNORECASE
            )[0]
        elif classify(text.lower()) == "other" and not day and not time:
            message = text
        else:
            message = ""
        draft.message = message.strip(" .?!")[:80] or None


def missing_details(draft: ReminderTask, now: datetime) -> str | None:
    if draft.message is None and (draft.day is None or draft.hour is None):
        return "What should I remind you about, and when?"
    if draft.message is None:
        return "What should I remind you about?"
    if draft.day is None:
        return "What day should I remind you?"
    if draft.hour is None:
        return "What time should I remind you?"
    if draft.day.replace(hour=draft.hour, minute=draft.minute) <= now:
        return "Please give me a future time."
    return None
