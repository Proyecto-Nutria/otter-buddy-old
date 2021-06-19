# Otter-Buddy
![Tests](https://github.com/Proyecto-Nutria/otter-buddy/workflows/Test/badge.svg)

Discord bot to help you to prepare for your interviews.

## Features

1. Give Discord role when reacted to messages

## Usage

### Dependencies

Now all dependencies need to be installed. **otter-buddy** uses [Poetry](https://python-poetry.org/) to manage its python dependencies. After installing Poetry navigate to the root of the repo and run

> :warning: **otter-buddy requires Python 3.7 and Poetry 1.1.6!**

### Setup

```sh
# Install dependencies
poetry install
```

#### Environment Variables

Fill in appropriate variables in new "environment" (`.env`) file.

- **BOT_TOKEN**: the Discord Bot Token for your bot.
- **LOGGING_CHANNEL**: the [Discord Channel ID](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-) of a Discord Channel where you want error messages sent to.
- **MONGO_URI**: address of the [MongoDB](https://www.mongodb.com/cloud/atlas) cluster.
- **WELCOME_MESSAGES**: [`message ids`](https://discord.com/developers/docs/resources/channel#message-object-message-structure) separated by `,` that give `OTTER_ROLE` when reacted to.
- **OTTER_ADMIN**: Discord role that give access to admin role based commands.
- **OTTER_MODERATOR**: Discord role that give access to moderator role based commands.
- **OTTER_ROLE**: Discord role to give when reacted to `WELCOME_MESSAGES`.

#### Constants

Modify the constants ([constants file](/otter_buddy/constants.py)) setting properly for you.

- **SERVER_INVITE**: Discord server where the users can look for help.
- **BOT_INVITE**: link to invite your bot to them servers.
- **GITHUB_LINK**: GitHub repository where the users can suggest features or report bugs.
- **LOGS_DIR**: folder where the logs are going to be saved.
- **LOG_FILE_PATH**: use the filename `otter-buddy.log` by default to save the logs.
- **ALL_DIRS**: this can be omitted, only is used to know which folders needs to create.
- **PREFIX**: character or string to be used as prefix for the bot.
- **BRAND_COLOR**: color used in the embedded messages.

### Run

```sh
# Run the bot
poetry run python -m otter_buddy
```
