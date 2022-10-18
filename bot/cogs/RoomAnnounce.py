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
        # disable timeout for persistent view
        super().__init__(timeout=None)

        # set timezone
        self.timezone = pytz.timezone("Asia/Tokyo")

        # set logger
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

        # biblio theater schedule
        self.theater_open_time = None  # type: datetime | None
        self.theater_close_time = None  # type: datetime | None

    @staticmethod
    def _get_theater_schedule() -> tuple[datetime, datetime] | None:
        """
        Get the Biblio Theater's opening hours from the web page.
        Returns:
            (datetime, datetime) | None: (opening time, closing time) or None if failed to get schedule.

        """

        # get data from web page
        resp = httpx.get("https://www.clib.kindai.ac.jp/")

        # if failed to request
        if resp.status_code != 200:
            return None

        # parse html
        soup = bs4.BeautifulSoup(resp.text, "html.parser")

        # get opening hours element
        opening_time_panel = soup.select_one("article.opening_info.pc_only_disp .home_opening_time")

        # if failed to find element
        if opening_time_panel is None:
            return None

        # get pairs of facility name and opening hours
        opening_times = opening_time_panel.find_all("dl")

        # if failed to find element
        if opening_times is None:
            return None

        # search biblio theater's opening hours
        for opening_time in opening_times:
            title = opening_time.select_one("dt")
            time = opening_time.select_one("dd")

            if title is not None and time is not None and title.text == "ビブリオシアター":
                open_text, close_text = time.text.split("-")

                # convert to datetime
                open_time = datetime.now().replace(hour=int(open_text.split(":")[0]), minute=int(open_text.split(":")[1]), second=0, microsecond=0)
                close_time = datetime.now().replace(hour=int(close_text.split(":")[0]), minute=int(close_text.split(":")[1]), second=0, microsecond=0)

                return open_time, close_time

        return None

    def is_admin_interaction(self, interaction: discord.Interaction) -> bool:
        return interaction.permissions.administrator

    def is_admin_in_the_room(self, guild: discord.Guild, mentions) -> bool:
        # get roles
        roles_list=guild.roles
        # create admin_roles_list
        admin_roles_list=[]
        for role in roles_list:
            if role.permissions.administrator:
                admin_roles_list.append(role)
        # create admin_mentions_list
        admin_mentions_list=[]
        for role in admin_roles_list:
            members_list=role.members
            for member in members_list:
                admin_mentions_list.append(member.mention)
        # check if admins are in mentions
        is_admin_in_the_room=False
        for mention in mentions:
            is_admin_in_the_room = mention in admin_mentions_list or is_admin_in_the_room
        
        return is_admin_in_the_room
                

    def update_theater_schedule(self) -> None:
        """
        Update the opening hours of the Biblio Theater.
        Returns:
            None : instance variables are updated.

        """

        # If the opening hours have already been fetched and are for today, update will not be performed.
        if self.theater_open_time is not None \
                and self.theater_open_time.day == datetime.now().day:
            return

        # unset opening hours
        self.theater_open_time = self.theater_close_time = None

        # get opening hours
        schedule = self._get_theater_schedule()

        # if failed to get schedule
        if schedule is None:
            self.logger.warning("Failed to update theater schedule.")
            return

        # set opening hours
        self.theater_open_time, self.theater_close_time = schedule

        # logging
        self.logger.info(f"ACT Theater schedule updated: {self.theater_open_time} - {self.theater_close_time}")

    def get_opening_embed(self, mentions: list[str], current_embed: discord.Embed | None = None) -> discord.Embed:
        """
        Create Embed for room opened.
        Args:
            mentions: List of return values of discord.Members.mentions of board members in the room
            current_embed: Embed of the previous message. If None, the current time will be used as the opening time.

        Returns:
            discord.Embed: Embed for room opened.

        """
        # templates
        title = f"[{datetime.now().strftime('%m/%d')}]ACT126は開室しています"
        description = "入室者："
        colour = discord.Colour.green()

        # if current_embed is None, use current time as opening time
        if current_embed is None:
            timestamp = datetime.now(self.timezone)
        else:
            timestamp = current_embed.timestamp

        # if opening hours are not set, provide error message instead of opening hours in footer
        if self.theater_open_time is None:
            footer_text = "ビブリオシアターの開室時間が取得できませんでした。"
        else:
            footer_text = f"ビブリオシアター開館時間：{self.theater_open_time.strftime('%H:%M')} - {self.theater_close_time.strftime('%H:%M')}"

        # create embed and return
        return discord.Embed(
                title=title,
                description=description + " ".join(mentions),
                colour=colour,
                timestamp=timestamp
        ).set_footer(
                text=footer_text
        )

    def get_closed_embed(self, current_embed: discord.Embed) -> discord.Embed:
        """
        Create Embed for room closed.
        Args:
            current_embed: Embed of the previous message. This is used to get the opening time.

        Returns:
            discord.Embed: Embed for room closed.

        """
        # create embed and return
        return discord.Embed(
                title=f"[{datetime.now().strftime('%m/%d')}]ACT126は閉室しました",
                description=f"開室時間：{current_embed.timestamp.astimezone(self.timezone).strftime('%H:%M:%S')}\n閉室時間：{datetime.now(self.timezone).strftime('%H:%M:%S')}",
                colour=discord.Colour.red(),
                timestamp=datetime.now(self.timezone)
        )

    async def _get_last_message_to_update(self, channel: discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None) -> discord.Message | None:
        """
        Get the last message to update.
        Args:
            channel: Channel to search for messages.

        Returns:
            discord.Message | None: Last message to update. If not found, None is returned.

        """
        # search for the last message to update
        edit_target_message = None

        for enter_message in await channel.history(oldest_first=False, after=datetime.now(self.timezone).replace(hour=0, minute=0, second=0, microsecond=0)).flatten():
            # no embeds in message
            if len(enter_message.embeds) == 0:
                continue
            # found
            if enter_message.embeds[0].colour == discord.Colour.green():
                edit_target_message = enter_message
                break
            # not found
            if enter_message.embeds[0].colour == discord.Colour.red():
                break

        return edit_target_message

    @discord.ui.button(label="入室", row=0, style=discord.ButtonStyle.primary, custom_id="room_management_panel_join")
    async def join_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        Callback for join button.
        Args:
            button: Button that was clicked.
            interaction: discord.Interaction object.

        Returns:
            None

        """
        


        self.update_theater_schedule()

        for channel_id in DataIO.get_room_announce_target():
            # get channel to notify
            channel = interaction.client.get_channel(channel_id)

            # if channel is not found
            if channel is None:
                continue

            edit_target_message = await self._get_last_message_to_update(channel)
            

            # if the last message is not found(= the room is closed), create a new message
            if edit_target_message is None:

                # if the interaction user is not an admin, rejection the request
                if not self.is_admin_interaction(interaction):
                    await interaction.response.send_message("開室の権限がありません", ephemeral=True)
                    return
                
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

            edit_target_message = await self._get_last_message_to_update(channel)

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
                    # to notify the room is closed
                    await channel.send("ACT126が閉室しました。", delete_after=1.0)
                    await interaction.response.send_message("全員が退室したため、閉室しました。", ephemeral=True)
                    continue

                # If the admin wasn't in the room.
                if not self.is_admin_in_the_room(channel.guild, mentions):
                    await edit_target_message.edit(
                            embed=self.get_closed_embed(edit_target_message.embeds[0])
                    )
                    # to notify the room is closed
                    await channel.send("ACT126が閉室しました。", delete_after=1.0)
                    await interaction.response.send_message("役員が全員退出したため、閉室しました。", ephemeral=True)
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

            edit_target_message = await self._get_last_message_to_update(channel)

            # if the interaction user is not an admin, rejection the request
            if not self.is_admin_interaction(interaction):
                await interaction.response.send_message("閉室の権限がありません", ephemeral=True)
                return

            # 未開室
            if edit_target_message is None:
                await interaction.response.send_message("開室していません", ephemeral=True)

            else:
                await edit_target_message.edit(
                        embed=self.get_closed_embed(edit_target_message.embeds[0])
                )

                # to notify the room is closed
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
