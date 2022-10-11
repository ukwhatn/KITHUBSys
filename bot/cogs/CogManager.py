from discord.ext import commands
from discord.commands import Option, slash_command


class CogManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="reload", description="指定したCogをリロードします")
    @commands.is_owner()
    async def reload(self, ctx, modulename: str):
        await ctx.send(f":repeat: Reloading {modulename}")
        try:
            self.bot.reload_extension(f"cogs.{modulename}")
            await ctx.send(":thumbsup: Reloaded")
        except Exception:
            await ctx.send(":exclamation: Failed")

    @slash_command(name="load", description="指定したCogをロードします")
    @commands.is_owner()
    async def load(self, ctx, modulename: str):
        await ctx.send(f":arrow_up: Loading {modulename}")
        try:
            self.bot.load_extension(f"cogs.{modulename}")
            await ctx.send(":thumbsup: Loaded")
        except Exception:
            await ctx.send(":exclamation: Failed")

    @slash_command(name="unload", description="指定したCogをアンロードします")
    @commands.is_owner()
    async def unload(self, ctx, modulename: str):
        await ctx.send(f":arrow_down: Unloading {modulename}")
        try:
            self.bot.unload_extension(f"cogs.{modulename}")
            await ctx.send(":thumbsup: Unloaded")
        except Exception:
            await ctx.send(":exclamation: Failed")


def setup(bot):
    return bot.add_cog(CogManager(bot))
