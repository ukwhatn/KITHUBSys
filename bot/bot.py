import logging
import time

import discord
from discord.ext import commands

from config import bot_config

while bot_config.TOKEN is None or bot_config.OWNER_ID is None:
    time.sleep(3)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s] %(message)s"
)

# bot init
bot = commands.Bot(help_command=None,
                   case_insensitive=True,
                   activity=discord.Game("©Yuki Watanabe"),
                   intents=discord.Intents.all()
                   )

bot.load_extension("cogs.Admin")
bot.load_extension("cogs.ThreadKeeper")
#bot.load_extension("cogs.MessageDeleteWatcher")
bot.load_extension("cogs.MessageDeleter")
bot.load_extension("cogs.PinMessage")
bot.load_extension("cogs.MessageExtractor")


bot.run(bot_config.TOKEN)
