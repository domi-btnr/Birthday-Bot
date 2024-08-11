import asyncio
import logging
import os
import time
from datetime import datetime, timedelta

import discord
import pymongo
from discord.ext import commands, tasks
from dotenv import load_dotenv

from utils.logger import logger_setup

intents = discord.Intents.default()
intents.members = True

load_dotenv()
TOKEN = os.getenv("TOKEN")
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = int(os.getenv("MONGO_PORT") or 27017)
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_DB = os.getenv("MONGO_DB") or "BirthdayBot"

logger_setup()
logger = logging.getLogger(os.path.basename(__file__))

bot = commands.Bot(intents=intents)
bot.startTime = time.time()
try:
    bot.DB = pymongo.MongoClient(
        host=MONGO_HOST,
        port=MONGO_PORT,
        username=MONGO_USER,
        password=MONGO_PASS,
    )[MONGO_DB]
    logger.info("Connected to MongoDB")
except pymongo.errors.ConnectionFailure:
    logger.error("Failed to connect to MongoDB")
    bot.DB = None

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")


@tasks.loop(minutes=30)
async def check_birthdays():
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    birthdays = bot.DB["users"].find(
        {
            "$expr": {
                "$and": [
                    {
                        "$eq": [
                            {
                                "$dateToString": {
                                    "format": "%m-%d",
                                    "date": "$birthday",
                                }
                            },
                            today.strftime("%m-%d"),
                        ]
                    },
                    {
                        "$eq": [
                            {
                                "$dateToString": {
                                    "format": "%H:%M",
                                    "date": "$birthday",
                                }
                            },
                            now.strftime("%H:%M"),
                        ]
                    },
                ]
            }
        }
    )

    for user in birthdays:
        age = now.year - user["birthday"].year
        guilds = [guild for guild in bot.guilds if guild.get_member(user["_id"])]
        for guild in guilds:
            channel = discord.utils.get(guild.text_channels, name="birthdays")
            if channel is None:
                continue

            await channel.send(
                f"Happy Birthday <@{user['_id']}>! 🎉🎂\nYou're now {age} Years old!"
            )


@bot.event
async def on_ready():
    logger.info(f"Bot started as {bot.user}")
    logger.info(f"Startup took {time.time() - bot.startTime:.2f} seconds")

    now = datetime.now()
    next_run = now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=30)
    if now.minute >= 30:
        next_run += timedelta(minutes=30)
    logger.info(f"Starting check_birthdays loop at {next_run}")
    await asyncio.sleep((next_run - now).total_seconds())
    check_birthdays.start()


bot.run(TOKEN)
