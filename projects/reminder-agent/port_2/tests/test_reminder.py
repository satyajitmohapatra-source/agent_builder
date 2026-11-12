# © 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its
# contents are confidential and proprietary to the Owners. No part of this document, including
# its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial
# proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to
# create any identical, substantially similar, or derivative material without the prior written
# consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is
# prohibited and may result in legal action under applicable Indian law. Subject to applicable
# law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha,
# where legally maintainable.

"""Evaluate the Port 2 prototype against the pinned SDK's offline harness."""

import sys
from pathlib import Path

import pytest
from chotu_agent_sdk import Language, Status
from chotu_agent_sdk.testing import MockOrchestrator, make_offline_user

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent import ReminderAgent


@pytest.fixture
def host(tmp_path):
    return MockOrchestrator(
        ReminderAgent,
        user=make_offline_user(language=Language.ENGLISH),
        port=2,
        log_dir=tmp_path,
    )


@pytest.mark.asyncio
async def test_resume_and_host_confirmation(host):
    async with host:
        request = await host.turn("Remind me to water the plants tomorrow")
        assert request.result and request.result.task_open
        assert request.sentences == ["What time should I remind you?"]
        await host.restart()
        proposal = await host.turn("At seven in the evening", turn_id="same-time")
        assert proposal.status is Status.DONE
        assert host.gate.confirmation is not None
        assert not host.domain.calls
        assert (
            await host.turn("At seven in the evening", turn_id="same-time")
        ).replayed
        assert (await host.turn("Yes")).handled_by_platform
        assert len(host.domain.calls) == 1
        call = host.domain.calls[0]
        assert call.kind == "personal.reminder.create"
        assert call.params["message"] == "water the plants"
        assert "T19:00:00" in call.params["due_at"]


@pytest.mark.asyncio
async def test_partial_reply_and_draft_cancel(host):
    async with host:
        first = await host.turn("Set a reminder")
        assert first.sentences == ["What should I remind you about, and when?"]
        second = await host.turn("Water the plants")
        assert second.sentences == ["What day should I remind you?"]
        await host.turn("Never mind")
        assert host.gate.confirmation is None
        assert not host.domain.calls


@pytest.mark.asyncio
@pytest.mark.parametrize("utterance", ["List my reminders", "Cancel my plant reminder"])
async def test_unavailable_read_is_explicit(host, utterance):
    async with host:
        result = await host.turn(utterance)
        assert result.sentences == ["I can't look up scheduled reminders here yet."]
        assert not host.domain.calls
