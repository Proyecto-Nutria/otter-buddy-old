import asyncio
import logging
import functools
import random
import datetime

import discord
from discord.ext import commands

from otter_buddy import constants

logger = logging.getLogger(__name__)

_OTTER_COLORS = (0x007A7A, 0x0099A2, 0xB8EAEA)
_SUCCESS_GREEN = 0x28A745
_ALERT_AMBER = 0xFFBF00


def embed_neutral(desc, color=discord.Embed.Empty):
    return discord.Embed(description=str(desc), color=color)


def embed_success(desc):
    return discord.Embed(description=str(desc), color=_SUCCESS_GREEN)


def embed_alert(desc):
    return discord.Embed(description=str(desc), color=_ALERT_AMBER)


def random_cf_color():
    return random.choice(_OTTER_COLORS)


def cf_color_embed(**kwargs):
    return discord.Embed(**kwargs, color=random_cf_color())


def set_same_cf_color(embeds):
    color = random_cf_color()
    for embed in embeds:
        embed.color=color


def attach_image(embed, img_file):
    embed.set_image(url=f'attachment://{img_file.filename}')


def set_author_footer(embed, user):
    embed.set_footer(text=f'Requested by {user}', icon_url=user.avatar_url)


def send_error_if(*error_cls):
    """Decorator for `cog_command_error` methods. Decorated methods send the error in an alert embed
    when the error is an instance of one of the specified errors, otherwise the wrapped function is
    invoked.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(cog, ctx, error):
            if isinstance(error, error_cls):
                await ctx.send(embed=embed_alert(error))
                error.handled = True
            else:
                await func(cog, ctx, error)
        return wrapper
    return decorator


async def bot_error_handler(ctx: discord.ext.commands.Context, error: Exception):
    if isinstance(error, commands.CommandNotFound):
        pass
    
    if getattr(error, 'handled', False):
        # Errors already handled in cogs should have .handled = True
        return

    if isinstance(error, commands.CommandOnCooldown):
        tot = error.cooldown.per
        rem = error.retry_after
        msg = f"{ctx.author.mention} That command has a default cooldown of {str(datetime.timedelta(seconds=tot)).split('.')[0]}.\n"
        msg += f"Please retry after {str(datetime.timedelta(seconds=rem)).split('.')[0]}."
        embed = discord.Embed(description=msg, color=discord.Color.red())
        embed.set_author(name=f"Slow down!")
        await ctx.author.send(embed=embed)
    elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
        command = ctx.command
        command.reset_cooldown(ctx)
        usage = f"`{constants.PREFIX}{str(command)} "
        params = []
        for key, value in command.params.items():
            if key not in ['self', 'ctx']:
                params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")
        usage += ' '.join(params)
        usage += '`'
        if command.help:
            usage += f"\n\n{command.help}"
        await ctx.author.send(embed=discord.Embed(description=f"The correct usage is: {usage}", color=discord.Color.gold()))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.author.send(f"{str(error)}")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.author.send(embed=embed_alert('Commands are disabled in private channels'))
    elif isinstance(error, commands.DisabledCommand):
        await ctx.author.send(embed=embed_alert('Sorry, this command is temporarily disabled'))
    elif isinstance(error, commands.CommandNotFound):
        await ctx.author.send(embed=embed_alert('Oops! Looks like your command doesn\' exist, type `&help` to learn more'))
    else:
        msg = 'Ignoring exception in command {}:'.format(ctx.command)
        exc_info = type(error), error, error.__traceback__
        extra = {
            "message_content": ctx.message.content,
            "jump_url": ctx.message.jump_url
        }
        logger.exception(msg, exc_info=exc_info, extra=extra)


def once(func):
    """Decorator that wraps the given async function such that it is executed only once."""
    first = True

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        nonlocal first
        if first:
            first = False
            await func(*args, **kwargs)

    return wrapper


def on_ready_event_once(bot):
    """Decorator that uses bot.event to set the given function as the bot's on_ready event handler,
    but does not execute it more than once.
    """
    def register_on_ready(func):
        @bot.event
        @once
        async def on_ready():
            await func()

    return register_on_ready
