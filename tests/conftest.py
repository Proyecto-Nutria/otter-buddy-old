import logging
import io
import asyncio

import pytest
from discord import Intents
from discord.ext.commands import Bot, when_mentioned_or

from otter_buddy.constants import PREFIX


log = logging.getLogger(__name__)

@pytest.fixture
async def bot(event_loop):
    bot = Bot(command_prefix=PREFIX, intents=Intents(members=True, guilds=True))

    yield bot
    

@pytest.fixture(scope="session")
def logcatch():
    return io.StringIO()

@pytest.fixture(scope="session", autouse=True)
def session_setup(logcatch):
    log.debug("Setting up test session")
    setup_logging(logcatch)


def setup_logging(logcatch):
    logging.root.handlers = []
    otter_log = logging.getLogger()
    sh = logging.StreamHandler(logcatch)
    otter_log.addHandler(sh)
    otter_log.propagate = False
    otter_log.setLevel(logging.DEBUG)
