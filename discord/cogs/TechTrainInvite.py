import logging
import re

import discord
from discord.commands import slash_command
from discord.ext import commands

from db.package.crud import tech_train_invite_management_channels as invite_management_channels_crud
from db.package.crud import tech_train_invites as invites_crud
from db.package.session import get_db


class TechTrainInviteUtility:
    @staticmethod
    async def get_notification_channels(bot: discord.Client, guild_id: int):
        with get_db() as db:
            notification_channel_records = invite_management_channels_crud.get_channels_by_guild_id(db, guild_id)
        # 送信先Chを取得
        notification_channels = []
        for notification_channel_record in notification_channel_records:
            notification_channel = bot.get_channel(notification_channel_record.channel_id)

            if notification_channel is None:
                notification_channel = await bot.fetch_channel(notification_channel_record.channel_id)

            if notification_channel is not None:
                notification_channels.append(notification_channel)

        return notification_channels


class TechTrainInviteResponseView(discord.ui.View):
    def __init__(self):
        # disable timeout for persistent view
        super().__init__(timeout=None)

        # set logger
        self.logger = logging.getLogger(type(self).__name__)

    @discord.ui.button(label="アカウントの作成・Slackワークスペースへの参加が完了した",
                       style=discord.ButtonStyle.primary, custom_id="tt_invite_response_success")
    async def join_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        # idを取得
        invite_id = int(interaction.message.embeds[0].footer.text)

        if invite_id is None:
            self.logger.error(f"TechTrainInviteResponseView: invite_id({invite_id}) is None")
            await interaction.response.send_message(
                "エラーが発生しました。以下の内容を役員にお伝えください。\n"
                "エラーコード: `TT_INVITE_RESPONSE_SUCCESS_INVITE_ID_NOT_FOUND`"
            )

        # 完了をマーク
        with get_db() as db:
            invite = invites_crud.complete(db, invite_id)

        if invite is None:
            self.logger.error(f"TechTrainInviteResponseView: invite({invite_id}) is None")
            await interaction.response.send_message(
                "エラーが発生しました。以下の内容を役員にお伝えください。\n"
                "エラーコード: `TT_INVITE_RESPONSE_SUCCESS_INVITE_NOT_FOUND`"
            )

        # ボタンを無効化
        button.disabled = True
        await interaction.response.edit_message(view=self)

        # respond
        await interaction.response.send_message("完了報告を受領しました！")

        # 送信先Chを取得
        notification_channels = await TechTrainInviteUtility.get_notification_channels(
            interaction.client,
            invite.guild_id
        )

        # 送信をチャンネルに通知
        notification_embed = discord.Embed(
            title="TechTrainへの招待が完了しました",
            description=f"{interaction.user.mention}がTechTrainに参加しました。",
            color=discord.Color.green()
        )
        notification_embed.add_field(name="招待時アドレス", value=invite.email)

        for notification_channel in notification_channels:
            await notification_channel.send("**【TechTrain 招待通知】**", embed=notification_embed)


