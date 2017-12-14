import os
import sys
import asyncio
import logging
import discord
from discord.ext import commands
from base import config
from base import models
from base import rpc


logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix=config.DISCORD_PREFIX, description=config.DISCORD_DESC)
startup_extensions = [ext.replace('.py', '') for ext in os.listdir("./gears") if "__pycache__" not in ext]
loaded_extensions = []

def bot_run():
    bot.loop.create_task(blocks_loop())
    bot.run(config.DISCORD_TOKEN)
    bot.loop.close()

def is_owner(ctx):
    return ctx.message.author.id in config.DISCORD_OWNERS

def is_server_owner(ctx):
    return ctx.message.author.id == ctx.message.server.owner

def is_soakable(ctx):
    s = models.Server.query.filter(models.Server.server_id == str(ctx.message.server.id)).first()
    if s == None:
        return False
    return s.can_soak

@bot.event
async def on_ready():
    print("Loading {} extension(s)...".format(len(startup_extensions)))

    for extension in startup_extensions:
        try:
            bot.load_extension("gears.{}".format(extension.replace(".py", "")))
            loaded_extensions.append(extension)

        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n\t->{}'.format(extension, exc), file=sys.stderr)
    print('Successfully loaded the following extension(s): {}'.format(', '.join(loaded_extensions)))
    print('You can now invite the bot to a server using the following link: https://discordapp.com/oauth2/authorize?&client_id={}&scope=bot&permissions=0'.format(bot.user.id))

last_block_height = -1
async def blocks_loop():
    await bot.wait_until_ready()
    await asyncio.sleep(1)
    global last_block_height
    while not bot.is_closed:
        info = rpc.call.getinfo()
        block_height = int(info["blocks"])
        if block_height > last_block_height:
            #print("Set Discord status to %s" % (str(block_height),))
            last_block_height = block_height
            await bot.change_presence(afk=True, status=discord.Status.online, game=discord.Game(name="Blocks: %s" % (block_height,), type=0))
        await asyncio.sleep(10)

async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            em = discord.Embed(title="Missing args :x:",
                               description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.red())
            await bot.send_message(ctx.message.channel, embed=em)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            em = discord.Embed(title="Missing args :x:",
                               description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.red())
            await bot.send_message(ctx.message.channel, embed=em)


@bot.command(pass_context=True)
@commands.check(is_owner)
async def shutdown(ctx):
    """Shut down the bot"""
    author = str(ctx.message.author)

    try:
        await bot.say("Shutting down...")
        await bot.logout()
        bot.loop.stop()
        print('{} has shut down the bot...'.format(author))

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('{} has attempted to shut down the bot, but the following '
                     'exception occurred;\n\t->{}'.format(author, exc), file=sys.stderr)


@bot.command(pass_context=True)
@commands.check(is_owner)
async def load_gear(ctx, module: str):
    author = str(ctx.message.author)
    module = module.strip()

    try:
        bot.load_extension("gears.{}".format(module))
        print('{} loaded module: {}'.format(author, module))
        loaded_extensions.append(module)
        await bot.say("Successfully loaded {}.py".format(module))

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('{} attempted to load module \'{}\' but the following '
                     'exception occured;\n\t->{}'.format(author, module, exc), file=sys.stderr)
        await bot.say('Failed to load extension {}\n\t->{}'.format(module, exc))

@bot.command(pass_context=True)
@commands.check(is_owner)
async def unload_gear(ctx, module: str):
    author = str(ctx.message.author)
    module = module.strip()

    try:
        bot.unload_extension("gears.{}".format(module))
        print('{} unloaded module: {}'.format(author, module))
        loaded_extensions.remove(module)
        await bot.say("Successfully unloaded {}.py".format(module))

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        await bot.say('Failed to unload extension {}\n\t->{}'.format(module, exc))

@bot.command(pass_context=True)
@commands.check(is_owner)
async def reload_gear(ctx, module: str):
    author = str(ctx.message.author)
    module = module.strip()

    try:
        bot.unload_extension("gears.{}".format(module))
        loaded_extensions.remove(module)
        print('{} reload started on module: {}'.format(author, module))
        bot.load_extension("gears.{}".format(module))
        loaded_extensions.append(module)
        print('{} reload completed on module: {}'.format(author, module))
        await bot.say("Successfully reloaded {}.py".format(module))

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        print('{} attempted to reload module \'{}\' but the following exception occured;\n\t->{}'.format(author, module, exc), file=sys.stderr)
        await bot.say('Failed to reload extension {}\n\t->{}'.format(module, exc))

@bot.command()
@commands.check(is_owner)
async def loaded_gears():
    string = ""
    for cog in loaded_extensions:
        string += str(cog) + "\n"

    await bot.say('Currently loaded extensions:\n```{}```'.format(string))


@bot.event
async def on_server_join(server):
    s = models.Server.query.filter(models.Server.server_id == str(server.id)).first()
    if s == None:
        print("Added to {0}".format(server.name))
        s = models.Server(server)
        s.can_soak = server.large
        models.db_session.add(s)
        models.db_session.commit()

        for channel in server.channels:
            chan = models.Channel.query.filter(models.Channel.channel_id == str(channel.id)).filter(models.Channel.server_id == s.id).first()
            print("%s : %s" % (server, channel))
            if chan is None:
                chan = models.Channel(server, channel)
            models.db_session.add(chan)
        models.db_session.commit()
        print("Added {0} channels".format(server.name))
    else:
        print("Already in {0}".format(server.name))

@bot.event
async def on_server_leave(server):
    s = models.Server.query.filter(models.Server.server_id == str(server.id)).first()
    if s == None:
        print("Leave server attempted: {0} but is not in the db.".format(server.name))
        return
    models.db_session.delete(s)
    models.db_session.commit()
    print("Leave server successfully: {0}".format(server.name))


@bot.event
async def on_channel_create(channel):
    if isinstance(channel, discord.PrivateChannel):
        return
    channel = models.Channel.query.filter(models.Channel.channel_id == str(channel.id)).first()
    if channel is None:
        channel = models.Channel(channel.server, channel)
    models.db_session.add(channel)
    models.db_session.commit()
    print("Channel {0} added to {1}".format(channel.name, channel.server.name))


@bot.event
async def on_channel_delete(channel):
    channel = models.Channel.query.filter(models.Channel.channel_id == str(channel.id)).first()
    if channel is None:
        print("Deletion of Channel attempted: {0} but is not in the db.".format(server.name))
        return
    models.db_session.delete(channel)
    models.db_session.commit()
    print("Channel {0} deleted from {1}".format(channel.name, channel.server.name))


@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.MissingRequiredArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.BadArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.CommandInvokeError):
        print("Exception in command '{}', {}".format(ctx.command.qualified_name, error.original), file=sys.stderr)
        oneliner = "Error in command '{}' - {}: {}\nIf this issue persists, Please report it in the support server.".format(
            ctx.command.qualified_name, type(error.original).__name__, str(error.original))
        await ctx.bot.send_message(channel, oneliner)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.is_private:
        await bot.send_message(message.channel, ':x: Sorry, but I don\'t accept commands through direct messages! Please use the `#bots` channel of your corresponding server!')
        return
    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        if 'help' in message.content.lower():
            await bot.send_message(message.channel, 'Hello! You can find a list of my commands by typing `%shelp` and I will Direct Message you my list.' % (config.DISCORD_PREFIX,))
    await bot.process_commands(message)
