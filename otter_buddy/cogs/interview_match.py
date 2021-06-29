import random
import discord
import asyncio
import logging
import datetime

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
            except discord.Forbidden:
                logger.error(f"Not permissions to add the role in {__name__}")
            except discord.HTTPException:
                logger.error(f"Adding roles failed in {__name__}")
            except Exception as e:
                logger.error(f"Exception in {__name__}")
                logger.error(e)
            interview_buddy_message: str = (
                f'{role.mention if role else ""}\n'
                'Hello my beloved otters, it is time to practice!\n'
                f'React to this message with {entry["emoji"]} if you want to make a mock interview with another otter.\n'
                'Remeber you only have 24 hours to react. A nice week to all of you and keep coding!'
            )
            channel = self.bot.get_channel(entry["channel_id"])
            message = await channel.send(interview_buddy_message)
            entry["message_id"] = message.id
            db_interview_match.DbInterviewMatch.set_interview_match(entry)
    
    async def check_weekly_message(self):
        weekday = (datetime.datetime.today().weekday() - 1 + 7) % 7
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
                return
            
            week_otter_pairs = self.make_pairs(week_otter_pool, entry["author_id"])
            _img, img_path = create_match_image(week_otter_pairs)
            for otter_one, otter_two in week_otter_pairs:
                await self.send_pair_message(otter_one, otter_two, entry["guild_id"])
                await self.send_pair_message(otter_two, otter_one, entry["guild_id"])

            message = 'These are the pairs of the week.\nPlease get in touch with your partner!'
            await channel.send(message, file=discord.File(img_path))
    
    async def send_pair_message(self, otter_one: discord.User, otter_two: discord.User, guild_id: int):
        username_one = f'{otter_one.name}#{otter_one.discriminator}'
        username_two = f'{otter_two.name}#{otter_two.discriminator}'
        message = (
            f'Hello {username_one}!\n'
            f'You have been paired with {username_two}. Please get in contact with she/he!.\n'
            '*Have fun!*'
        )
        await otter_one.send(message)

        result = db_email.DbEmail.get_mail(otter_one.id, guild_id)
        if not result is None:
            email = result['email']
            conn = EmailConn()
            conn.send_mail(email, "Interview buddy", message)
    
    def make_pairs(self, week_otter_pool: list, author_id: int):
        week_otter_pairs: list = []
        if len(week_otter_pool) % 2 == 1:
            print("Hello")
            author = self.bot.get_user(author_id)
            print(author)
            week_otter_pool.append(author)
        
        random.shuffle(week_otter_pool)
        for idx in range(len(week_otter_pool) // 2):
            week_otter_pairs.append((week_otter_pool[idx*2], week_otter_pool[idx*2+1]))
        
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


def setup(bot):
    bot.add_cog(InterviewMatch(bot))
