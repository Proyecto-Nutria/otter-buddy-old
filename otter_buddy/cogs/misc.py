import discord
import logging
import time

from discord.ext import commands
from humanfriendly import format_timespan as timeez
from psutil import Process, virtual_memory

from otter_buddy import constants
from otter_buddy.utils.db import db_email
from otter_buddy.constants import OTTER_ADMIN, OTTER_MODERATOR, OTTER_ROLE, WELCOME_MESSAGES
from otter_buddy.utils.common import is_valid_email

logger = logging.getLogger(__name__)


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.uptime = int(time.time())

    @commands.command(brief="Reply with the `text` wrote")
    async def echo(self, ctx, *, content:str):
        '''
        Echo will reply your message with the `text` that you wrote next to the command.
        '''
        await ctx.send(content)

    @commands.command(brief="Add your `email` to notifications")
    async def subscribe(self, ctx, email:str):
        '''
        Subscribe to our notifications via email..
        '''
        if is_valid_email(email):
            user = {
                "user_id": ctx.author.id,
                "guild_id": ctx.guild.id,
                "email": email
            }
            result = db_email.DbEmail.set_mail(user)
            msg = "Succesfully subscribed!" if result.matched_count == 0 else "Succesfully updated your subscription!"
            await ctx.send(msg)
        else:
            await ctx.send("Write a valid email")

    @commands.command(brief="Remove your `email` from notifications")
    async def unsubscribe(self, ctx):
        '''
        Unsubscribe from our notifications via email
        '''
        result = db_email.DbEmail.delete_mail(ctx.author.id, ctx.guild.id)
        msg: str = ""
        if result.deleted_count == 1:
            msg = "Succesfully removed your subscription!"
        else:
            msg = "You wasn't subscribed"
        await ctx.send(msg)

    @commands.command()
    async def botinfo(self, ctx):
        guilds = len(self.bot.guilds)
        uptime_ = int(time.time()) - self.uptime

        proc = Process()
        with proc.oneshot():
            mem_total = virtual_memory().total / (1024 ** 3)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)

        embed = discord.Embed(description="A Discord Bot to help you during your preparation process.",
                              color=constants.BRAND_COLOR)
        embed.set_author(name="Bot Stats", icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        embed.add_field(name="Servers", value=f"**{guilds}**", inline=True)
        embed.add_field(name="Uptime", value=f"**{timeez(uptime_)}**", inline=True)
        embed.add_field(name="Memory usage", value=f"{int(mem_usage * 1024)} MB / {mem_total:,.0f} GB ({mem_of_total:.0f}%)",
                        inline=True)
        embed.add_field(name="About", value=f"The Bot is developed by `Proyecto Nutria`, based on discord.py.\n\
                                Please visit the following links to submit ideas or bugs:\n", inline=False)
        embed.add_field(name="GitHub repository", value=f"[GitHub]({constants.GITHUB_LINK})",
                        inline=True)
        embed.add_field(name="Support Server", value=f"[Server]({constants.SERVER_INVITE})",
                        inline=True)

        await ctx.send(embed=embed)

    @commands.Cog.listener(name='on_raw_reaction_add')
    async def reaction_give_role(self, payload: discord.RawReactionActionEvent):
        if not WELCOME_MESSAGES or str(payload.message_id) in WELCOME_MESSAGES:
            try:
                guild = next(guild for guild in self.bot.guilds if guild.id == payload.guild_id)
                role = discord.utils.get(guild.roles, name=OTTER_ROLE)
                if role == None:
                    logger.error(f"Not role found in {__name__} for guild {guild.name}")
                    return
                await discord.Member.add_roles(payload.member, role)
            except StopIteration:
                logger.error(f"Not guild found in {__name__}")
            except discord.Forbidden:
                logger.error(f"Not permissions to add the role in {__name__}")
            except discord.HTTPException:
                logger.error(f"Adding roles failed in {__name__}")
            except Exception as e:
                logger.error(f"Exception in {__name__}")
                logger.error(e)

    @commands.command()
    @commands.has_any_role(OTTER_ADMIN, OTTER_MODERATOR)
    async def reactioncheck(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name=OTTER_ROLE)
        if role == None:
            logger.error(f"Not role found in {__name__} for guild {ctx.guild.name}")
            return
        for message_id in WELCOME_MESSAGES:
            message = None
            for text_channel in ctx.guild.text_channels:
                try:
                    message = await text_channel.fetch_message(message_id)
                    break
                except discord.NotFound:
                    continue
                except discord.Forbidden:
                    logger.error(f"Not permissions to get the message with id {message_id} in {__name__}")
                except discord.HTTPException:
                    logger.error(f"Retrieving the message with id {message_id} failed in {__name__}")
                except Exception as e:
                    logger.error(f"Exception in {__name__}")
                    logger.error(e)
            if not message:
                logger.error(f"The specified message with id {message_id} was not found in {__name__}")
                return

            users = set()
            for reaction in message.reactions:
                try:
                    users_list = await reaction.users().flatten()
                    users.update(users_list)
                except discord.HTTPException:
                    logger.error(f"Retrieving the list of users for message with id {message_id} with reaction {reaction.emoji} failed in {__name__}")
            logger.info(f"Got {len(users)} to add role")
            for user in users:
                try:
                    await discord.Member.add_roles(user, role)
                except discord.Forbidden:
                    logger.error(f"Not permissions to add the role for user {user.id} in {__name__}")
                except discord.HTTPException:
                    logger.error(f"Adding roles for user {user.id} failed in {__name__}")
                except Exception as e:
                    logger.error(f"Exception with {user.display_name} in {__name__}")
                    logger.error(e)


def setup(bot):
    bot.add_cog(Misc(bot))
