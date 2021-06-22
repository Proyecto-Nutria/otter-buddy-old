import time

import discord
import discord.ext.test as dpytest
import pytest
import mongomock
from unittest.mock import patch

from otter_buddy import constants
from otter_buddy.cogs import misc
from otter_buddy.data import dbconn


mock_connection = mongomock.MongoClient('mongodb://localhost:27017')

def mock_client(self):
    self.connection = mock_connection
    return self


@pytest.fixture(autouse=True)
def misc_cog(bot: discord.ext.commands.Bot):
    misc_cog = misc.Misc(bot)
    bot.add_cog(misc_cog)
    dpytest.configure(bot)
    print("Tests starting")
    return misc_cog


# === TESTING ===

@pytest.mark.asyncio
async def test_echo_command():
    msg_content: str = "This is a test!"
    await dpytest.message(f'{constants.PREFIX}echo {msg_content}')
    assert dpytest.verify().message().content(msg_content)

@pytest.mark.asyncio
async def test_subscribe_command_invalid_email():
    msg_content: str = "test.com"
    expected: str = "Write a valid email"
    await dpytest.message(f'{constants.PREFIX}subscribe {msg_content}')
    assert dpytest.verify().message().content(expected)

@patch.object(dbconn.DbConn, '__enter__', mock_client)
@pytest.mark.asyncio
async def test_subscribe_command():
    msg_content: str = "test@test.com"
    expected: str = "Succesfully subscribed!"
    await dpytest.message(f'{constants.PREFIX}subscribe {msg_content}')
    assert dpytest.verify().message().content(expected)

    msg_content: str = "new_test@test.com"
    expected: str = "Succesfully updated your subscription!"
    await dpytest.message(f'{constants.PREFIX}subscribe {msg_content}')
    assert dpytest.verify().message().content(expected)

@pytest.mark.asyncio
async def test_pass_role_reaction_event():
    config = dpytest.get_config()
    user: discord.Member = config.members[0]
    guild: discord.Guild = config.guilds[0]
    role: discord.Role = dpytest.backend.make_role(name=constants.OTTER_ROLE, guild=guild)
    dpytest.backend.update_guild(guild=guild, roles=guild.roles.extend([role]))
    channel: discord.TextChannel = config.channels[0]
    message: discord.Message = dpytest.backend.make_message(content="This is a test message", author=user, channel=channel, id_num=int(constants.WELCOME_MESSAGES[0]))
    await dpytest.add_reaction(user, message, "😀")
    assert constants.OTTER_ROLE in map(lambda role: role.name, user.roles)

@pytest.mark.asyncio
async def test_fail_role_reaction_event():
    config = dpytest.get_config()
    user: discord.Member = config.members[0]
    guild: discord.Guild = config.guilds[0]
    role: discord.Role = dpytest.backend.make_role(name=constants.OTTER_ROLE, guild=guild)
    dpytest.backend.update_guild(guild=guild, roles=guild.roles.extend([role]))
    channel: discord.TextChannel = config.channels[0]
    message: discord.Message = dpytest.backend.make_message(content="This is a test message", author=user, channel=channel, id_num=1)
    await dpytest.add_reaction(user, message, "😀")
    assert constants.OTTER_ROLE not in map(lambda role: role.name, user.roles)
