import discord
import json
import requests
from discord.ext import commands
from base import rpc
from base import models
from base import config
from base import util

class Tip:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def tip(self, ctx, user:discord.Member, amount: float):
        """Tip a user coins"""
        snowflake = ctx.message.author.id
        name = ctx.message.author.name
        discriminator = ctx.message.author.discriminator

        tip_user = user.id
        if snowflake == tip_user:
            await self.bot.say("{} **:warning:You cannot tip yourself!:warning:**".format(ctx.message.author.mention))
            return

        if amount < 1.00000000:
            await self.bot.say("{} **:warning:You cannot tip < 1.00000000!:warning:**".format(ctx.message.author.mention))
            return

        if amount > 850000000.00000000:
            await self.bot.say("{} **:warning:You cannot tip > 850000000.00000000!:warning:**".format(ctx.message.author.mention))
            return

        u = models.DiscordUser.get_or_create(name, discriminator, snowflake)
        balance = rpc.call.getbalance(snowflake)
        u.update_balance(balance)

        amount = util.coin_float_to_bignum(amount)
        if u.balance < amount:
            await self.bot.say("{} **:warning:You cannot tip more money than you have!:warning:**".format(ctx.message.author.mention))
            return

        rcvr = models.DiscordUser.get_or_create(user.name, user.discriminator, user.id)
        if rcvr.address is None:
            rcvr.address = rpc.call.getaccountaddress(user.id)

        payments = {}
        total_amount = amount
        amount = amount - config.NET_TAX
        personal_tax = util.coin_bignum_to_float((amount // 100) * config.PERSONAL_TAX)
        amount = util.coin_bignum_to_float((amount // 100) * (100-config.PERSONAL_TAX))
        print("amt: {:.8f} tax: {:.8f}".format(amount, personal_tax))
        payments[config.TAX_COLLECTOR] = personal_tax
        payments[rcvr.address] = amount

        rpc.call.sendmany(snowflake, payments)
        await self.bot.say("{} **Tipped {} {:.8f} EMB! :money_with_wings: Small tax levied: {:.8f}**".format(ctx.message.author.mention, user.mention, amount, personal_tax))

def setup(bot):
    bot.add_cog(Tip(bot))
