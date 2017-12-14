import discord
import json
import requests
from discord.ext import commands
import math

from base import rpc
from base import models

class Withdraw:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def withdraw(self, ctx, address:str, amount:float):
        """Withdraw coins from your account to any Ember address"""
        snowflake = ctx.message.author.id
        name = ctx.message.author.name
        discriminator = ctx.message.author.discriminator
        amount = abs(amount)

        if math.log10(amount) > 8:
            await self.bot.say(":warning:**Invalid amount!**:warning:")
            return

        u = models.DiscordUser.get_or_create(name, discriminator, snowflake)

        conf = rpc.call.validateaddress(address)
        if not conf["isvalid"]:
            await self.bot.say("{} **:warning:Invalid address!:warning:**".format(ctx.message.author.mention))
            return

        txid = rpc.call.sendfrom(snowflake, address, amount)

        await self.bot.say("%s withdrew %s EMB\nView the transaction: http://explorer.embercoin.io/tx/%s" % (ctx.message.author.mention, str(amount), txid))

def setup(bot):
    bot.add_cog(Withdraw(bot))
