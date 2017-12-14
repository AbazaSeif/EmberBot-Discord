import discord, json, requests
from discord.ext import commands

from base import rpc

class Deposit:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def deposit(self, ctx):
        """Shows wallet info"""
        user = ctx.message.author
        user_addy = rpc.call.getaccountaddress(user.id)
        await self.bot.say(user.mention + "'s Deposit Address: `" + str(user_addy) + "`")


def setup(bot):
    bot.add_cog(Deposit(bot))
