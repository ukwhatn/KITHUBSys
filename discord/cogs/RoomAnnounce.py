import logging
import re
from datetime import datetime

import discord
from discord.commands import slash_command
from discord.ext import commands

from db.package.crud import discord_act126_open_status as status_crud
from db.package.crud import discord_room_announce_targets as announce_target_crud
from db.package.session import get_db


class RoomOpenUtility:
    @staticmethod
    async def get_embed(client: discord.Client) -> discord.Embed:
        with get_db() as db:
            in_room_managers = status_crud.get_managers(db)

        if len(in_room_managers) == 0:
            return discord.Embed(
                title=f"[{datetime.now().strftime('%m/%d')}]ACT126は閉室しました",
                colour=discord.Colour.red(),
                timestamp=datetime.now()
            )

        max_estimated_close_at = max([manager.estimated_close_at for manager in in_room_managers])
        mentions = []
        for manager in in_room_managers:
            user = client.get_user(manager.user_id)
            if user is None:
                user = await client.fetch_user(manager.user_id)
            mentions.append(user.mention)

        return discord.Embed(
            title=f"[{datetime.now().strftime('%m/%d')}]ACT126は開室しています",
            description=f"入室者： {' '.join(mentions)} \n\n閉室予定時間： {max_estimated_close_at.strftime('%H:%M')}",
            colour=discord.Colour.green(),
            timestamp=datetime.now()
        )

    @staticmethod
    async def send_or_update_messages_on_join(client: discord.Client, guild_id: int):
        embed = await RoomOpenUtility.get_embed(client)

        with get_db() as db:
            target_channel_ids = [t.channel_id for t in announce_target_crud.get_targets_by_guild_id(db, guild_id)]
            existing_messages = status_crud.get_messages(db)
            existing_message_channel_ids = [m.channel_id for m in existing_messages]

        for channel_id in target_channel_ids:
            channel = client.get_channel(channel_id)
            if channel is None:
                channel = await client.fetch_channel(channel_id)
                if channel is None:
                    continue

            if channel_id in existing_message_channel_ids:
                message_data = existing_messages[existing_message_channel_ids.index(channel_id)]
                message = await channel.fetch_message(message_data.message_id)
                await message.edit(embed=embed)
            else:
                message = await channel.send(embed=embed)
                with get_db() as db:
                    status_crud.add_message(db, guild_id=guild_id, channel_id=channel_id, message_id=message.id)

    @staticmethod
    async def update_messages_on_leave(client: discord.Client, guild_id: int, message_ids: list[tuple[int, int, int]]):
        embed = await RoomOpenUtility.get_embed(client)

        if embed.color == discord.Colour.red():
            for _, channel_id, message_id in message_ids:
                guild = client.get_guild(guild_id)
                if guild is None:
                    guild = await client.fetch_guild(guild_id)
                    if guild is None:
                        continue

                channel = guild.get_channel(channel_id)
                if channel is None:
                    channel = await guild.fetch_channel(channel_id)
                    if channel is None:
                        continue

                message = await channel.fetch_message(message_id)

                await message.edit(embed=embed)
                await channel.send("ACT126が閉室しました。", delete_after=1.0)
        else:
            await RoomOpenUtility.send_or_update_messages_on_join(client, guild_id)


class RoomOpenModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="閉室予定時間", placeholder="HH:MM"))

    async def callback(self, interaction: discord.Interaction):
        estimated_close_time = self.children[0].value

        # estimated_close_timeがHH:MM形式でない場合
        if not re.match(r"\d{1,2}:\d{1,2}", estimated_close_time):
            await interaction.response.send_message(
                "閉室予定時間がHH:MM形式でないため、開室できませんでした。",
                ephemeral=True
            )
            return

        with get_db() as db:
            status_crud.join_room(
                db,
                manager_user_id=interaction.user.id,
                estimated_close_at=datetime.strptime(estimated_close_time, "%H:%M")
            )

        await RoomOpenUtility.send_or_update_messages_on_join(interaction.client, interaction.guild.id)

        await interaction.response.send_message(
            "開室しました。",
            ephemeral=True
        )


class RoomManagementPanel(discord.ui.View):
    def __init__(self):
        # disable timeout for persistent view
        super().__init__(timeout=None)

        # set logger
        self.logger = logging.getLogger(type(self).__name__)

    @staticmethod
    def is_admin_interaction(interaction: discord.Interaction) -> bool:
        return interaction.permissions.administrator

    @discord.ui.button(label="入室", row=0, style=discord.ButtonStyle.primary, custom_id="room_management_panel_join")
    async def join_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(RoomOpenModal(title="閉室予定時間を入力"))

    @discord.ui.button(label="自分だけ退室", row=1, style=discord.ButtonStyle.secondary,
                       custom_id="room_management_panel_leave")
    async def leave_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        with get_db() as db:
            leave_result = status_crud.leave_room(db, manager_user_id=interaction.user.id)

            if leave_result is None:
                leave_result = []

        await RoomOpenUtility.update_messages_on_leave(interaction.client, interaction.guild.id, leave_result)

        await interaction.response.send_message("退室しました。", ephemeral=True)

    @discord.ui.button(label="全員退室", row=2, style=discord.ButtonStyle.danger,
                       custom_id="room_management_panel_close")
    async def close_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        with get_db() as db:
            leave_result = status_crud.cleanup(db)

            if leave_result is None:
                leave_result = []

        await RoomOpenUtility.update_messages_on_leave(interaction.client, interaction.guild.id, leave_result)

        await interaction.response.send_message("全員を退室させ、閉室しました", ephemeral=True)


class RoomAnnounce(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(RoomManagementPanel())

    @slash_command(name="room_manager", description="ACT開閉室用の操作パネルを送信します")
    async def room_manager(self, ctx: discord.commands.context.ApplicationContext):
        await ctx.respond(view=RoomManagementPanel())

    @slash_command(name="setup_room_announce", description="ACT開閉室時の通知Chに設定します")
    @commands.has_permissions(ban_members=True)
    async def setup_room_announce(self, ctx: discord.commands.context.ApplicationContext):
        with get_db() as db:
            announce_target_crud.create(db, guild_id=ctx.guild.id, channel_id=ctx.channel.id)
        await ctx.respond(f"このChにACT開閉室時の通知を行います。", ephemeral=True)

    @slash_command(name="remove_room_announce", description="ACT開閉室時の通知Chから削除します。")
    @commands.has_permissions(ban_members=True)
    async def remove_room_announce(self, ctx: discord.commands.context.ApplicationContext):
        with get_db() as db:
            announce_target_crud.delete(db, guild_id=ctx.guild.id, channel_id=ctx.channel.id)
        await ctx.respond(f"このChをACT開閉室時の通知対象から削除しました。", ephemeral=True)


def setup(bot):
    return bot.add_cog(RoomAnnounce(bot))
