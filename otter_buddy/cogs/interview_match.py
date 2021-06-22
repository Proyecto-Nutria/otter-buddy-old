import discord
import asyncio
import logging

from discord.ext import commands

from otter_buddy.data import db_email
from otter_buddy.constants import OTTER_ADMIN, OTTER_MODERATOR

logger = logging.getLogger(__name__)


class InterviewMatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(brief='Commands related to Interview Match activity!', invoke_without_command=True)
    async def interview_match(self, ctx, *, content:str):
        '''
        Interview Match will help to set up interviews between discord members.
        '''
        await ctx.send_help(ctx.command)

    @interview_match.command(brief='Start interview match activity', usage='<text_channel> [day_of_week]')
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def start(self, ctx, channel: discord.TextChannel, day_of_week: int = None):
        '''
        Start Interview Match setting up options
        '''
        emoji = '👍'
        get_emoji_message: str = f'You have 15s to react to this message with the emoji that you want to use (by default is {emoji}).'
        emoji_message = await ctx.send(get_emoji_message)

        def check(reaction, user):
            return reaction.message.id == emoji_message.id and user == ctx.author

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=15, check=check)
        except asyncio.TimeoutError:
            logger.info("User not reacted to interview_match start")
        else:
            emoji = reaction.emoji


def setup(bot):
    bot.add_cog(InterviewMatch(bot))
