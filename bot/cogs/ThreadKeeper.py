import asyncio
import json
import logging

import discord
from config.message_config import MessageTemplates
from discord.commands import Option, slash_command
from discord.ext import commands, tasks


class ThreadKeeper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    def get_ignore_data(self) -> dict:
        with open("/opt/keep_ignore.json", "r") as f:
            return json.load(f)

    def set_ignore_data(self, data: dict):
        with open("/opt/keep_ignore.json", "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def is_ignore_thread(self, thread: discord.Thread, key: str):
        json_data = self.get_ignore_data()[key]
        if thread.id in json_data["threads"] or \
                thread.parent.id in json_data["channels"] or \
                thread.guild.id in json_data["guilds"]:
            return True
        return False

    async def autocomplete_set_to_ignore_category(self, ctx: discord.commands.context.ApplicationContext):
        values = ["keep", "notify"]
        return [value for value in values if value.startswith(ctx.value)]

    @slash_command(name="set_to_ignore", guild_ids=[958663674216718366, 490892087668244480])
    @commands.has_permissions(ban_members=True)
    async def set_to_ignore(self, ctx: discord.commands.context.ApplicationContext,
                            category: Option(str, 'provide ignore category', autocomplete=autocomplete_set_to_ignore_category),
                            is_whole_guild: Option(int)):
        ignore_data = self.get_ignore_data()  # type: dict[str, dict[str, list]]
        if is_whole_guild == 1:
            if ctx.guild.id not in ignore_data[category]["guilds"]:
                ignore_data[category]["guilds"].append(ctx.guild.id)
                self.logger.info(f"Guild {ctx.guild.name}({ctx.guild.id})を除外しました。")
        else:
            key = None
            if type(ctx.channel) is discord.channel.TextChannel:
                key = "channel"
            elif type(ctx.channel) is discord.threads.Thread:
                key = "thread"
            if key is not None:
                if ctx.channel.id not in ignore_data[category][key + "s"]:
                    ignore_data[category][key + "s"].append(ctx.channel.id)
                    self.logger.info(f"{key} {ctx.channel.name}({ctx.channel.id})を除外しました。")

        self.set_ignore_data(ignore_data)

        await ctx.respond("除外しました")

    @commands.Cog.listener()
    async def on_ready(self):
        self.thread_keep_loop.stop()
        self.thread_keep_loop.start()

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
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if type(channel) is discord.channel.TextChannel:
                    for thread in channel.threads:
                        if self.is_ignore_thread(thread, "keep"):
                            self.logger.info(f"Ignoring: {thread.guild.name}/{thread.parent.name}/{thread.name}")
                        else:
                            self.logger.info(f"Keeping: {thread.guild.name}/{thread.parent.name}/{thread.name}")
                            await self.extend_archive_duration(thread)
        self.logger.info("[Keep] loop finished")

    async def invite_roles(self, thread: discord.Thread):
        await thread.join()
        msg = await thread.send(MessageTemplates.on_thread_create_main())
        await msg.edit(content=f"{msg.content}{MessageTemplates.on_thread_create_roles()}")

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        if not self.is_ignore_thread(thread, "notify"):
            self.logger.info(f"[New] {thread.name}")
            await self.invite_roles(thread)
        else:
            self.logger.info(f"[New/Ignored] {thread.name}")


def setup(bot):
    return bot.add_cog(ThreadKeeper(bot))
