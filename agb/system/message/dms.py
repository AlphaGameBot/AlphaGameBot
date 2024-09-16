#    AlphaGameBot - A Discord bot that's free and (hopefully) doesn't suck
#    Copyright (C) 2024  Damien Boisvert (AlphaGameDeveloper)

#    AlphaGameBot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    AlphaGameBot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with AlphaGameBot.  If not, see <https://www.gnu.org/licenses/>.

import discord
from discord.ext import commands
import logging
import agb.cogwheel
import agb.system.onboarding
import agb.system.message.announcements
import mysql.connector
from agb.system.requestHandler import handler
from mysql.connector import (connection)

global dms_command_list
with open("assets/dms_command_list.txt", "r") as f:
    dms_command_list = f.read()

async def command_optin(
        ctx: discord.Message,
        cnx: connection.MySQLConnection,
        CAN_USE_DATABASE: bool):
    """This function handles opt-in requests for DM annnouncements"""
    if not CAN_USE_DATABASE:
        await ctx.reply(":x: Sorry, but I can't process your request because the database is not enabled.")
        return
    
    logger = logging.getLogger('system')
    cursor = cnx.cursor()
    
    cursor.execute("SELECT announcements FROM user_settings WHERE userid = %s", [ctx.author.id])
    r = cursor.fetchone()[0]
    logger.debug("optin: Current is %s", r)
    currentSetting = bool(r)

    if currentSetting:
        await ctx.reply(":tada: Guess what?  You're already opted in!\n"
                               "-# You can opt out at any time by typing `.optout`.")
        return
    else:
        cursor.execute("UPDATE user_settings SET announcements = 1 WHERE userid = %s", [ctx.author.id])
        cnx.commit()
        await ctx.reply(":white_check_mark: You've been successfully opted in!  You'll now receive DM announcements from me.\n"
                               "-# You can opt out at any time by typing `.optout`.")

async def command_optout(
        ctx: discord.Message,
        cnx: connection.MySQLConnection,
        CAN_USE_DATABASE: bool):
    """This function handles opt-out requests for DM annnouncements"""
    if not CAN_USE_DATABASE:
        await ctx.reply(":x: Sorry, but I can't process your request because the database is not enabled.")
        return
    
    logger = logging.getLogger('system')
    cursor = cnx.cursor()

    cursor.execute("SELECT announcements FROM user_settings WHERE userid = %s", [ctx.author.id])
    currentSetting = cursor.fetchone()[0]
    logger.debug("optout: Current is %s", currentSetting)

    if not currentSetting:
        await ctx.reply(":x: You've already opted out of DM announcements!\n"
                                 "-# You can opt in at any time by typing `.optin`.")
        return
    
    else:
        cursor.execute("UPDATE user_settings SET announcements = 0 WHERE userid = %s", [ctx.author.id])
        cnx.commit()
        await ctx.reply(":white_check_mark: You've been successfully opted out!  You'll no longer receive DM announcements from me.\n"
                               "-# You can opt in at any time by typing `.optin`.")
        
async def command_optstatus(
        ctx: discord.Message,
        cnx: connection.MySQLConnection,
        CAN_USE_DATABASE: bool):
    """This function allows users to see if they're opted in or out of DM announcements"""
    if not CAN_USE_DATABASE:
        await ctx.reply(":x: Sorry, but I can't process your request because the database is not enabled.")
        return
    
    logger = logging.getLogger('system')
    cursor = cnx.cursor()

    cursor.execute("SELECT announcements FROM user_settings WHERE userid = %s", [ctx.author.id])
    currentSetting = cursor.fetchone()[0]
    logger.debug("optstatus: Current is %s (Evaluates to %s)", currentSetting, bool(currentSetting))

    if currentSetting:
        await ctx.reply(":tada: You're currently opted in to receive DM announcements from me!\n"
                               "-# You can opt out at any time by typing `.optout`.")
        return
    else:
        await ctx.reply(":x: You're currently opted out of DM announcements from me.\n"
                               "-# You can opt in at any time by typing `.optin`.")
        return

