import discord

from discord.ext import commands
from discord.ext.commands import BucketType

from otter_buddy.constants import SERVER_INVITE, GITHUB_LINK, PREFIX, BRAND_COLOR


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.remove_command("help")

    def make_help_embed(self, ctx):
        headers = "Information about commands are given below!\nFor general information about the bot,  type `{}botinfo`".format(PREFIX)
        misc = ['echo', 'subscribe', 'unsubscribe']
        interview_match = self.client.get_command('interview_match')
        interview_reminder = self.client.get_command('interview_reminder')
        footers = "\n```cpp\nReact to change pages"


        content = []

        desc = "\n\n:otter: Misc related commands\n\n"
        for cmd in list(map(lambda name: self.client.get_command(name), misc)):
            desc += f"`{cmd.name}`: **{cmd.brief}**\n"
        content.append(desc)
        footers += "\nPage 1: Misc related commands"
        
        desc = "\n\n:otter: Interview Match related commands\n\n"
        for cmd in interview_match.commands:
            desc += f"`{cmd.name}`: **{cmd.brief}**\n"
        content.append(desc)
        footers += "\nPage 2: Interview Match related commands"
        
        desc = "\n\n:otter: Interview Reminder related commands\n\n"
        for cmd in interview_reminder.commands:
            desc += f"`{cmd.name}`: **{cmd.brief}**\n"
        content.append(desc)
        footers += "\nPage 3: Interview Reminder related commands"

        footers += "```"
        embeds = []
        for desc in content:
            embed = discord.Embed(description=headers + desc + footers, color=BRAND_COLOR)
            embed.set_author(name="Otter-Buddy commands help", icon_url=ctx.me.avatar_url)
            embed.set_footer(
                text="Use the prefix *{}* before each command. For detailed usage about a particular command, type {}help <command>".format(PREFIX, PREFIX))
            embeds.append(embed)

        return embeds

    def make_cmd_embed(self, command):
        usage = f"{PREFIX}{str(command)} "
        params = []
        for key, value in command.params.items():
            if key not in ['self', 'ctx']:
                params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")
        usage += ' '.join(params)
        aliases = [str(command), *command.aliases]
        embed = discord.Embed(title=f"Information about {str(command)}", color=BRAND_COLOR)
        embed.add_field(name="Description", value=command.brief, inline=False)
        embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
        embed.add_field(name="Aliases", value=f"{' '.join([f'`{x}`' for x in aliases])}", inline=False)
        return embed

    @commands.command(name="help")
    @commands.cooldown(1, 5, BucketType.user)
    async def help(self, ctx, *, cmd: str=None):
        """Shows help for various commands"""
        if cmd is None:
            embeds = self.make_help_embed(ctx)
            emotes = ['1️⃣', '2️⃣', '3️⃣']
            msg = await ctx.send(embed=embeds[0])
            for emote in emotes:
                await msg.add_reaction(emote)

            def check(reaction, user):
                return reaction.message.id == msg.id and reaction.emoji in emotes and user != self.client.user

            while True:
                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=60, check=check)
                    try:
                        await reaction.remove(user)
                    except Exception:
                        pass
                    await msg.edit(embed=embeds[emotes.index(reaction.emoji)])
                except Exception:
                    break
        else:
            command = self.client.get_command(cmd)
            if command is None or command.hidden:
                await ctx.author.send(f"{ctx.author.mention} that command does not exists")
                return
            await ctx.send(embed=self.make_cmd_embed(command))


def setup(client):
    client.add_cog(Help(client))