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
import discord
from discord import commands
import agb.cogwheel
import agb.requestHandler
import time
logger = logging.getLogger("listener")


def webhook(message):
    """
    Send a message to the specified webhook URL.

    Args:
    webhook_url (str): The URL of the webhook.
    message (str): The message to send.

    Returns:
    bool: True if the message was sent successfully, False otherwise.
    """
    payload = {'content': message}
    try:
        response = agb.requestHandler.handler.post(os.getenv("WEBHOOK"), payload)
        if response.status_code == 200:
            print("Message sent successfully")
            return True
        else:
            print(f"Failed to send message. Status code: {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"Unable to send information to webhook: {e}")
        return False


class ErrorOptionView(discord.ui.View):
    def __init__(self, error, interaction):
        super().__init__()
        self._error = error
        self.realinteraction = interaction
    @discord.ui.button(label="Report this Bug!", style=discord.ButtonStyle.green, emoji="📢")
    async def reportError(self, button, interaction: commands.context.ApplicationContext):
        button.disabled = True
        button.label = "Error Reported!"
        await interaction.response.edit_message(view=self)

        data = self.realinteraction.interaction.to_dict()
        arguments = ""
        for x in data["data"]["options"]:
            arguments = arguments + "* `{0}: {1}`\n".format(x["name"], x["value"])
        webhook("""
# AlphaGameBot Error Reporter
An error was reported.  Here is some information!

**User**: `{0}` (Nick: *{1}*)
**Error Message**: `{2}`
**Command Affected**: `/{3}`

**Command Arguments**
{4}

**Reported At** {5}
        """.format(interaction.user.name,
                   interaction.user.nick,
                   repr(self._error),
                   self.realinteraction.command,
                   arguments,
                   time.ctime()))

        button.disabled = True
        button.label = "Error Reported!"
        # It seems that editing the original message is not needed. :/
        #await interaction.followup.edit_message(view=self)

async def handleApplicationCommandError(interaction: commands.context.ApplicationContext, error):
    embed = agb.cogwheel.embed(title="An error occured...", description="An internal server error has occured, and the bot cannot fulfill your request.  You may be able \
                                                                       to make it work by trying again.\nSorry about that! (awkward face emoji)",
                               color=discord.Color.red())

    if agb.cogwheel.isDebugEnv:
    	embed.add_field(name="Error message", value="`{0}`".format(repr(error)))
    embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/error.png")
    try:
        await interaction.response.send_message(embed=embed, view=ErrorOptionView(error, interaction))
    except discord.errors.InteractionResponded:
        await interaction.followup.send(embed=embed, view=ErrorOptionView(error, interaction))
    if agb.cogwheel.isDebugEnv:
        raise error
