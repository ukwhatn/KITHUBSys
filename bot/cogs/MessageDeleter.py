import json
import json
import logging

import discord
from discord.commands import slash_command
from discord.ext import commands


class MessageDeleter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    def get_delete_targets(self) -> dict:
        with open("/opt/delete_targets.json", "r") as f:
            return {int(key): data for key, data in json.load(f).items()}

    def set_delete_targets(self, data: dict):
        with open("/opt/delete_targets.json", "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @slash_command(name="set_to_delete_target", guild_ids=[958663674216718366, 490892087668244480])
    @commands.has_permissions(ban_members=True)
    async def set_to_delete_target(self, ctx: discord.commands.context.ApplicationContext):
        delete_targets = self.get_delete_targets()  # type: dict[int: list[int]]

        if ctx.guild.id not in delete_targets:
            delete_targets[ctx.guild.id] = []

        if ctx.channel.id not in delete_targets[ctx.guild.id]:
            delete_targets[ctx.guild.id].append(ctx.channel.id)

        self.set_delete_targets(delete_targets)

        await ctx.respond("今後このチャンネルに送信されるすべてのメッセージを削除します。")

    @slash_command(name="remove_from_delete_target", guild_ids=[958663674216718366, 490892087668244480])
    @commands.has_permissions(ban_members=True)
    async def remove_from_delete_target(self, ctx: discord.commands.context.ApplicationContext):
        delete_targets = self.get_delete_targets()  # type: dict[int: list[int]]

        if ctx.guild.id in delete_targets and ctx.channel.id in delete_targets[ctx.guild.id]:
            delete_targets[ctx.guild.id].remove(ctx.channel.id)

        self.set_delete_targets(delete_targets)

        await ctx.respond("メッセージの自動削除を無効化しました。")

    def is_delete_target(self, message: discord.Message):
        delete_targets = self.get_delete_targets()  # type: dict[int: list[int]]
        if message.guild is not None and message.channel is not None:
            if message.guild.id in delete_targets and message.channel.id in delete_targets[message.guild.id]:
                return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.bot and self.is_delete_target(message):
            await message.delete(reason="AutoDelete")
            self.logger.info(f"Deleted: {message.guild.name}/{message.channel.name}/{message.content}, by {message.author.name}")


def setup(bot):
    return bot.add_cog(MessageDeleter(bot))
