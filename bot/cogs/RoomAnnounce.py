import logging
from datetime import datetime

import bs4
import discord
import httpx
import pytz
from discord.commands import slash_command
from discord.ext import commands

from util.dataio import DataIO


class RoomManagementPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.timezone = pytz.timezone("Asia/Tokyo")
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

        self.theater_open_time = None  # type: datetime | None
        self.theater_close_time = None  # type: datetime | None

    @staticmethod
    def _get_theater_schedule():
        resp = httpx.get("https://www.clib.kindai.ac.jp/")

        if resp.status_code != 200:
            return None

        soup = bs4.BeautifulSoup(resp.text, "html.parser")

        opening_time_panel = soup.select_one("article.opening_info.pc_only_disp .home_opening_time")

        if opening_time_panel is None:
            return None

        opening_times = opening_time_panel.find_all("dl")

        if opening_times is None:
            return None

        for opening_time in opening_times:
            title = opening_time.select_one("dt")
            time = opening_time.select_one("dd")

            if title is not None and time is not None and title.text == "ビブリオシアター":
                open_text, close_text = time.text.split("-")
                open_time = datetime.now().replace(hour=int(open_text.split(":")[0]), minute=int(open_text.split(":")[1]), second=0, microsecond=0)
                close_time = datetime.now().replace(hour=int(close_text.split(":")[0]), minute=int(close_text.split(":")[1]), second=0, microsecond=0)

                return open_time, close_time

        return None

    def update_theater_schedule(self):

        if self.theater_open_time is not None \
                and self.theater_open_time.day == datetime.now().day:
            return

        self.theater_open_time = self.theater_close_time = None

        schedule = self._get_theater_schedule()

        if schedule is None:
            self.logger.warning("Failed to update theater schedule.")
            return

        self.theater_open_time, self.theater_close_time = schedule
        self.logger.info(f"ACT Theater schedule updated: {self.theater_open_time} - {self.theater_close_time}")

    def get_opening_embed(self, mentions: list[str], current_embed: discord.Embed | None = None) -> discord.Embed:
        title = f"[{datetime.now().strftime('%m/%d')}]ACT126は開室しています"
        description = "入室者："
        colour = discord.Colour.green()

        if current_embed is None:
            timestamp = datetime.now(self.timezone)
        else:
            timestamp = current_embed.timestamp

        if self.theater_open_time is None:
            footer_text = "ビブリオシアターの開室時間が取得できませんでした。"
        else:
            footer_text = f"ビブリオシアター開館時間：{self.theater_open_time.strftime('%H:%M')} - {self.theater_close_time.strftime('%H:%M')}"

        return discord.Embed(
                title=title,
                description=description + " ".join(mentions),
                colour=colour,
                timestamp=timestamp
        ).set_footer(
                text=footer_text
        )

    def get_closed_embed(self, current_embed: discord.Embed) -> discord.Embed:
        return discord.Embed(
                title=f"[{datetime.now().strftime('%m/%d')}]ACT126は閉室しました",
                description=f"開室時間：{current_embed.timestamp.astimezone(self.timezone).strftime('%H:%M:%S')}\n閉室時間：{datetime.now(self.timezone).strftime('%H:%M:%S')}",
                colour=discord.Colour.red(),
                timestamp=datetime.now(self.timezone)
        )

    @discord.ui.button(label="入室", row=0, style=discord.ButtonStyle.primary, custom_id="room_management_panel_join")
    async def join_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.update_theater_schedule()
        for channel_id in DataIO.get_room_announce_target():
            channel = interaction.client.get_channel(channel_id)
            if channel is None:
                continue

            edit_target_message = None

            for enter_message in await channel.history(oldest_first=False, after=datetime.now(self.timezone).replace(hour=0, minute=0, second=0, microsecond=0)).flatten():
                if len(enter_message.embeds) == 0:
                    continue
                if enter_message.embeds[0].colour == discord.Colour.green():
                    edit_target_message = enter_message
                    break
                if enter_message.embeds[0].colour == discord.Colour.red():
                    break

            # 新規開室
            if edit_target_message is None:
                await channel.send(
                        embed=self.get_opening_embed([interaction.user.mention])
                )
                await interaction.response.send_message("開室しました", ephemeral=True)
            else:
                mentions = edit_target_message.embeds[0].description.split("：")[1].split(" ")

                if interaction.user.mention in mentions:
                    await interaction.response.send_message("既に入室しています", ephemeral=True)
                    continue

                mentions.append(interaction.user.mention)

                await edit_target_message.edit(
                        embed=self.get_opening_embed(mentions, edit_target_message.embeds[0])
                )
                await interaction.response.send_message("入室しました", ephemeral=True)

    @discord.ui.button(label="自分だけ退室", row=1, style=discord.ButtonStyle.secondary, custom_id="room_management_panel_leave")
    async def leave_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.update_theater_schedule()
        for channel_id in DataIO.get_room_announce_target():
            channel = interaction.client.get_channel(channel_id)
            if channel is None:
                continue

            edit_target_message = None

            for enter_message in await channel.history(oldest_first=False, after=datetime.now(self.timezone).replace(hour=0, minute=0, second=0, microsecond=0)).flatten():
                if len(enter_message.embeds) == 0:
                    continue
                if enter_message.embeds[0].colour == discord.Colour.green():
                    edit_target_message = enter_message
                    break
                if enter_message.embeds[0].colour == discord.Colour.red():
                    break

            # 未開室
            if edit_target_message is None:
                await interaction.response.send_message("開室していません", ephemeral=True)
            else:
                mentions = edit_target_message.embeds[0].description.replace("**", "").split("：")[1].split(" ")

                if interaction.user.mention not in mentions:
                    await interaction.response.send_message("入室していません", ephemeral=True)
                    continue

                mentions.remove(interaction.user.mention)

                if len(mentions) == 0:
                    await edit_target_message.edit(
                            embed=self.get_closed_embed(edit_target_message.embeds[0])
                    )
                    await interaction.response.send_message("全員が退室したため、閉室しました。", ephemeral=True)
                    continue

                await edit_target_message.edit(
                        embed=self.get_opening_embed(mentions, edit_target_message.embeds[0])
                )
                await interaction.response.send_message("退室しました", ephemeral=True)

    @discord.ui.button(label="全員退室", row=2, style=discord.ButtonStyle.danger, custom_id="room_management_panel_close")
    async def close_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.update_theater_schedule()
        for channel_id in DataIO.get_room_announce_target():
            channel = interaction.client.get_channel(channel_id)
            if channel is None:
                continue

            edit_target_message = None

            for enter_message in await channel.history(oldest_first=False, after=datetime.now(self.timezone).replace(hour=0, minute=0, second=0, microsecond=0)).flatten():
                if len(enter_message.embeds) == 0:
                    continue
                if enter_message.embeds[0].colour == discord.Colour.green():
                    edit_target_message = enter_message
                    break
                if enter_message.embeds[0].colour == discord.Colour.red():
                    break

            # 未開室
            if edit_target_message is None:
                await interaction.response.send_message("開室していません", ephemeral=True)
            else:
                await edit_target_message.edit(
                        embed=self.get_closed_embed(edit_target_message.embeds[0])
                )
                await channel.send("ACT126が閉室しました。", delete_after=1.0)
                await interaction.response.send_message("全員を退出させ、閉室しました。", ephemeral=True)


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
        DataIO.set_room_announce_target(channel_id=ctx.channel.id)
        await ctx.respond(f"このChにACT開閉室時の通知を行います。")

    @slash_command(name="remove_room_announce", description="ACT開閉室時の通知Chから削除します。")
    @commands.has_permissions(ban_members=True)
    async def remove_room_announce(self, ctx: discord.commands.context.ApplicationContext):
        DataIO.remove_room_announce_target(channel_id=ctx.channel.id)
        await ctx.respond(f"このChをACT開閉室時の通知対象から削除しました。")


def setup(bot):
    return bot.add_cog(RoomAnnounce(bot))
