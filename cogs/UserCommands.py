import logging
from collections import defaultdict
from datetime import datetime
from typing import List

import pytz
from discord import ApplicationContext, AutocompleteContext, Embed
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands

from cogs.utils.constants import Colors


class UserCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.__name__ = __name__
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Module loaded")

    def cog_unload(self) -> None:
        self.logger.info(f"Module unloaded")

    def get_common_timezones(ctx: AutocompleteContext) -> List[str]:
        timezones = pytz.common_timezones
        return [
            tz for tz in timezones if ctx.value.lower().replace(" ", "_") in tz.lower()
        ]

    birthday = SlashCommandGroup(name="birthday")

    @birthday.command(name="set", description="Set your birthday")
    async def set_birthday(
        self,
        ctx: ApplicationContext,
        date=Option(
            str, "The date of your birthday (Format: dd.MM.YYYY)", required=True
        ),
        timezone=Option(
            str,
            "Your timezone (Type to search)",
            autocomplete=get_common_timezones,
            required=True,
        ),
    ):
        if timezone not in pytz.common_timezones:
            embed = Embed(description="Timezone not found", color=Colors.ERROR)
            return await ctx.respond(embed=embed, ephemeral=True)
        timezone = pytz.timezone(timezone)
        try:
            date = datetime.strptime(date, "%d.%m.%Y")
            date = timezone.localize(date)
        except:
            return await ctx.respond(
                "Invalid date format. Please use dd.MM.YYYY", ephemeral=True
            )
        if date > datetime.now(pytz.UTC):
            embed = Embed(
                description="You can't set a birthday in the future", color=Colors.ERROR
            )
            return await ctx.respond(embed=embed, ephemeral=True)
        self.bot.DB["users"].update_one(
            {"_id": ctx.author.id},
            {"$set": {"birthday": date, "timezone": timezone.zone}},
            upsert=True,
        )
        embed = Embed(color=Colors.SUCCESS)
        embed.title = "Birthday set"
        embed.add_field(name="Date", value=f"<t:{int(datetime.timestamp(date))}:d>")
        embed.add_field(name="Timezone", value=timezone)
        await ctx.respond(embed=embed, ephemeral=True)

    @birthday.command(name="delete", description="Delete your birthday")
    async def delete_birthday(self, ctx: ApplicationContext):
        if not self.bot.DB["users"].find_one({"_id": ctx.author.id}):
            embed = Embed(
                description="You haven't set a birthday yet", color=Colors.WARNING
            )
            return await ctx.respond(embed=embed, ephemeral=True)
        self.bot.DB["users"].delete_one({"_id": ctx.author.id})
        embed = Embed(description="Birthday deleted", color=Colors.ERROR)
        await ctx.respond(embed=embed, ephemeral=True)

    @birthday.command(name="show", description="Show your birthday")
    async def show_birthday(self, ctx: ApplicationContext):
        user = self.bot.DB["users"].find_one({"_id": ctx.author.id})
        if not user:
            embed = Embed(
                description="You haven't set a birthday yet", color=Colors.WARNING
            )
            return await ctx.respond(embed=embed, ephemeral=True)
        embed = Embed(color=Colors.INFO)
        embed.title = "Your birthday"
        embed.add_field(
            name="Date", value=f"<t:{int(datetime.timestamp(user['birthday']))}:d>"
        )
        embed.add_field(name="Timezone", value=user["timezone"])
        await ctx.respond(embed=embed, ephemeral=True)

    @birthday.command(name="upcoming", description="Show upcoming birthdays")
    async def upcoming_birthdays(self, ctx: ApplicationContext):
        now = datetime.now(pytz.UTC)
        current_month = now.month
        current_year = now.year
        users_by_time = defaultdict(list)

        users = list(
            self.bot.DB["users"].find(
                {"_id": {"$in": [member.id for member in ctx.guild.members]}}
            )
        )

        if not users:
            embed = Embed(description="No upcoming birthdays", color=Colors.WARNING)
            return await ctx.respond(embed=embed)

        for user in users:
            birthday_utc = user["birthday"].replace(tzinfo=pytz.UTC)
            user_timezone = pytz.timezone(user["timezone"])
            birthday_local = birthday_utc.astimezone(user_timezone)

            next_birthday = birthday_local.replace(year=current_year)
            if next_birthday < now:
                next_birthday = birthday_local.replace(year=current_year + 1)

            time_until_birthday = next_birthday - now
            if time_until_birthday.days <= 30:
                time_key = f"In {time_until_birthday.days} {'Day' if time_until_birthday.days == 1 else 'Days'}"
            else:
                months_until_birthday = (
                    (next_birthday.year - current_year) * 12
                    + next_birthday.month
                    - current_month
                )
                time_key = f"In {months_until_birthday} {'Month' if months_until_birthday == 1 else 'Months'}"
            users_by_time[time_key].append((user, birthday_local))

        sorted_birthdays = sorted(users_by_time.keys(), key=lambda x: int(x.split()[1]))

        embed = Embed(title="Upcoming Birthdays", color=Colors.INFO)
        for time in sorted_birthdays:
            users = users_by_time[time]
            for user in users:
                value = f"- <@{user[0]['_id']}> <t:{int(user[1].timestamp())}:d> ({user[0]['timezone']})"
                embed.add_field(name=time, value=value, inline=False)
        await ctx.respond(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(UserCommands(bot))
