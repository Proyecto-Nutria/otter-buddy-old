import os
import logging
from dotenv import load_dotenv
from os import environ
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

import discord
from discord.ext.commands import Bot, when_mentioned_or, NoPrivateMessage

from otter_buddy import constants
from otter_buddy.utils import discord_common


def setup() -> None:
    # Load enviroment variables.
    load_dotenv()

    # Make required directories.
    for path in constants.ALL_DIRS:
        os.makedirs(path, exist_ok=True)

    # Logging to console and file on daily interval
    logging.basicConfig(format='{asctime}:{levelname}:{name}:{message}', style='{',
                        datefmt='%d-%m-%Y %H:%M:%S', level=logging.INFO,
                        handlers=[logging.StreamHandler(),
                                  TimedRotatingFileHandler(constants.LOG_FILE_PATH, when='D',
                                                           backupCount=3, utc=True)])


def main() -> None:
    setup()

    token: str = environ.get('BOT_TOKEN')
    if not token:
        logging.error('Token required')
        return
    
    # Gateway requested by Discord to allow usage from users
    intents: discord.Intents = discord.Intents.all()
    intents.bans = False
    intents.dm_typing = False
    intents.emojis = False
    intents.guild_typing = False
    intents.integrations = False
    intents.presences = False
    intents.typing = False
    intents.webhooks = False
    bot: Bot = Bot(
        case_insensitive=True, 
        description="Otter-Buddy Bot", 
        command_prefix=when_mentioned_or(constants.PREFIX), 
        intents=intents,
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="{}help".format(constants.PREFIX)
        )
    )

    # Load collections of commands, listeners, etc.
    cogs: [str] = [file.stem for file in Path('otter_buddy', 'cogs').glob('*.py')]
    for extension in cogs:
        bot.load_extension(f'otter_buddy.cogs.{extension}')
    logging.info(f'Cogs loaded: {", ".join(bot.cogs)}')

    # Restrict bot usage to inside guild channels only.
    def no_dm_check(ctx):
        if ctx.guild is None:
            raise NoPrivateMessage('Private messages not permitted.')
        return True
    bot.add_check(no_dm_check)

    bot.add_listener(discord_common.bot_error_handler, name='on_command_error')

    bot.run(token)


if __name__ == '__main__':
    main()
