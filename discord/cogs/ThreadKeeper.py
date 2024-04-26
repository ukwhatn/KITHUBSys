import asyncio
import logging

import discord
from discord.commands import Option, slash_command
from discord.ext import commands, tasks

from config import bot_config
from util.dataio import DataIO


class ThreadKeeper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    def is_keep_ignore_thread(self, thread: discord.Thread):
        data = DataIO.get_keep_ignore_targets_in_guild(thread.guild.id)

        if data is None:
            return False

        return thread.id in data["threads"] or \
               thread.parent.id in data["channels"] or \
               thread.guild.id in data["guilds"]

    def is_notify_ignore_thread(self, thread: discord.Thread):
        data = DataIO.get_notify_ignore_targets()

        if data is None:
            return False

        return thread.id in data["threads"] or \
               thread.parent.id in data["channels"] or \
               thread.guild.id in data["guilds"]

    async def autocomplete_set_to_ignore_category(self, ctx: discord.commands.context.ApplicationContext):
        values = ["keep", "notify"]
        return [value for value in values if value.startswith(ctx.value)]

    @slash_command(name="set_to_ignore", description="スレッドを除外対象に設定します")
    @commands.has_permissions(ban_members=True)
    async def set_to_ignore(self, ctx: discord.commands.context.ApplicationContext,
                            category: Option(str, 'provide ignore category', autocomplete=autocomplete_set_to_ignore_category),
                            is_whole_guild: Option(int),
                            is_whole_category: Option(int)):
        if is_whole_guild == 1:
            if category == "keep":
                DataIO.set_keep_ignore_target(guild_id=ctx.guild.id)
            elif category == "notify":
                DataIO.set_notify_ignore_target(guild_id=ctx.guild.id)

            self.logger.info(f"Guild {ctx.guild.name}({ctx.guild.id})を{category}から除外しました。")
            await ctx.respond(f"Guild {ctx.guild.name}({ctx.guild.id})を{category}から除外しました。")
            await bot_config.NOTIFY_TO_OWNER(self.bot, f"🧐 Add to {category} ignore: Guild {ctx.guild.name}({ctx.guild.id})")
        else:
            key = value = None
            if is_whole_category == 1:
                key = "category_id"
                value = ctx.channel.category.id
            elif type(ctx.channel) is discord.channel.TextChannel:
                key = "channel_id"
                value = ctx.channel.id
            elif type(ctx.channel) is discord.threads.Thread:
                key = "thread_id"
                value = ctx.channel.id

            if key is not None:
                if category == "keep":
                    DataIO.set_keep_ignore_target(**{key: value})
                elif category == "notify":
                    DataIO.set_notify_ignore_target(**{key: value})

                self.logger.info(f"{ctx.guild.name}({ctx.guild.id})/{ctx.channel.name}({ctx.channel.id})が属する{key.removesuffix('_id').capitalize()}を{category}から除外しました。")
                await ctx.respond(f"{ctx.guild.name}({ctx.guild.id})/{ctx.channel.name}({ctx.channel.id})が属する{key.removesuffix('_id').capitalize()}を{category}から除外しました。")
                await bot_config.NOTIFY_TO_OWNER(self.bot,
                                                 f"🧐 Add to {category} ignore: {key.removesuffix('_id').capitalize()} {ctx.guild.name}({ctx.guild.id})/{ctx.channel.name}({ctx.channel.id})")

            else:
                await ctx.respond("Error: 追加に失敗しました。")

    @commands.Cog.listener()
    async def on_ready(self):
        self.thread_keep_loop.stop()
        self.thread_keep_loop.start()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self.thread_keep_loop.is_running():
            self.logger.warning("Thread keep loop is not running.")
            self.thread_keep_loop.start()
            self.logger.info("Thread keep loop is started.")

    async def extend_archive_duration(self, thread: discord.Thread):

        if thread.archive is True:
            return

        try:
            await thread.edit(auto_archive_duration=60)
            await asyncio.sleep(1)
            await thread.edit(auto_archive_duration=10080)
        except Exception as e:
            self.logger.exception(e, exc_info=True)
            return

    @tasks.loop(hours=4)
    async def thread_keep_loop(self):
        self.logger.info("[Keep] loop start")
        # await bot_config.NOTIFY_TO_OWNER(self.bot, f"👀 Thread keeping......")
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if type(channel) is discord.channel.TextChannel:
                    for thread in channel.threads:
                        if self.is_keep_ignore_thread(thread):
                            self.logger.info(f"Ignoring: {thread.guild.name}/{thread.parent.name}/{thread.name}")
                        else:
                            self.logger.info(f"Keeping: {thread.guild.name}/{thread.parent.name}/{thread.name}")
                            await self.extend_archive_duration(thread)
        self.logger.info("[Keep] loop finished")

    @slash_command(name="set_notify_role", description="新規作成されたスレッドにinviteするロールを設定します")
    @commands.has_permissions(ban_members=True)
    async def set_notify_role(self, ctx: discord.commands.context.ApplicationContext,
                              roles: str):
        roles = roles.split(" ")
        role_ids = [int(role.removeprefix("<@&").removesuffix(">")) for role in roles]
        for role_id in role_ids:
            DataIO.set_notify_role(ctx.guild.id, role_id)
        await ctx.respond(f"Invite対象ロールを設定しました：{' '.join(roles)}")

    async def invite_roles(self, thread: discord.Thread):
        await thread.join()
        notify_roles = DataIO.get_notify_roles_in_guild(thread.guild.id)

        if notify_roles is not None:
            msg = await thread.send("スレッドが作成されました。")
            await msg.edit(content=f"{msg.content}\n{' '.join([f'<@&{role_id}>' for role_id in notify_roles])}")

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        if not self.is_notify_ignore_thread(thread):
            self.logger.info(f"[New] {thread.name}")
            await bot_config.NOTIFY_TO_OWNER(self.bot, f"🆕 Thread created: {thread.guild.name}/{thread.parent.name}/{thread.name}")
            await self.invite_roles(thread)
        else:
            self.logger.info(f"[New/Ignored] {thread.name}")
            await bot_config.NOTIFY_TO_OWNER(self.bot, f"🙈 Ignored thread created: {thread.guild.name}/{thread.parent.name}/{thread.name}")


def setup(bot):
    return bot.add_cog(ThreadKeeper(bot))
