import time

import discord
import discord.ext.test as dpytest
import pytest

from otter_buddy import constants
from otter_buddy.cogs import misc


@pytest.fixture(autouse=True)
def misc_cog(bot: discord.ext.commands.Bot):
    misc_cog = misc.Misc(bot)
    bot.add_cog(misc_cog)
    dpytest.configure(bot)
    print("Tests starting")
    return misc_cog


# === TESTING ===

@pytest.mark.asyncio
async def test_echo_command(bot):    
    msg_content: str = "This is a test!"
    await dpytest.message(f'{constants.PREFIX}echo {msg_content}')
    assert dpytest.verify().message().content(msg_content)
