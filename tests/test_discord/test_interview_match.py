import datetime

import discord
import discord.ext.test as dpytest
import pytest
import mongomock
from unittest.mock import patch
from email.message import EmailMessage

from otter_buddy import constants
from otter_buddy.cogs import interview_match
from otter_buddy.utils.db import dbconn, db_interview_match, db_email


mock_connection = mongomock.MongoClient('mongodb://localhost:27021')

def mock_client(self):
    self.connection = mock_connection
    return self

@pytest.fixture(autouse=True)
def interview_match_cog(bot: discord.ext.commands.Bot):
    interview_match_cog = interview_match.InterviewMatch(bot)
    bot.add_cog(interview_match_cog)
    dpytest.configure(bot, 2, 2, 2)
    print("Tests starting")
    return interview_match_cog


# === TESTING ===

@patch.object(dbconn.DbConn, '__enter__', mock_client)
@pytest.mark.asyncio
async def test_send_weekly_message(interview_match_cog):
    config = dpytest.get_config()
    guild: discord.Guild = config.guilds[0]
    channel: discord.TextChannel = config.channels[0]
    member: discord.Member = config.members[0]
    role: discord.Role = dpytest.backend.make_role(name=constants.OTTER_ROLE, guild=guild)
    dpytest.backend.update_guild(guild=guild, roles=guild.roles.extend([role]))
    interview_match = {
        "emoji":            '👍',
        "day_of_the_week":  datetime.datetime.today().weekday(),
        "channel_id":       channel.id,
        "message_id":       None,
        "author_id":        member.id,
        "guild_id":         guild.id,
    }
    db_interview_match.DbInterviewMatch.set_interview_match(interview_match)

    await interview_match_cog.send_weekly_message()

    result = db_interview_match.DbInterviewMatch.get_interview_match(guild.id)
    assert result['message_id'] is not None

    expected: str = (
        f'{role.mention if role else ""}\n'
        'Hello my beloved otters, it is time to practice!\n'
        f'React to this message with 👍 if you want to make a mock interview with another otter.\n'
        'Remeber you only have 24 hours to react. A nice week to all of you and keep coding!'
    )
    assert dpytest.verify().message().content(expected)

    db_interview_match.DbInterviewMatch.delete_interview_match(guild.id)

# TODO: Add full test, waiting for dpytest to add flatten method.
@patch.object(dbconn.DbConn, '__enter__', mock_client)
@pytest.mark.asyncio
async def test_check_weekly_message_empty(interview_match_cog):
    config = dpytest.get_config()
    guild: discord.Guild = config.guilds[0]
    channel: discord.TextChannel = config.channels[0]
    member: discord.Member = config.members[0]
    message: discord.Message = dpytest.backend.make_message(content="This is a test message", author=member, channel=channel)
    interview_match = {
        "emoji":            '😀',
        "day_of_the_week":  ((datetime.datetime.today().weekday() - 1 + 7) % 7),
        "channel_id":       channel.id,
        "message_id":       message.id,
        "author_id":        member.id,
        "guild_id":         guild.id,
    }
    db_interview_match.DbInterviewMatch.set_interview_match(interview_match)

    await interview_match_cog.check_weekly_message()

    expected: str = "No one wanted to practice 😟"
    assert dpytest.verify().message().content(expected)

    db_interview_match.DbInterviewMatch.delete_interview_match(guild.id)

@patch.object(dbconn.DbConn, '__enter__', mock_client)
@pytest.mark.asyncio
async def test_send_pair_message(interview_match_cog):
    config = dpytest.get_config()
    otter_one: discord.Member = config.members[0]
    otter_two: discord.Member = config.members[1]
    guild: discord.Guild = config.guilds[0]
    email = 'test@test.com'

    user = {
        "user_id": otter_one.id,
        "guild_id": guild.id,
        "email": email
    }
    db_email.DbEmail.set_mail(user)

    username_one = f'{otter_one.name}#{otter_one.discriminator}'
    username_two = f'{otter_two.name}#{otter_two.discriminator}'
    expected_subject = "Interview buddy"
    expected_message = (
        f'Hello {username_one}!\n'
        f'You have been paired with {username_two}. Please get in contact with her/him and don\'t forget to request the resume!.\n'
        '*Have fun!*\n\n'
        'Check this message for more information about the activity:\n'
        'https://discord.com/channels/742890088190574634/743138942035034164/859236992403374110'
    )
    expected_email = EmailMessage()
    expected_email.set_content(expected_message)
    expected_email["Subject"] = expected_subject
    expected_email["From"] = constants.MAIL_USER
    expected_email["To"] = email

    with patch('smtplib.SMTP_SSL', autospec=True) as mock_smtp:
        await interview_match_cog.send_pair_message(otter_one, otter_two, guild.id)

        mock_smtp.assert_called()

        context = mock_smtp.return_value.__enter__.return_value
        context.ehlo.assert_called()
        context.login.assert_called()
        context.sendmail.assert_called_with(constants.MAIL_USER, email, expected_email.as_string())

    assert dpytest.verify().message().content(expected_message)

    db_email.DbEmail.delete_mail(otter_one.id, guild.id)
    db_interview_match.DbInterviewMatch.delete_interview_match(guild.id)

