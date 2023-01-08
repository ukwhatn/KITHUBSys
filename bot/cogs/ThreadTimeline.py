import asyncio
import logging

import discord
from config import bot_config
from discord.commands import Option, slash_command
from discord.ext import commands, tasks

from util.dataio import DataIO


class ThreadTimeline(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    @staticmethod
    def is_timeline_target(thread: discord.Thread):
        data = DataIO.get_timeline_chs_in_guild(thread.guild.id)

        if data is None:
            return False, None

        if thread.parent.id not in data:
            return False, None

        return True, data[thread.parent.id]

    @staticmethod
    def compose_embed(message: discord.Message) -> discord.Embed:
        if len(message.content) == 0:
            content = "no content"
        elif len(message.content) > 300:
            content = message.content[:300] + "..."
        else:
            content = message.content

        embed = discord.Embed(
                title=message.channel.name,
                url=message.jump_url,
                description=content,
                timestamp=message.created_at
        )
        if message.author.avatar is None:
            avatar_url = 'https://cdn.discordapp.com/embed/avatars/0.png'
        else:
            avatar_url = message.author.avatar.replace(format="png").url
        embed.set_author(
                name=message.author.display_name,
                icon_url=avatar_url
        )
        if message.attachments and message.attachments[0].proxy_url:
            embed.set_image(
                    url=message.attachments[0].proxy_url
            )
        return embed

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.channel.type not in [discord.ChannelType.public_thread, discord.ChannelType.private_thread]:
            return
        if len(message.content) == 0 and len(message.attachments) == 0:
            return

        is_target, target_chs = self.is_timeline_target(message.channel)

        if is_target:
            # if message.content[:7] == "!ignore":
            #     return

            for ch in target_chs:
                channel = self.bot.get_channel(ch)
                if channel is None:
                    continue
                await channel.send(embed=self.compose_embed(message))

    @commands.Cog.listener()
    async def on_message_edit(self, before_message: discord.Message, after_message: discord.Message):
        if before_message.author.bot:
            return
        if before_message.channel.type not in [discord.ChannelType.public_thread, discord.ChannelType.private_thread]:
            return
        if len(message.content) == 0 and len(message.attachments) == 0:
            return

        is_target, target_chs = self.is_timeline_target(before_message.channel)

        if is_target:
            # if before_message.content[:7] == "!ignore":
            #     return

            for ch in target_chs:
                channel = self.bot.get_channel(ch)
                if channel is None:
                    continue

                async for tl_message in channel.history(oldest_first=True, after=before_message.created_at):
                    if tl_message.embeds is not None and tl_message.embeds[0].url == before_message.jump_url:
                        await tl_message.edit(embed=self.compose_embed(after_message))
                        continue

    @slash_command(name="setup_timeline", description="TLの取得対象に設定")
    @commands.has_permissions(ban_members=True)
    async def setup_timeline(self, ctx: discord.commands.context.ApplicationContext, timeline_ch: Option(discord.TextChannel, "タイムラインを表示するチャンネル", required=True)):
        DataIO.set_timeline_ch(ctx.guild.id, ctx.channel.id, timeline_ch.id)
        await ctx.respond(f"このChのスレッドの内容を<#{timeline_ch.id}>に表示します。")

    @slash_command(name="remove_timeline", description="TLの取得対象から削除")
    @commands.has_permissions(ban_members=True)
    async def remove_timeline(self, ctx: discord.commands.context.ApplicationContext, timeline_ch: Option(discord.TextChannel, "タイムラインを表示するチャンネル", required=True)):
        DataIO.remove_timeline_ch(ctx.guild.id, ctx.channel.id, timeline_ch.id)
        await ctx.respond(f"このChのスレッドの内容は<#{timeline_ch.id}>に表示されません。")


def setup(bot):
    return bot.add_cog(ThreadTimeline(bot))
