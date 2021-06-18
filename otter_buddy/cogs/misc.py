import discord
import logging
import time

from discord.ext import commands
from humanfriendly import format_timespan as timeez
from psutil import Process, virtual_memory

from otter_buddy import constants
from otter_buddy.data import dbconn
from otter_buddy.constants import OTTER_ROLE

logger = logging.getLogger(__name__)


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.uptime = int(time.time())

    @commands.command(brief="Reply with the `text` wrote", usage='<text>')
    async def echo(self, ctx, *, content:str):
        '''
        Echo will reply your message with the `text` that you wrote next to the command.
        '''
        await ctx.send(content)

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
        except:
            logger.error(f"Exception in {__name__}")


def setup(bot):
    bot.add_cog(Misc(bot))
