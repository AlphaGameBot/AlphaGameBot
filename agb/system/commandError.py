#      AlphaGameBot - A Discord bot that's free and (hopefully) doesn't suck
#      Copyright (C) 2024  Damien Boisvert (AlphaGameDeveloper)
#
#      AlphaGameBot is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      AlphaGameBot is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with AlphaGameBot.  If not, see <https://www.gnu.org/licenses/>.
import logging
import os
import random
import traceback
import discord
from discord.ext import commands
import agb.cogwheel
import agb.requestHandler
import time
from json import load
from mysql.connector.errors import OperationalError

logger = logging.getLogger("listener")

with open("assets/error_jokes.json", "r") as f:
    ERROR_JOKES = load(f)

class ErrorOptionView(discord.ui.View):
    def __init__(self, error, interaction, user: discord.User):
        super().__init__()
        self.user = user
        self._error = error
        self.realinteraction = interaction
        self.logger = logging.getLogger('listener')

    @discord.ui.button(label="Report this Bug!", style=discord.ButtonStyle.green, emoji="📢")
    async def reportError(self, button: discord.ui.Button, interaction: discord.ApplicationContext):
        # Check if the user is the same one who originally did the command!
        if interaction.user.id != self.user.id:
            # ephemeral=True adds the "Only you can see this message" message
            await interaction.response.send_message(":x: Only the person who originally ran the command can send a bug report!", ephemeral=True)
            return

        if isinstance(self._error, discord.ApplicationCommandInvokeError):
            error = self._error.original
        else:
            error = self._error
        
        if False: # agb.cogwheel.isDebugEnv:
            # well this is kind of useless
            self.logger.info("Bug reporting was disabled, as this is a debug build.  If you need to test bug reporting, remove the 'DEBUG' environment variable.  Also, be sure to set the 'WEBHOOK' so you can actually send the report!")
            await interaction.response.send_message(":x: Naturally, you shouldn't be able to send a bug report in a debug build, as there is no real benefit of doing so.  If you are the developer, please check the Python console.  Otherwise, please inform the developer of this bug!.", ephemeral=True)
            return

        data = self.realinteraction.interaction.to_dict()
        arguments = ""
        try:
            for x in data["data"]["options"]:
                rtype = type(x["value"])
                if isinstance(x["value"], bool):
                    rtype = "Boolean"
                elif isinstance(x["value"], int):
                    rtype = "Integer"
                elif isinstance(x["value"], str):
                    rtype = "String"
                
                arguments = arguments + "* `{0}: {1}` (Type: `{2}`)\n".format(x["name"], x["value"], rtype)
        except KeyError:
            arguments = "*No Arguments.*"
        response = agb.requestHandler.handler.post(os.getenv("WEBHOOK"), {"content": """
# AlphaGameBot Error Reporter
An error was reported.  Here is some information!

**User**: `{0}` (Nick: *{1}*)
**Error Message**: `{2}`
**Command Affected**: `/{3}`

**Command Arguments**
{4}

**Python Traceback**
```
{5}
```

**Reported At** {6}
        """.format(interaction.user.name,
                   interaction.user.nick,
                   repr(error),
                   self.realinteraction.command,
                   arguments,
                   ''.join(traceback.format_tb(error.__traceback__)),
                   time.ctime())}, "Error report by %s" % self.user.name)
        
        
        # Stop the button from being used again.  Thank you for sending the bug report, but I don't need spam.
        # Just use 'disabled=True' to disable it, and also change the button text to alert the user of the status.

        # We define a success by getting a 200 (OK) or 204 (No Content) response code.  Anything else, we would call
        # an error.  I've only seen Discord send 204 in their webhooks, but I also include 200 just in case.
        if response.status_code in [200, 204]: # Success!
            ok = True
            button.label = "Error Reported!"
        else: # womp womp error :(
            ok = False
            button.label = "Error while sending bug report!"
            button.emoji = None
            button.style = discord.ButtonStyle.danger # red

        # Disable the button so it cannot be used again
        button.disabled = True

        # Update the message to reflect the changes to the button.
        await interaction.response.edit_message(view=self)

        # We don't need to send a dm, or do anything else if the bug report failed
        if not ok:
            return
        
        
        # Send a DM thanking the user for reporting the bug (I will eventually add a way to not get a DM)
        dm = await self.user.create_dm()
        sent_embed = agb.cogwheel.embed(
            title="✅ Bug Report Recieved!",
            description=f"""
Hey, {self.user.name}!

I just got your bug report, and will try to fix it soon!  Thanks for helping me squash those bugs!
People like you help AlphaGameBot be the Discord bot we all know it can be, and I couldn't do it without your bug reports!
Anyway, that command that gave you a hard time (`/{self.realinteraction.command}`) should be fixed soon.  While you wait, why not check out the [GitHub repository](https://github.com/AlphaGameDeveloper/AlphaGameBot/)?

Cheers,
*AlphaGameDeveloper*

*Note: Your bug report will be processed as per the Privacy Policy.  (It's fair.. Don't worry!)*""",
            color=discord.Color.green()
        )
        view = discord.ui.View()

        btn1 = discord.ui.Button(label="GitHub", url="https://github.com/AlphaGameDeveloper/AlphaGameBot", style=discord.ButtonStyle.link)
        btn2 = discord.ui.Button(label="Privacy Policy", emoji="📜", url="https://alphagame.dev/alphagamebot/privacy", style=discord.ButtonStyle.link)
        
        view.add_item(item=btn1)
        view.add_item(item=btn2)

        await dm.send(embed=sent_embed, view=view)


async def handleApplicationCommandError(interaction: discord.ApplicationContext, error):
    try:
        # big booty errors like this
        trueerror = error.original
        if isinstance(error.original, discord.Forbidden):
            await interaction.response.send_message(":x: The bot does not have sufficient permissions to do that.")
            return
        elif isinstance(error.original, discord.errors.NotFound):
            await interaction.response.send_message(":x: The bot took too long to respond.  Please try again.")
            return
        elif isinstance(error.original, OperationalError):
            await interaction.response.send_message(":x: Internal Database Error.  Please try again later!")
            return
    except AttributeError:
        # commands.xxx error
        trueerror = error
        if isinstance(error, commands.MissingPermissions):
            await interaction.response.send_message(":x: Sorry, but you don't have sufficient permissions to do that!")
            return
        
    embed = agb.cogwheel.embed(title="An error occured...", description="An internal server error has occured, and the bot cannot fulfill your request.  You may be able \
                                                                       to make it work by trying again.\nSorry about that! (awkward face emoji)",
                               color=discord.Color.red())
    if not agb.cogwheel.isDebugEnv:
        embed.add_field(name="Joke", value=random.choice(ERROR_JOKES))
    if agb.cogwheel.isDebugEnv:
        embed.add_field(name="Error message", value="`{0}`".format(repr(trueerror)))
    embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/error.png")
    try:
        await interaction.response.send_message(embed=embed, view=ErrorOptionView(error, interaction, interaction.user))
    except discord.errors.InteractionResponded:
        logging.debug("Using a followup message to send the error message because the interaction was already responded to.")
        await interaction.followup.send(embed=embed, view=ErrorOptionView(error, interaction, interaction.user))
    if agb.cogwheel.isDebugEnv:
        # Pass the error along to the Python Error Handler (console)
        raise error 
