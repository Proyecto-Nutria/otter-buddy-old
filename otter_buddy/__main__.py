import argparse
import asyncio
import distutils.util
import logging
import os
import discord
from dotenv import load_dotenv
from logging.handlers import TimedRotatingFileHandler
from os import environ
from pathlib import Path

from discord.ext.commands import Bot, when_mentioned_or, NoPrivateMessage

from otter_buddy import constants
from otter_buddy.utils import discord_common


def setup():
    # Load enviroment variables.
    load_dotenv()

    # Make required directories.
    for path in constants.ALL_DIRS:
        os.makedirs(path, exist_ok=True)

    # logging to console and file on daily interval
    logging.basicConfig(format='{asctime}:{levelname}:{name}:{message}', style='{',
                        datefmt='%d-%m-%Y %H:%M:%S', level=logging.INFO,
                        handlers=[logging.StreamHandler(),
                                  TimedRotatingFileHandler(constants.LOG_FILE_PATH, when='D',
                                                           backupCount=3, utc=True)])


def main():
    setup()

    token = environ.get('BOT_TOKEN')
    if not token:
        logging.error('Token required')
        return
    
    intents = discord.Intents.default()

    bot = Bot(case_insensitive=True, description="Otter-Buddy Bot", command_prefix=when_mentioned_or(constants.PREFIX), intents=intents)
    cogs = [file.stem for file in Path('otter_buddy', 'cogs').glob('*.py')]
    for extension in cogs:
        bot.load_extension(f'otter_buddy.cogs.{extension}')
    logging.info(f'Cogs loaded: {", ".join(bot.cogs)}')

    def no_dm_check(ctx):
        if ctx.guild is None:
            raise NoPrivateMessage('Private messages not permitted.')
        return True

    # Restrict bot usage to inside guild channels only.
    bot.add_check(no_dm_check)

    # on_ready event handler rather than an on_ready listener.
    @discord_common.on_ready_event_once(bot)
    async def init():
        asyncio.create_task(discord_common.presence(bot))

    bot.add_listener(discord_common.bot_error_handler, name='on_command_error')
    bot.run(token)


if __name__ == '__main__':
    main()
