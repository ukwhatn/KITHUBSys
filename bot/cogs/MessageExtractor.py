from __future__ import annotations

import logging
import re

import discord
from discord.ext import commands


class MessageExtractor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # type:discord.Client
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

        self.regex_discord_message_url = (
            'https://(ptb.|canary.)?discord(app)?.com/channels/'
            '(?P<guild>[0-9]{18,19})/(?P<channel>[0-9]{18,19})/(?P<message>[0-9]{18,19})'
        )

        self.extract_delete_cmd_emoji = "❌"

    async def get_message_from_id(self, guild_id: int, channel_id: int, message_id: int) -> discord.Message | None:
        guild = self.bot.get_guild(guild_id)  # type: discord.Guild | None
        if guild is None:
            return None
        channel = await guild.fetch_channel(channel_id)  # type: discord.abc.GuildChannel | discord.Thread | None
        if channel is None:
            return None
        message = await channel.fetch_message(message_id)  # type: discord.Message | None

        return message

    @staticmethod
    def compose_embed(message: discord.Message) -> discord.Embed:
        embed = discord.Embed(
                description=message.content,
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
        embed.set_footer(
                text=message.channel.name,
                icon_url=message.guild.icon.url,
        )
        if message.attachments and message.attachments[0].proxy_url:
            embed.set_image(
                    url=message.attachments[0].proxy_url
            )
        return embed

    def is_readable_for_everyone(self, message: discord.Message) -> bool:
        everyone_role = message.guild.default_role
        message_permission = message.channel.permissions_for(everyone_role)
        self.logger.debug(" ".join(["everyone_readable:", str(message_permission.read_messages)]))
        return message_permission.read_messages

    def has_same_readable_roles(self, channel_a: discord.abc.GuildChannel, channel_b: discord.abc.GuildChannel) -> bool:
        if channel_a.guild.id != channel_b.guild.id:
            return False

        for role in channel_a.guild.roles:
            channel_a_permission = channel_a.permissions_for(role)
            channel_b_permission = channel_b.permissions_for(role)
            self.logger.debug(" ".join(["readable:", role.name, str(channel_a_permission.read_messages), str(channel_b_permission.read_messages)]))
            if channel_a_permission.read_messages != channel_b_permission.read_messages:
                return False

        return True

    async def extract_message(self, message: discord.Message) -> list[discord.Message]:
        founded_messages = []
        for ids in re.finditer(self.regex_discord_message_url, message.content):
            guild_id = int(ids["guild"])
            channel_id = int(ids["channel"])
            message_id = int(ids["message"])
            fetched_message = await self.get_message_from_id(guild_id, channel_id, message_id)
            if fetched_message is None:
                continue
            if not self.is_readable_for_everyone(fetched_message):
                if not self.has_same_readable_roles(message.channel, fetched_message.channel):
                    continue
            founded_messages.append(fetched_message)
        return founded_messages

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        founded_messages = await self.extract_message(message)
        for founded_message in founded_messages:
            try:
                if founded_message.content:
                    _msg = await message.channel.send(embed=self.compose_embed(founded_message))
                    await _msg.add_reaction(self.extract_delete_cmd_emoji)
                for embed in founded_message.embeds:
                    _msg = await message.channel.send(embed=embed)
                    await _msg.add_reaction(self.extract_delete_cmd_emoji)
            except BaseException as e:
                raise

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.emoji.name == self.extract_delete_cmd_emoji:
            channel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            user = await self.bot.fetch_user(payload.user_id)
            if message.author.id == self.bot.user.id:
                if user.id == channel.owner_id or channel.permissions_for(await channel.guild.fetch_member(user.id)).administrator:
                    await message.delete()
                    self.logger.info(f"Extracted message deleted: {message.guild.name}/{message.channel.name} by {user.name}")


def setup(bot):
    return bot.add_cog(MessageExtractor(bot))
