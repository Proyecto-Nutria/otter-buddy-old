import discord
import logging
import datetime

from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from otter_buddy.utils.db import db_interview_reminder
from otter_buddy.constants import OTTER_ADMIN, OTTER_MODERATOR, BRAND_COLOR

logger = logging.getLogger(__name__)


class InterviewReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduler: AsyncIOScheduler = AsyncIOScheduler()
        self.emoji: str = '👍'
        self.channel: discord.TextChannel = None
        self.message: discord.TextChannel = None
        self.author: discord.User = None
        self.guild: discord.Guild = None

        self.scheduler.add_job(self.send_scheduled_message, CronTrigger(hour=12, timezone="America/Mexico_City"))
        self.scheduler.start()

    @commands.group(brief='Commands related to set reminders for interviews!', invoke_without_command=True)
    async def interview_reminder(self, ctx, *, content:str):
        '''
        Interview Reminder will help to keep people aware of your activities.
        '''
        await ctx.send_help(ctx.command)

    async def send_scheduled_message(self):
        weekday = datetime.datetime.today().weekday()
        for entry in db_interview_reminder.DbInterviewReminder.get_day_interview_reminder(weekday):
            try:
                guild = next(guild for guild in self.bot.guilds if guild.id == entry["guild_id"])
            except StopIteration:
                logger.error(f"Not guild found in {__name__}")
            except Exception as e:
                logger.error(f"Exception in {__name__}")
                logger.error(e)
            finally:
                reminder_message: str = (
                    f'{entry["role_mention"]}\n'
                    f'{entry["message"]}'
                )
                embed = discord.Embed(description=reminder_message, color=BRAND_COLOR)
                channel = self.bot.get_channel(entry["channel_id"])
                await channel.send(embed=embed)

    @interview_reminder.command(brief='Start interview reminder', usage='<text_channel> [message_id] [role] [day_of_week]')
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def start(self, ctx, channel: discord.TextChannel, message_id: int, role: discord.Role = None, day_of_week: int = None):
        '''
        Start Interview Reminder setting up options, use the message id to refer the template that will be sent each time \
        (keep in mind that this message need to be in the same channel where you're invoking this command). The channel, \
        role and day of the week is configuration about how to send the reminder.
        '''
        cache_message = await ctx.fetch_message(message_id)
        
        interview_reminder = {
            "day_of_the_week":  5 if day_of_week is None else day_of_week % 7,
            "channel_id":       channel.id,
            "role_mention":     '' if role is None else role.mention,
            "message":          cache_message.content,
            "guild_id":         ctx.guild.id,
        }

        db_interview_reminder.DbInterviewReminder.set_interview_reminder(interview_reminder)

        await ctx.send(f"**Interview Reminder** scheduled! Let me do the boring job.")

    @interview_reminder.command(brief='Stop interview reminder')
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def stop(self, ctx):
        '''
        Stop Interview Reminder
        '''
        result = db_interview_reminder.DbInterviewReminder.delete_interview_reminder(ctx.guild.id)
        msg: str = ""
        if result.deleted_count == 1:
            msg = "**Interview Reminder** stopped!"
        else:
            msg = "No reminder was set! 😱"
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(InterviewReminder(bot))
