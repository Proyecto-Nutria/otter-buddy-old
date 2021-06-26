import random
import discord
import asyncio
import logging

from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from otter_buddy.utils.db import db_email
from otter_buddy.utils.email.emailconn import EmailConn
from otter_buddy.utils.common import create_match_image
from otter_buddy.constants import OTTER_ADMIN, OTTER_MODERATOR

logger = logging.getLogger(__name__)


class InterviewMatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduler: AsyncIOScheduler = AsyncIOScheduler()
        self.channel: discord.TextChannel = None
        self.emoji: str = '👍'
        self.message: discord.TextChannel = None
        self.author: discord.User = None
        self.guild: discord.Guild = None

        self.scheduler.start()

    @commands.group(brief='Commands related to Interview Match activity!', invoke_without_command=True)
    async def interview_match(self, ctx, *, content:str):
        '''
        Interview Match will help to set up interviews between discord members.
        '''
        await ctx.send_help(ctx.command)
    
    async def send_weekly_message(self):
        interview_buddy_message: str = (
            'Hello my beloved otters, it is time to practice!\n'
            f'React to this message with {self.emoji} if you want to make a mock interview with another otter.\n'
            'Remeber you only have 24 hours to react. A nice week to all of you and keep coding!'
        )
        self.message = await self.channel.send(interview_buddy_message)
    
    async def check_weekly_message(self):
        cache_message = discord.utils.get(self.bot.cached_messages, id=self.message.id)
        week_otter_pool = set()
        for reaction in cache_message.reactions:
            list_users = await reaction.users().flatten()
            for user in list_users:
                week_otter_pool.add(user)
        week_otter_pool = list(week_otter_pool)
        
        week_otter_pairs = self.make_pairs(week_otter_pool)
        _img, img_path = create_match_image(week_otter_pairs)
        for otter_one, otter_two in week_otter_pairs:
            await self.send_pair_message(otter_one, otter_two)
            await self.send_pair_message(otter_two, otter_one)

        message = 'These are the pairs of the week.\nPlease get in touch with your partner!'
        await self.channel.send(message, file=discord.File(img_path))
    
    async def send_pair_message(self, otter_one: discord.User, otter_two: discord.User):
        username_one = f'{otter_one.name}#{otter_one.discriminator}'
        username_two = f'{otter_two.name}#{otter_two.discriminator}'
        message = (
            f'Hello {username_one}!\n'
            f'You have been paired with {username_two}. Please get in contact with she/he!.\n'
            '*Have fun!*'
        )
        await otter_one.send(message)

        result = db_email.DbEmail.get_mail(otter_one.id, self.guild.id)
        if not result is None:
            email = result['email']
            conn = EmailConn()
            conn.send_mail(email, "Interview buddy", message)
    
    def make_pairs(self, week_otter_pool: list):
        week_otter_pairs: list = []
        if len(week_otter_pool) % 2 == 1:
            week_otter_pool.append(self.author)
        
        random.shuffle(week_otter_pool)
        for idx in range(len(week_otter_pool) // 2):
            week_otter_pairs.append((week_otter_pool[idx], week_otter_pool[idx+1]))
        
        return week_otter_pairs

        

    @interview_match.command(brief='Start interview match activity', usage='<text_channel> [day_of_week]')
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def start(self, ctx, channel: discord.TextChannel, day_of_week: int = None):
        '''
        Start Interview Match setting up options
        '''
        get_emoji_message: str = f'You have 15s to react to this message with the emoji that you want to use (by default is {self.emoji}).'
        emoji_message = await ctx.send(get_emoji_message)

        def check(reaction, user):
            return reaction.message.id == emoji_message.id and user == ctx.author

        try:
            reaction, _user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
        except asyncio.TimeoutError:
            logger.info("User not reacted to interview_match start")
        else:
            self.emoji = reaction.emoji
        
        self.author = ctx.author
        self.channel = channel
        self.guild = ctx.guild
        self.scheduler.remove_all_jobs()
        self.scheduler.add_job(self.send_weekly_message, CronTrigger(day_of_week=day_of_week, hour=12, timezone="America/Mexico_City"))
        self.scheduler.add_job(self.check_weekly_message, CronTrigger(day_of_week=((((day_of_week + 1) % 7) + 7) % 7), hour=12, timezone="America/Mexico_City"))


def setup(bot):
    bot.add_cog(InterviewMatch(bot))
