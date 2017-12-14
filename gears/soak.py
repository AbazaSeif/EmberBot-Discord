import math
import discord
import os
import itertools
from discord.ext import commands
from base.bot import is_owner, is_soakable
from base import models
from base.models import Server, db_session
from base import rpc
from base import config
from base import util

class Soak:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.check(is_owner)
    async def setsoak(self, ctx, enable: bool):
        s = Server.query.filter(Server.server_id == str(ctx.message.server.id)).first()
        if s is None:
            await self.bot.say("No go, dude!")
        else:
            s.can_soak = enable
            db_session.commit()
        await self.bot.say("Ok!")

    @commands.command(pass_context=True)
    @commands.check(is_owner)
    async def checksoak(self, ctx):
        print(ctx.message.server.id)
        s = Server.query.filter(Server.server_id == str(ctx.message.server.id)).first()
        if s is None:
            await self.bot.say("Uh oh, dude!")
        await self.bot.say(s.can_soak)

    @commands.command(pass_context=True)
    @commands.check(is_soakable)
    async def soak(self, ctx, amount: float):
        """Tip all online users"""
        snowflake = ctx.message.author.id
        name = ctx.message.author.name
        discriminator = ctx.message.author.discriminator
        #print("Snowflake: %s" % (snowflake,))

        balance = rpc.call.getbalance(snowflake)
        u = models.DiscordUser.get_or_create(name, discriminator, snowflake)
        u.update_balance(balance)

        if not math.isfinite(amount):
            await self.bot.say("{} **:warning:You tried to use special float values to break my parser! Bad form Jack!:warning:**".format(ctx.message.author.mention))
            return

        amount_bn = util.coin_float_to_bignum(amount)
        print("Balance %s\nAmount %s" % (balance, amount_bn))

        if balance < amount_bn:
            await self.bot.say("{} **:warning:You cannot soak more money than you have!:warning:**".format(ctx.message.author.mention))
            return

        if amount_bn < 10000000000:
            await self.bot.say("{} **:warning:You cannot soak < 100.00000000!:warning:**".format(ctx.message.author.mention))
            return

        if amount_bn > 85000000000000000:
            await self.bot.say("{} **:warning:You cannot soak > 850000000.00000000!:warning:**".format(ctx.message.author.mention))
            return

        online_users = [x for x in ctx.message.server.members if x.status in (discord.Status.online,) and
                             x is not ctx.message.author and
                             x.bot is not True]

        if len(online_users) < 1:
            await self.bot.say("{} **:warning:There is no one to soak!:warning:**".format(ctx.message.author.mention))
            return

        payments = {}
        amount_bn -= config.NET_TAX
        personal_tax = config.PERSONAL_TAX * amount
        amount -= personal_tax
        amount_split = math.floor(float(amount) * 1e8 / len(online_users)) / 1e8

        for u in online_users:
            user = models.DiscordUser.get_or_create(u.name, u.discriminator, u.id)
            if user.address is None:
                user.address = rpc.call.getaccountaddress(u.id)
            payments[user.address] = amount_split
        payments[config.TAX_COLLECTOR] = personal_tax
        rpc.call.sendmany(snowflake, payments)

        await self.bot.say(":money_with_wings: {} **Soaked {:.8f} EMB on each of {} :money_with_wings:\nSmall tax levied: {:.8f}**".format(ctx.message.author.mention, amount_split, ', '.join([x.mention for x in online_users]), personal_tax))


def setup(bot):
    bot.add_cog(Soak(bot))
