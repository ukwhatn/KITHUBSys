from discord.ext import commands
import discord
import tweepy
import logging
from config import bot_config


class TweetStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.logger = logging.getLogger(type(self).__name__)
        self.logger.setLevel(logging.DEBUG)

        # Create Twitter API Session
        twKeys = bot_config.TWITTER_KEY_OBJECT
        twAuth = tweepy.OAuthHandler(twKeys.key, twKeys.secretKey)
        twAuth.set_access_token(twKeys.token, twKeys.secretToken)
        self.twAPI = tweepy.API(twAuth)

    @commands.Cog.listener(name="on_voice_state_update")
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if after.channel is not None:
            if len(after.channel.members) == 1:
                memberName = member.nick if member.nick is not None else member.name
                channelName = after.channel.name
                if channelName == "作業":
                    tweetContent = "\n".join([
                        "[KITHUB Notification]",
                        f"{memberName}がVCで作業を開始しました！"
                    ])
                elif channelName == "雑談":
                    tweetContent = "\n".join([
                        "[KITHUB Notification]",
                        f"{memberName}がVCで雑談を開始しました！"
                    ])
                else:
                    tweetContent = "\n".join([
                        "[KITHUB Notification]",
                        f"{memberName}が{channelName}に入室しました！"
                    ])

                self.twAPI.update_status(tweetContent)
                self.logger.info(f"Tweeted: {tweetContent}")


def setup(bot):
    return bot.add_cog(TweetStatus(bot))
