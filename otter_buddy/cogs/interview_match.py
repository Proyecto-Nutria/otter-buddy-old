import random
import discord
import asyncio
import logging
import datetime

from typing import List, Tuple

from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from otter_buddy.utils.db import db_email, db_interview_match
from otter_buddy.utils.email.emailconn import EmailConn
from otter_buddy.utils.common import create_match_image
from otter_buddy.constants import OTTER_ADMIN, OTTER_MODERATOR, OTTER_ROLE

logger = logging.getLogger(__name__)


class InterviewMatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduler: AsyncIOScheduler = AsyncIOScheduler()
        self.emoji: str = '👍'
        self.channel: discord.TextChannel = None
        self.message: discord.TextChannel = None
        self.author: discord.User = None
        self.guild: discord.Guild = None

        self.scheduler.add_job(self.send_weekly_message, CronTrigger(hour=12, timezone="America/Mexico_City"))
        self.scheduler.add_job(self.check_weekly_message, CronTrigger(hour=12, timezone="America/Mexico_City"))
        self.scheduler.start()

    @commands.group(brief='Commands related to Interview Match activity!', invoke_without_command=True)
    async def interview_match(self, ctx, *, content:str):
        '''
        Interview Match will help to set up interviews between discord members.
        '''
        await ctx.send_help(ctx.command)
    
    async def send_weekly_message(self):
        weekday = datetime.datetime.today().weekday()
        for entry in db_interview_match.DbInterviewMatch.get_day_interview_match(weekday):
            guild: discord.Guild = None
            role: discord.Role = None
            try:
                guild = next(guild for guild in self.bot.guilds if guild.id == entry["guild_id"])
                role = discord.utils.get(guild.roles, name=OTTER_ROLE)
                if role == None:
                    logger.error(f"Not role found in {__name__} for guild {guild.name}")
                    return
            except StopIteration:
                logger.error(f"Not guild found in {__name__}")
            except Exception as e:
                logger.error(f"Exception in {__name__}")
                logger.error(e)
            finally:
                interview_buddy_message: str = (
                    f'{role.mention if role else ""}\n'
                    'Hello my beloved otters, it is time to practice!\n'
                    f'React to this message with {entry["emoji"]} if you want to make a mock interview with another otter.\n'
                    'Remeber you only have 24 hours to react. A nice week to all of you and keep coding!'
                )
                channel = self.bot.get_channel(entry["channel_id"])
                logger.info(entry["channel_id"])
                logger.info(channel)
                message = await channel.send(interview_buddy_message)
                entry["message_id"] = message.id
                db_interview_match.DbInterviewMatch.set_interview_match(entry)
    
    async def check_weekly_message(self, weekday = None) -> None:
        weekday = (datetime.datetime.today().weekday() - 1 + 7) % 7 if weekday is None else weekday
        for entry in db_interview_match.DbInterviewMatch.get_day_interview_match(weekday):
            logger.info(entry)
            channel = self.bot.get_channel(entry["channel_id"])
            cache_message = await channel.fetch_message(entry["message_id"])
            week_otter_pool = set()
            for reaction in cache_message.reactions:
                if reaction.emoji != entry["emoji"]:
                    continue
                list_users = await reaction.users().flatten()
                for user in list_users:
                    if not user.bot:
                        week_otter_pool.add(user)

            week_otter_pool = list(week_otter_pool)
            if not week_otter_pool:
                await channel.send("No one wanted to practice 😟")
                logger.warning("Empty pool for Interview Match")
                continue
            
            placeholder = channel.guild.get_member(entry["author_id"])
            week_otter_pairs = self.make_pairs(week_otter_pool, placeholder)
            _img, img_path = create_match_image(week_otter_pairs)
            for otter_one, otter_two in week_otter_pairs:
                await self.send_pair_message(otter_one, otter_two, entry["guild_id"])
                await self.send_pair_message(otter_two, otter_one, entry["guild_id"])

            week_otter_pool.sort(key=lambda user: user.display_name) # in-place sort
            users_mentions = ",".join(list(map(lambda user: f"{user.mention}", week_otter_pool)))
            message = 'These are the pairs of the week.\nPlease get in touch with your partner!'
            message += f'\n{users_mentions}'
            await channel.send(message, file=discord.File(img_path))
    
    async def send_pair_message(self, otter_one: discord.User, otter_two: discord.User, guild_id: int):
        username_one = f'{otter_one.name}#{otter_one.discriminator}'
        username_two = f'{otter_two.name}#{otter_two.discriminator}'
        message = (
            f'Hello {username_one}!\n'
            f'You have been paired with {username_two}. Please get in contact with her/him and don\'t forget to request the resume!.\n'
            '*Have fun!*\n\n'
            'Check this message for more information about the activity:\n'
            'https://discord.com/channels/742890088190574634/743138942035034164/859236992403374110'
        )
        try:
            await otter_one.send(message)
        except BaseException as err:
            logger.error(f'Error while sending a message to {username_one}')
            logger.error(f"Unexpected {err=}, {type(err)=}")

        result = db_email.DbEmail.get_mail(otter_one.id, guild_id)
        if not result is None:
            email = result['email']
            conn = EmailConn()
            conn.send_mail(email, "Interview buddy", message)
    
    def make_pairs(self, week_otter_pool: list, placeholder: discord.Member) -> List[Tuple[discord.Member, discord.Member]]:
        week_otter_pairs: list = []
        week_otter_collaborator: list = []
        week_otter_member: list = []
        if len(week_otter_pool) % 2 == 1:
            week_otter_pool.append(placeholder)

        for otter in week_otter_pool:
            str_otter_roles = [str(otter_role) for otter_role in otter.roles]
            if OTTER_MODERATOR in str_otter_roles or OTTER_ADMIN in str_otter_roles:
                week_otter_collaborator.append(otter)
            else:
                week_otter_member.append(otter)

        random.shuffle(week_otter_collaborator)
        random.shuffle(week_otter_member)

        for collaborator, member in list(zip(week_otter_collaborator, week_otter_member)):
            week_otter_pairs.append((collaborator, member))
            week_otter_collaborator.remove(collaborator)
            week_otter_member.remove(member)
        
        for idx in range(len(week_otter_collaborator) // 2):
            week_otter_pairs.append((week_otter_collaborator[idx*2], week_otter_collaborator[idx*2+1]))
        
        for idx in range(len(week_otter_member) // 2):
            week_otter_pairs.append((week_otter_member[idx*2], week_otter_member[idx*2+1]))

        return week_otter_pairs

    @interview_match.command(brief='Start interview match activity', usage='<text_channel> [day_of_week]')
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def start(self, ctx, channel: discord.TextChannel, day_of_week: int = None):
        '''
        Start Interview Match setting up options
        '''
        emoji_selected = self.emoji
        get_emoji_message: str = f'You have 15s to react to this message with the emoji that you want to use (by default is {emoji_selected}).'
        emoji_message = await ctx.send(get_emoji_message)

        def check(reaction, user):
            return reaction.message.id == emoji_message.id and user == ctx.author

        try:
            reaction, _user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
        except asyncio.TimeoutError:
            logger.info("User not reacted to interview_match start")
        else:
            emoji_selected = reaction.emoji
        
        interview_match = {
            "emoji":            emoji_selected,
            "day_of_the_week":  2 if day_of_week is None else day_of_week % 7,
            "channel_id":       channel.id,
            "message_id":       None,
            "author_id":        ctx.author.id,
            "guild_id":         ctx.guild.id,
        }

        db_interview_match.DbInterviewMatch.set_interview_match(interview_match)

        await ctx.send(f"**Interview Match** activity scheduled! See you there {emoji_selected}.")

    @interview_match.command(brief='Stop interview match activity')
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def stop(self, ctx):
        '''
        Stop Interview Match
        '''
        result = db_interview_match.DbInterviewMatch.delete_interview_match(ctx.guild.id)
        msg: str = ""
        if result.deleted_count == 1:
            msg = "**Interview Match** activity stopped!"
        else:
            msg = "No activity was running! 😱"
        await ctx.send(msg)
    
    @interview_match.group(  # type: ignore
    brief="Commands related to trigger manually the Interview Match activity!",
    invoke_without_command=True,
    )   
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def run(self, ctx) -> None:
        """
        Admin commands related to trigger and test the activity
        """
        await ctx.send_help(ctx.command)

    @run.command(brief="Admin command to trigger the send weekly message job")  # type: ignore
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def send(self, _) -> None:
        """
        Admin command that execute the send weekly message method, this is executed as usual
        to all the guilds and for the current day
        """
        await self.send_weekly_message()

    @run.command(brief="Admin command to trigger the check weekly message job")  # type: ignore
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def check(self, _) -> None:
        """
        Admin command that execute the check weekly message method, this is executed as usual
        to all the guilds and for the current day
        """
        await self.check_weekly_message(datetime.datetime.today().weekday())



def setup(bot):
    bot.add_cog(InterviewMatch(bot))
