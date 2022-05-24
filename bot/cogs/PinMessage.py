import json
import json
import logging

import discord
from discord.commands import slash_command
from discord.ext import commands


class PinMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # type: discord.Client
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.emoji.name == "📌":
            channel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = await self.bot.fetch_user(payload.user_id)
            if user.id == message.author.id:
                await message.pin()
                self.logger.info(f"Pinned: {message.guild.name}/{message.channel.name}/{message.content}, by {user.name}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.emoji.name == "📌":
            channel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = await self.bot.fetch_user(payload.user_id)
            if user.id == message.author.id:
                await message.unpin()
                self.logger.info(f"Unpinned: {message.guild.name}/{message.channel.name}/{message.content}, by {user.name}")


def setup(bot):
    return bot.add_cog(PinMessage(bot))
