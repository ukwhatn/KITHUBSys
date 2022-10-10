import json
import json
import logging

import discord
from discord.commands import slash_command
from discord.ext import commands

from util.dataio import DataIO


class MessageDeleter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    @slash_command(name="set_to_delete_target", description="このChに送信されるメッセージをすべて削除")
    @commands.has_permissions(ban_members=True)
    async def set_to_delete_target(self, ctx: discord.commands.context.ApplicationContext):
        DataIO.set_delete_target(ctx.guild.id, ctx.channel.id)
        await ctx.respond("今後このチャンネルに送信されるすべてのメッセージを削除します。")

    @slash_command(name="remove_from_delete_target", description="削除対象から外す")
    @commands.has_permissions(ban_members=True)
    async def remove_from_delete_target(self, ctx: discord.commands.context.ApplicationContext):
        DataIO.remove_delete_target(ctx.guild.id, ctx.channel.id)
        await ctx.respond("メッセージの自動削除を無効化しました。")

    def is_delete_target(self, message: discord.Message):
        targets = DataIO.get_delete_targets_in_guild(message.guild.id)
        if targets is None:
            return False
        return message.channel.id in targets

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.bot and self.is_delete_target(message):
            await message.delete(reason="AutoDelete")
            self.logger.info(f"Deleted: {message.guild.name}/{message.channel.name}/{message.content}, by {message.author.name}")


def setup(bot):
    return bot.add_cog(MessageDeleter(bot))