class TechTrainInvite(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.logger = logging.getLogger(type(self).__name__)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TechTrainInviteResponseView())

    @slash_command(name="tt_invite", description="TechTrainの招待リンクを送信します")
    @discord.commands.default_permissions(administrator=True)
    async def tt_invite(
            self, ctx: discord.commands.context.ApplicationContext,
            user: discord.Option(discord.User, "TechTrainに招待するユーザー", required=True),
            invite_url: discord.Option(str, "TechTrainの招待リンク", required=True),
            email: discord.Option(str, "TechTrainの招待リンクを送信するメールアドレス", required=True)
    ):
        # バリデーション
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            await ctx.respond("メールアドレスが正しくありません。", ephemeral=True)
            return

        if not re.match(r"https://techtrain.dev/invited-signup\?invitation_code=", invite_url):
            await ctx.respond("招待リンクが正しくありません。", ephemeral=True)
            return

        # respond
        await ctx.respond(f"{user.mention}にTechTrainの招待リンクを送信します。", ephemeral=True)

        # 保存
        with get_db() as db:
            invite = invites_crud.create(db, ctx.guild.id, user.id, email, invite_url, ctx.author.id)

        # 送信先Chを取得
        notification_channels = await TechTrainInviteUtility.get_notification_channels(self.bot, ctx.guild.id)

        # embed作成
        embed = discord.Embed(
            title="TechTrain招待リンク",
            description="以下のリンクからTechTrainに参加してください。",
            color=discord.Color.green()
        )
        embed.add_field(name="招待URL", value=invite_url, inline=False)
        embed.add_field(name="メールアドレス", value=email, inline=False)
        embed.set_footer(text=str(invite.id))

        # userのDMに送信
        try:
            await user.send("**【KITHUBからのお知らせ】**", embed=embed, view=TechTrainInviteResponseView())
        except discord.errors.Forbidden as e:
            await ctx.respond(f"{user.mention}のDMが無効化されているため、招待リンクを送信できませんでした。",
                              ephemeral=True)
            return

        # 送信をチャンネルに通知
        notification_embed = discord.Embed(
            title="TechTrainへの招待を送信しました",
            description=f"{user.mention}に招待リンクを送信しました。",
            color=discord.Color.green()
        )
        notification_embed.add_field(name="招待URL", value=invite_url, inline=False)
        notification_embed.add_field(name="メールアドレス", value=email, inline=False)
        notification_embed.add_field(name="送信者", value=ctx.author.mention, inline=False)

        for notification_channel in notification_channels:
            await notification_channel.send("**【TechTrain 招待通知】**", embed=notification_embed)

    @slash_command(name="tt_invite_list", description="TechTrainの招待リンク一覧を表示します")
    @discord.commands.default_permissions(administrator=True)
    async def tt_invite_list(
            self, ctx: discord.commands.context.ApplicationContext
    ):
        # 保存
        with get_db() as db:
            invites = invites_crud.get_invites_by_guild_id(db, ctx.guild.id)

        # embed作成
        embed = discord.Embed(
            title="TechTrain招待リンク一覧",
            description="TechTrainの招待リンク一覧です。",
            color=discord.Color.green()
        )
        for invite in invites:
            embed.add_field(name=f"ID: {invite.id}",
                            value=f"ユーザー: <@{invite.user_id}>\n"
                                  f"メールアドレス: {invite.email}\n"
                                  f"招待URL: {invite.invite_url}\n"
                                  f"送信者: <@{invite.sender_id}>\n"
                                  f"完了: {invite.is_completed}\n",
                            inline=False
                            )

        await ctx.respond(embed=embed)

    @slash_command(name="set_tt_notification_channel", description="TechTrainの招待通知先チャンネルを設定します")
    @discord.commands.default_permissions(administrator=True)
    async def set_tt_notification_channel(
            self, ctx: discord.commands.context.ApplicationContext,
            channel: discord.Option(discord.TextChannel, "TechTrainの招待通知先チャンネル", required=True)
    ):
        # 保存
        with get_db() as db:
            invite_management_channels_crud.create(db, ctx.guild.id, channel.id)

        await ctx.respond(f"TechTrainの招待通知先チャンネルを{channel.mention}に設定しました。", ephemeral=True)

    @slash_command(name="remove_tt_notification_channel", description="TechTrainの招待通知先チャンネルを削除します")
    @discord.commands.default_permissions(administrator=True)
    async def remove_tt_notification_channel(
            self, ctx: discord.commands.context.ApplicationContext,
            channel: discord.Option(discord.TextChannel, "TechTrainの招待通知先チャンネル", required=True)
    ):
        # 保存
        with get_db() as db:
            invite_management_channels_crud.delete(db, ctx.guild.id, channel.id)

        await ctx.respond(f"TechTrainの招待通知先チャンネルを{channel.mention}から削除しました。", ephemeral=True)


def setup(bot):
    return bot.add_cog(TechTrainInvite(bot))
