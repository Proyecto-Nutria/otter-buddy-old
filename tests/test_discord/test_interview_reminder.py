import datetime

import discord
import discord.ext.test as dpytest
import pytest
import mongomock
from unittest.mock import patch

from otter_buddy import constants
from otter_buddy.cogs import interview_reminder
from otter_buddy.utils.db import dbconn, db_interview_reminder


mock_connection = mongomock.MongoClient('mongodb://localhost:27021')

def mock_client(self):
    self.connection = mock_connection
    return self

@pytest.fixture(autouse=True)
def interview_reminder_cog(bot: discord.ext.commands.Bot):
    interview_reminder_cog = interview_reminder.InterviewReminder(bot)
    bot.add_cog(interview_reminder_cog)
    dpytest.configure(bot, 2, 2, 2)
    print("Tests starting")
    return interview_reminder_cog


# === TESTING ===

@patch.object(dbconn.DbConn, '__enter__', mock_client)
@pytest.mark.asyncio
async def test_send_weekly_message(interview_reminder_cog):
    config = dpytest.get_config()
    guild: discord.Guild = config.guilds[0]
    channel: discord.TextChannel = config.channels[0]
    role_name: str = 'TEST_ROLE'
    role: discord.Role = dpytest.backend.make_role(name=role_name, guild=guild)
    dpytest.backend.update_guild(guild=guild, roles=guild.roles.extend([role]))
    message: str = 'This is a test reminder'

    interview_reminder = {
        "day_of_the_week":  datetime.datetime.today().weekday(),
        "channel_id":       channel.id,
        "role_mention":     role.mention,
        "message":          message,
        "guild_id":         guild.id,
    }
    db_interview_reminder.DbInterviewReminder.set_interview_reminder(interview_reminder)

    await interview_reminder_cog.send_scheduled_message()

    reminder_message: str = (
        f'{role.mention}\n'
        f'{message}'
    )
    expected = discord.Embed(description=reminder_message, color=constants.BRAND_COLOR)
    assert dpytest.verify().message().embed(expected)

    db_interview_reminder.DbInterviewReminder.delete_interview_reminder(guild.id)

@patch.object(dbconn.DbConn, '__enter__', mock_client)
@pytest.mark.asyncio
async def test_succesfully_stop(interview_reminder_cog):
    config = dpytest.get_config()
    guild: discord.Guild = config.guilds[0]
    channel: discord.TextChannel = config.channels[0]
    role_name: str = constants.OTTER_ADMIN
    role: discord.Role = dpytest.backend.make_role(name=role_name, guild=guild)
    dpytest.backend.update_guild(guild=guild, roles=guild.roles.extend([role]))
    message: str = 'This is a test reminder'

    interview_reminder = {
        "day_of_the_week":  datetime.datetime.today().weekday(),
        "channel_id":       channel.id,
        "role_mention":     role.mention,
        "message":          message,
        "guild_id":         guild.id,
    }
    db_interview_reminder.DbInterviewReminder.set_interview_reminder(interview_reminder)

    result = db_interview_reminder.DbInterviewReminder.get_interview_reminder(guild.id)
    assert result["guild_id"] == guild.id

    user: discord.Member = config.members[0]
    extended_roles = user.roles
    extended_roles.append(role)
    dpytest.backend.update_member(member=user, roles=extended_roles)
    expected: str = "**Interview Reminder** stopped!"
    await dpytest.message(f'{constants.PREFIX}interview_reminder stop', channel=channel, member=user)
    assert dpytest.verify().message().content(expected)

    result = db_interview_reminder.DbInterviewReminder.get_interview_reminder(guild.id)
    assert result is None

@patch.object(dbconn.DbConn, '__enter__', mock_client)
@pytest.mark.asyncio
async def test_unsuccesfully_stop(interview_reminder_cog):
    config = dpytest.get_config()
    user: discord.Member = config.members[0]
    guild: discord.Guild = config.guilds[0]
    channel: discord.TextChannel = config.channels[0]
    role_name: str = constants.OTTER_ADMIN
    role: discord.Role = dpytest.backend.make_role(name=role_name, guild=guild)
    extended_roles = user.roles
    extended_roles.append(role)
    dpytest.backend.update_guild(guild=guild, roles=guild.roles.extend([role]))
    dpytest.backend.update_member(member=user, roles=extended_roles)

    expected: str = "No reminder was set! 😱"
    await dpytest.message(f'{constants.PREFIX}interview_reminder stop', channel=channel, member=user)
    assert dpytest.verify().message().content(expected)
