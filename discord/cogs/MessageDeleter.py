import logging

import discord
from discord.commands import slash_command
from discord.ext import commands

from db.package.crud import discord_message_delete_targets as db_crud
from db.package.session import get_db


class MessageDeleter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(type(self).__name__)

    @slash_command(name="set_to_delete_target", description="このChに送信されるメッセージをすべて削除")
    @commands.has_permissions(ban_members=True)
    async def set_to_delete_target(self, ctx: discord.commands.context.ApplicationContext):
        with get_db() as db:
            db_crud.create(db, ctx.guild.id, ctx.channel.id)

        await ctx.respond("今後このチャンネルに送信されるすべてのメッセージを削除します。", ephemeral=True)

    @slash_command(name="remove_from_delete_target", description="削除対象から外す")
    @commands.has_permissions(ban_members=True)
    async def remove_from_delete_target(self, ctx: discord.commands.context.ApplicationContext):
        with get_db() as db:
            db_crud.delete(db, ctx.guild.id, ctx.channel.id)

        await ctx.respond("メッセージの自動削除を無効化しました。", ephemeral=True)

    @staticmethod
    def is_delete_target(message: discord.Message):
        if message.channel.type in (discord.ChannelType.private, discord.ChannelType.group):
            return False

        with get_db() as db:
            targets = db_crud.get_targets_by_guild_id(db, message.guild.id)

        if targets is None or len(targets) == 0:
            return False

        return message.channel.id in [t.channel_id for t in targets]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.bot and self.is_delete_target(message):
            await message.delete(reason="AutoDelete")
            self.logger.info(
                f"Deleted: {message.guild.name}/{message.channel.name}/{message.content}, by {message.author.name}")


def setup(bot):
    return bot.add_cog(MessageDeleter(bot))
