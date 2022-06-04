import logging
import time
from datetime import datetime
import mysql.connector

import discord

TOKEN = OWNER_ID = TWITTER_KEY_OBJECT = None


class TwitterKeys(object):
    def __init__(self,
                 key: str,
                 secretKey: str,
                 bearer: str,
                 token: str,
                 secretToken: str
                 ):
        self.key = key
        self.secretKey = secretKey
        self.bearer = bearer
        self.token = token
        self.secretToken = secretToken


# DBコンテナの起動を待つ
while True:
    try:
        with mysql.connector.Connect(**{
            "host":       "db",
            "port":       "3306",
            "user":       "application",
            "password":   "applicationpassword",
            "database":   "Master",
            "charset":    "utf8mb4",
            "collation":  "utf8mb4_general_ci",
            "autocommit": False
        }) as connect:
            with connect.cursor(dictionary=True) as cur:
                cur.execute("SELECT * FROM Master.config WHERE name LIKE 'bot_%' OR name LIKE 'twitter_%'")
                data = cur.fetchall()
                twKey = twSecretKey = twBearer = twToken = twSecretToken = None
                for d in data:
                    match d["name"]:
                        case "bot_token":
                            TOKEN = d["value"]
                        case "bot_owner_id":
                            OWNER_ID = int(d["value"])
                        case "twitter_key":
                            twKey = d["value"]
                        case "twitter_secret_key":
                            twSecretKey = d["value"]
                        case "twitter_bearer":
                            twBearer = d["value"]
                        case "twitter_token":
                            twToken = d["value"]
                        case "twitter_secret_token":
                            twSecretToken = d["value"]

        TWITTER_KEY_OBJECT = TwitterKeys(twKey, twSecretKey, twBearer, twToken, twSecretToken)
        break
    except mysql.connector.errors.InterfaceError as e:
        logging.warning("waiting database.....")
        time.sleep(3)
        continue


async def NOTIFY_TO_OWNER(bot, message: str):
    owner = await bot.fetch_user(OWNER_ID)
    dmCh = await owner.create_dm()
    await dmCh.send(
            content="Bot Status Notification",
            embed=discord.Embed().add_field(
                    name="Status",
                    value=message
            ).set_footer(
                    text=str(datetime.now())
            )
    )