async def command_blast(bot, ctx, cnx, CAN_USE_DATABASE):
    if ctx.author.id != agb.cogwheel.getBotInformation()["OWNER_ID"]:
        await ctx.reply(":x: Nice try, but you're not allowed to use this command. ;)")
        return
    t = await agb.system.message.announcements.blast_announcement(bot, cnx, CAN_USE_DATABASE)
    await ctx.reply(t)

async def command_blastpreview(bot, ctx, cnx):
    if ctx.author.id != agb.cogwheel.getBotInformation()["OWNER_ID"]:
        await ctx.reply(":x: Nice try, but you're not allowed to use this command. ;)")
        return
    rendered_text = agb.system.message.announcements.render_announcement_template(handler.get(
        agb.cogwheel.getBotInformation()["ANNOUNCEMENT_URL"],
        attemptCache=False).text)
    await ctx.reply(rendered_text)

async def command_blastdryrun(bot, ctx, cnx, CAN_USE_DATABASE):
    if ctx.author.id != agb.cogwheel.getBotInformation()["OWNER_ID"]:
        await ctx.reply(":x: Nice try, but you're not allowed to use this command. ;)")
        return
    t = await agb.system.message.announcements.blast_announcement(bot, cnx, CAN_USE_DATABASE, dry_run=True)
    await ctx.reply(t)

async def handleDMMessage(bot: commands.Bot,
                          ctx: discord.Message,
                          cnx: connection.MySQLConnection,
                          CAN_USE_DATABASE: bool):
    """This function handles messages sent to the bot in DMs.
    
    Doesn't do much at the moment, but I'm planning on adding some cool features using this!
    
    Args:
        ctx (discord.Message): The message context.
    """
    if ctx.guild: return
    if ctx.author.bot: return
    
    
    commands = {
        "optin": lambda: command_optin(ctx, cnx, CAN_USE_DATABASE),
        "optout": lambda: command_optout(ctx, cnx, CAN_USE_DATABASE),
        "optstatus": lambda: command_optstatus(ctx, cnx, CAN_USE_DATABASE),
        "blast": lambda: command_blast(bot, ctx, cnx, CAN_USE_DATABASE),
        "blastpreview": lambda: command_blastpreview(bot, ctx, cnx),
        "blastdryrun": lambda: command_blastdryrun(bot, ctx, cnx, CAN_USE_DATABASE)
    }

    logger = logging.getLogger('system')

    await ctx.channel.trigger_typing()
    content = ctx.content.strip()

    isCommand = ctx.content.startswith(".")
    logger.debug(f"DM message received from {ctx.author} with content: {content}.  IsCommand: {isCommand}")
    if isCommand:
        # add the user to the database if they're not already in it
        await agb.system.onboarding.initalizeNewUser(cnx, CAN_USE_DATABASE, ctx.author.id)

        command = ctx.content.split(" ")[0][1:].lower()
        logger.debug(f"Command: {command}")
        if command == "help":
            await ctx.reply("```\n%s\n```" % dms_command_list)
            return
        try:
            command = commands[command]
        except KeyError:
            await ctx.reply(":x: I'm sorry, but that command is not recognized.  Please type `.help` for a list of commands.")
            return
        
        try:
            await command()
            return
        except Exception as e:
            if agb.cogwheel.isDebugEnv:
                await ctx.reply(f":x: Internal Error: `{repr(e)}`")
            else:
                await ctx.reply(":x: An error occurred while processing your command.  Please try again later.")
            return

    v = discord.ui.View()

    # support server
    v.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Support Server", url="https://discord.gg/ECJS6ssyf4"))

    # github
    v.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="GitHub", url="https://github.com/AlphaGameBot/AlphaGameBot"))

    # webpage
    v.add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Webpage", url="https://alphagame.dev/alphagamebot"))

    await ctx.reply(f"Hello, {ctx.author.mention}! DMs are not supported at this time. If you need help, please join the support server!\n"
                           "Don't worry, though!  I've got some nice features planned that involve DMs!\n"
                           "-# There are a few commands you can do in DMs.  Type `.help` to see them.", view=v)