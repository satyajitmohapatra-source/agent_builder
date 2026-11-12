# © 2026 Diya Mohapatra and Satyajit Mohapatra. All rights reserved. This document and its
# contents are confidential and proprietary to the Owners. No part of this document, including
# its concepts, ideas as expressed, strategies, structure, designs, methodologies, or commercial
# proposals, may be copied, reproduced, adapted, modified, distributed, disclosed, or used to
# create any identical, substantially similar, or derivative material without the prior written
# consent of the Owners. Unauthorised use, disclosure, reproduction, or distribution is
# prohibited and may result in legal action under applicable Indian law. Subject to applicable
# law, disputes shall fall within the jurisdiction of the competent courts at Cuttack, Odisha,
# where legally maintainable.

from pathlib import Path

import pytest
from chotu_agent_sdk import Language, Status
from chotu_agent_sdk.testing import MockOrchestrator, make_offline_user
from chotu_agent_sdk.testing.loader import load_agent_class

StoryCompanion = load_agent_class(Path(__file__).resolve().parents[1])


@pytest.fixture
def host(tmp_path):
    return MockOrchestrator(
        StoryCompanion,
        user=make_offline_user(language=Language.ENGLISH),
        port=0,
        log_dir=tmp_path,
    )


@pytest.mark.asyncio
async def test_story_restart_and_discussion(host):
    async with host:
        opening = await host.turn("Tell me a story", turn_id="opening")
        assert opening.result and not opening.result.task_open
        assert "Mira found a paper boat beside the river." in opening.sentences
        await host.restart()
        assert (await host.turn("Tell me a story", turn_id="opening")).replayed
        ending = await host.turn("What happened next?")
        assert "Together they brought the kitten home." in ending.sentences
        discussion = await host.turn("Mira was kind.")
        assert discussion.status is Status.DONE
        assert "Even a small act of kindness can matter." in discussion.sentences
        assert not host.domain.calls


@pytest.mark.asyncio
async def test_user_stops_story(host):
    async with host:
        await host.turn("Tell me a story")
        assert (await host.turn("Stop")).status is Status.DONE
        after = await host.turn("Continue")
        assert after.sentences == ["You can ask me to tell you a story."]


@pytest.mark.asyncio
async def test_accept_story_invitation(host):
    async with host:
        assert (await host.turn("Hello")).status is Status.NEEDS_INPUT
        opening = await host.turn("Yes")
        assert "Mira found a paper boat beside the river." in opening.sentences
