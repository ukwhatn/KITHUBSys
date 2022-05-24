import asyncio
import json
import logging

import discord
from discord.commands import Option, slash_command
from discord.ext import commands, tasks


class MessageDeleteWatcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.author.bot:
            self.logger.info(f"Message deleted in {message.guild.name}/{message.channel.name}, content: {message.content} by {message.author.name}")
            await message.channel.send("このチャンネルでメッセージが削除されました。この操作はログに記録されています。")


def setup(bot):
    return bot.add_cog(MessageDeleteWatcher(bot))
