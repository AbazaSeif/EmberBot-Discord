import discord
import json
import requests
import os
import datetime
import time
from discord.ext import commands
from base import rpc
from base.bot import is_owner

start_time = time.time()

class Admin:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.check(is_owner)
    async def pull(self, ctx):
        """
        Updates the bot.
        """
        await self.bot.say("Pulling...")
        try:
            returned = os.system("git pull")
            await self.bot.say(":+1:Returned code "+ str(returned))
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            output.error('{} has attempted to update the bot, but the following '
                         'exception occurred;\n\t->{}'.format(ctx.message.author, exc))

    @commands.command()
    async def uptime(self):
        """
        Get the time the bot has been active.
        """
        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        embed = discord.Embed(colour=0xFF0000)
        embed.add_field(name="Uptime", value=text)
        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("Current uptime: " + text)


    @commands.command()
    async def wallet(self):
        """Shows wallet info"""
        info = rpc.call.getinfo()
        wallet_balance = str(float(info["balance"]))
        block_height = info["blocks"]
        connection_count = rpc.call.getconnectioncount()
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="Balance", value="{:.8f} EMB".format(float(wallet_balance)))
        embed.add_field(name="Connections", value=connection_count)
        embed.add_field(name="Block Height", value=block_height)

        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")

    @commands.command()
    async def invite(self):
        """
        Get the bots invite link
        """
        await self.bot.say(":tada: https://discordapp.com/oauth2/authorize?permissions=0&client_id={}&scope=bot".format(self.bot.user.id))



def setup(bot):
    bot.add_cog(Admin(bot))
