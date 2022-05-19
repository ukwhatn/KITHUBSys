import asyncio
import logging

import discord
from discord.ext import commands, tasks


class ThreadKeeper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    @commands.Cog.listener()
    async def on_ready(self):
        self.thread_keep_loop.stop()
        self.thread_keep_loop.start()

    async def extend_archive_duration(self, thread: discord.Thread):
        logging.info(f"[Keep] thread: {thread.guild.name}/{thread.parent.name}/{thread.name}")
        if thread.auto_archive_duration != 1440:
            await thread.edit(auto_archive_duration=1440)
            await asyncio.sleep(10)

        if thread.archive is True:
            return

        try:
            await thread.edit(auto_archive_duration=60)
            await asyncio.sleep(10)
            await thread.edit(auto_archive_duration=1440)
        except Exception as e:
            logging.exception(e, exc_info=True)

    @tasks.loop(hours=1)
    async def thread_keep_loop(self):
        logging.info("[Keep] loop start")
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if type(channel) is discord.channel.TextChannel:
                    for thread in channel.threads:
                        await self.extend_archive_duration(thread)
        logging.info("[Keep] loop finished")


def setup(bot):
    return bot.add_cog(ThreadKeeper(bot))
