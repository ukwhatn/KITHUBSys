import logging
import random
import string

import discord
from discord.commands import Option, slash_command
from discord.ext import commands

from util.dataio import DataIO

user_form_master = {}


class ModalSendPanel(discord.ui.View):
    def __init__(self, bot):
        # disable timeout for persistent view
        super().__init__(timeout=None)

        self.bot = bot

        # set logger
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    @discord.ui.button(label="質問する", style=discord.ButtonStyle.primary, custom_id="create_question")
    async def create_question_callback(self, button: discord.Button, interaction: discord.Interaction):
        user_form_master[interaction.user.id] = DataIO.get_form_buttons()[interaction.message.id]
        await interaction.response.send_modal(QuestionFormModal(bot=self.bot, title="匿名質問フォーム"))


class QuestionFormModal(discord.ui.Modal):
    def __init__(self, bot, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.bot = bot

        self.add_item(discord.ui.InputText(label="質問のタイトル"))
        self.add_item(discord.ui.InputText(label="質問の内容", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        form_id = user_form_master[interaction.user.id]
        send_to = self.bot.get_channel(DataIO.get_question_forms()[form_id]["send_to"])  # type: discord.ForumChannel
        thread = await send_to.create_thread(
                name=self.children[0].value,
                content=self.children[1].value
        )
        await interaction.response.send_message(f"=> {thread.mention}", ephemeral=True)


class QuestionForm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

    @staticmethod
    def randomname(n):
        randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
        return ''.join(randlst)

    async def autocomplete_forms(self, ctx: discord.commands.context.ApplicationContext):
        forms = DataIO.get_question_forms()
        names = [f'{k}/{d["name"]}' for k, d in forms.items()]
        res = [value for value in names if ctx.value in value]
        if len(res) == 0:
            return names
        return res

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ModalSendPanel(self.bot))

    @slash_command(name="create_form", description="フォームを作成")
    @commands.has_permissions(ban_members=True)
    async def create_form(self,
                          ctx: discord.commands.context.ApplicationContext,
                          name: Option(str, "provide form name", required=True),
                          send_to: Option(discord.ForumChannel, "provide channel", required=True)
                          ):
        form_id = self.randomname(10)
        DataIO.set_question_form(form_id, name, send_to.id)
        await ctx.respond(
                "\n".join([
                    f"Created: ",
                    f"> id: {form_id}",
                    f"> name: {name}",
                    f"> send_to: {send_to.mention}"
                ]),
                ephemeral=True
        )

    @slash_command(name="remove_form", description="フォームを削除")
    @commands.has_permissions(ban_members=True)
    async def remove_form(self,
                          ctx: discord.commands.context.ApplicationContext,
                          name: Option(str, "provide form name", required=True, autocomplete=autocomplete_forms)
                          ):
        form_id = name.split("/")[0]
        DataIO.remove_question_form(form_id)
        await ctx.respond("Deleted!", ephemeral=True)

    @slash_command(name="send_form", description="フォーム作成ボタンを送信")
    @commands.has_permissions(ban_members=True)
    async def send_form(self,
                        ctx: discord.commands.context.ApplicationContext,
                        name: Option(str, "provide form name", required=True, autocomplete=autocomplete_forms)
                        ):
        form_id = name.split("/")[0]
        panel = await ctx.channel.send(view=ModalSendPanel(self.bot))
        DataIO.set_form_button(panel.id, form_id)
        await ctx.respond("Created!", ephemeral=True)


def setup(bot):
    return bot.add_cog(QuestionForm(bot))
