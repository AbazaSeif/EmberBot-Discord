import discord
from discord.ext import commands
from base import models
from base import rpc

class Balance:
    def __init__(self, bot):
        self.bot = bot

    async def do_embed(self, name, db_bal):
        # Simple embed function for displaying username and balance
        embed = discord.Embed(colour=0xff0000)
        embed.add_field(name="User", value=name.mention)
        embed.add_field(name="Balance", value="{:.8f} EMB".format(round(float(db_bal), 8)))

        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")


    @commands.command(pass_context=True)
    async def balance(self, ctx):
        """Display your balance"""
        # Set important variables
        snowflake = ctx.message.author.id
        name = ctx.message.author.name
        discriminator = ctx.message.author.discriminator
        #print("Snowflake: %s" % (snowflake,))

        u = models.DiscordUser.get_or_create(name, discriminator, snowflake)
        balance = rpc.call.getbalance(snowflake)
        u.update_balance(balance)
        await self.do_embed(ctx.message.author, balance)

def setup(bot):
    bot.add_cog(Balance(bot))