@pytest.mark.asyncio
async def test_make_pairs_complete(interview_match_cog):
    config = dpytest.get_config()
    otter_one: discord.Member = config.members[0]
    otter_two: discord.Member = config.members[1]

    week_otter_pool = [otter_one, otter_two]

    result = interview_match_cog.make_pairs(week_otter_pool, otter_one.id)
    result_flatten = [item for tup in result for item in tup]
    result_flatten.sort(key=lambda otter: otter.id)
    week_otter_pool.sort(key=lambda otter: otter.id)

    assert week_otter_pool == result_flatten

@pytest.mark.asyncio
async def test_make_pairs_incomplete(interview_match_cog):
    config = dpytest.get_config()
    otter_one: discord.Member = config.members[0]
    otter_two: discord.Member = config.members[1]

    week_otter_pool = [otter_two]

    result = interview_match_cog.make_pairs(week_otter_pool, otter_one.id)
    result_flatten = [item.id for tup in result for item in tup]
    result_flatten.sort()
    expected_list = [otter_one.id, otter_two.id]
    expected_list.sort()

    assert expected_list == result_flatten

@patch.object(dbconn.DbConn, '__enter__', mock_client)
@pytest.mark.asyncio
async def test_succesfully_stop(interview_match_cog):
    config = dpytest.get_config()
    user: discord.Member = config.members[0]
    guild: discord.Guild = config.guilds[0]
    channel: discord.TextChannel = config.channels[0]
    role: discord.Role = dpytest.backend.make_role(name=constants.OTTER_MODERATOR, guild=guild)
    extended_roles = user.roles
    extended_roles.append(role)
    dpytest.backend.update_guild(guild=guild, roles=guild.roles.extend([role]))
    dpytest.backend.update_member(member=user, roles=extended_roles)

    interview_match = {
        "emoji":            '👍',
        "day_of_the_week":  1,
        "channel_id":       channel.id,
        "message_id":       None,
        "author_id":        user.id,
        "guild_id":         guild.id,
    }
    db_interview_match.DbInterviewMatch.set_interview_match(interview_match)

    result = db_interview_match.DbInterviewMatch.get_interview_match(guild.id)
    assert result["guild_id"] == guild.id

    expected: str = "**Interview Match** activity stopped!"
    await dpytest.message(f'{constants.PREFIX}interview_match stop', channel=channel, member=user)
    assert dpytest.verify().message().content(expected)

    result = db_interview_match.DbInterviewMatch.get_interview_match(guild.id)
    assert result is None

@patch.object(dbconn.DbConn, '__enter__', mock_client)
@pytest.mark.asyncio
async def test_unsuccesfully_stop(interview_match_cog):
    config = dpytest.get_config()
    user: discord.Member = config.members[0]
    guild: discord.Guild = config.guilds[0]
    channel: discord.TextChannel = config.channels[0]
    role: discord.Role = dpytest.backend.make_role(name=constants.OTTER_MODERATOR, guild=guild)
    extended_roles = user.roles
    extended_roles.append(role)
    dpytest.backend.update_guild(guild=guild, roles=guild.roles.extend([role]))
    dpytest.backend.update_member(member=user, roles=extended_roles)

    expected: str = "No activity was running! 😱"
    await dpytest.message(f'{constants.PREFIX}interview_match stop', channel=channel, member=user)
    assert dpytest.verify().message().content(expected)
