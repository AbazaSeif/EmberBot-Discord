import discord, os
from discord.ext import commands
from aiohttp import ClientSession
import urllib.request
import json
from decimal import Decimal

class Pricing:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.command()
    async def price(self, amount=1):
        """
        Checks the price of EMB
        """
        headers={"user-agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"}
        try:
            async with ClientSession() as session:
                async with session.get("https://www.cryptopia.co.nz/api/GetMarket/EMB_LTC", headers=headers) as response:
                    responseRaw = await response.read()
                    resp = responseRaw.decode()
                    priceData = json.loads(resp)['Data']
                    embed = discord.Embed(colour=0x00FF00)
                    embed.add_field(name="24-hour Volume", value="{} EMB".format(priceData['Volume']))
                    embed.add_field(name="24-hour Low", value="{:.8f} LTC".format(priceData['Low']))
                    embed.add_field(name="24-hour High", value="{:.8f} LTC".format(priceData['High']))
                    embed.add_field(name="Price", value="{} EMB = {:.8f} LTC".format(amount, amount * float(priceData['LastPrice'])))
                    await self.bot.say(embed=embed)
        except Exception as err:
            print("Exception: {0}".format(err))
            await self.bot.say(":warning: Error fetching prices!")


def setup(bot):
    bot.add_cog(Pricing(bot))
