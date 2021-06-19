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

@pytest.mark.asyncio
async def test_pass_role_reaction_event(bot):
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
async def test_fail_role_reaction_event(bot):
    config = dpytest.get_config()
    user: discord.Member = config.members[0]
    guild: discord.Guild = config.guilds[0]
    role: discord.Role = dpytest.backend.make_role(name=constants.OTTER_ROLE, guild=guild)
    dpytest.backend.update_guild(guild=guild, roles=guild.roles.extend([role]))
    channel: discord.TextChannel = config.channels[0]
    message: discord.Message = dpytest.backend.make_message(content="This is a test message", author=user, channel=channel, id_num=1)
    await dpytest.add_reaction(user, message, "😀")
    assert constants.OTTER_ROLE not in map(lambda role: role.name, user.roles)
