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
from dhooks import Webhook
logger = logging.getLogger("listener")


class ErrorOptionView(discord.ui.View):
    def __init__(self, error, interaction, user: discord.User):
        super().__init__()
        self.user = user
        self._error = error
        self.realinteraction = interaction
    @discord.ui.button(label="Report this Bug!", style=discord.ButtonStyle.green, emoji="📢")
    async def reportError(self, button, interaction: commands.context.ApplicationContext):
        # Set the button to be disabled to prevent spamming. (button.disabled)
        button.disabled = True
        button.label = "Error Reported!"
        await interaction.response.edit_message(view=self)

        # Send information to the webhook
        webhook = Webhook.Async(os.getenv("WEBHOOK"))
        

        data = self.realinteraction.interaction.to_dict()
        arguments = ""
        for x in data["data"]["options"]:
            arguments = arguments + "* `{0}: {1}`\n".format(x["name"], x["value"])
        await webhook.send("""
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

        # We no longer need the Webhook connection.  Close it!
        await webhook.close()
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
        await interaction.response.send_message(embed=embed, view=ErrorOptionView(error, interaction, interaction.user))
    except discord.errors.InteractionResponded:
        await interaction.followup.send(embed=embed, view=ErrorOptionView(error, interaction))
    if agb.cogwheel.isDebugEnv:
        # Pass the error along to the Python Error Handler (console)
        raise error 
