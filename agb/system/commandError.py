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
from discord import commands
import agb.cogwheel
import agb.requestHandler
import time
import nltk
from dhooks import Webhook
logger = logging.getLogger("listener")

ERROR_JOKES = [
    "Looks like someone tripped over the cables again. Let's try that command one more time, shall we?",
    "Whoops! Gremlins must have invaded our servers. Let's hope they're more cooperative next time.",
    "Error 404: Command not found... because it's hiding from its responsibilities! 😄",
    "Houston, we have a problem. But don't worry, I've sent a team of highly trained bots to investigate.",
    "Well, that's embarrassing. Seems like our bot decided to take a coffee break instead of executing the command.",
    "Hold on, let me check the manual... Oh wait, we don't have one! Looks like we're improvising today.",
    "Looks like someone forgot to feed the hamsters powering our servers. No worries, we'll get them some snacks ASAP.",
    "Unexpected error: Our bot got stage fright! It happens to the best of us.",
    "Ah, the classic case of 'Oops, I did it again' - our bot's favorite song when it messes up.",
    "Well, that's a new one! Our bot just pulled a disappearing act. Don't worry, we'll track it down.",
    "Command failed due to a quantum fluctuation in the server matrix. Don't worry, we're recalibrating.",
    "Looks like our bot is taking a quick nap. Wakey-wakey, bot! Time to get back to work.",
    "Error: Command execution terminated unexpectedly. Our bot might need some caffeine to wake up.",
    "Oops! Our bot went on a coffee run instead of executing the command. We'll have it back on track in no time.",
    "Hold tight! Our bot is currently solving the mystery of the missing semicolon. It might take a moment.",
    "Looks like our bot is experiencing a moment of existential crisis. It'll be back once it figures out the meaning of life.",
    "Command failed due to a cosmic alignment issue. We're waiting for Mercury to get out of retrograde.",
    "Our bot is currently attending a crash course on error handling. It'll be a pro in no time.",
    "Error: Command execution encountered a black hole in the code. We're sending in reinforcements.",
    "Command failed due to a disagreement between our bot and its inner workings. We're working on conflict resolution.",
    "Oops! Our bot's GPS malfunctioned, and it took a wrong turn in the code. We'll reroute it ASAP.",
    "Looks like our bot took a detour through the Bermuda Triangle of coding. We'll guide it back to safety.",
    "Error: Command execution encountered a glitch in the matrix. Neo is on standby to help us out.",
    "Our bot tried to juggle too many commands at once and dropped the ball. We're picking up the pieces.",
    "Command failed due to a syntax error. Our bot is brushing up on its grammar skills.",
    "Oops! Our bot tried to do a backflip but ended up crashing instead. We'll get it back on its feet.",
    "Looks like our bot encountered a wild Pikachu in the code. We're calling in Ash Ketchum for assistance.",
    "Error: Command execution encountered a hiccup in the space-time continuum. We're waiting for the fabric of reality to settle.",
    "Our bot tried to do a barrel roll but ended up crashing instead. We'll roll it back to safety.",
    "Command failed due to a coding hiccup. Our bot is holding its breath until it passes.",
    "Oops! Our bot mistook the command for a recipe and started cooking up a storm. We'll clean up the kitchen.",
    "Looks like our bot wandered into the wrong neighborhood in the code. We'll escort it back to safety.",
    "Error: Command execution encountered a hiccup in the server space-time continuum. We're recalibrating.",
    "Our bot tried to do a cartwheel but ended up crashing instead. We'll flip it back to reality.",
    "Command failed due to a quantum entanglement issue. We're untangling the mess as we speak.",
    "Oops! Our bot got caught in a time loop. We're breaking the cycle as we speak.",
    "Looks like our bot encountered a glitch in the matrix. We're rebooting it to clear the system.",
    "Error: Command execution encountered a cosmic anomaly. Our bot is investigating the anomaly.",
    "Our bot tried to do a magic trick but ended up pulling a disappearing act. We'll bring it back.",
    "Command failed due to a coding conundrum. Our bot is solving the puzzle as we speak.",
    "Oops! Our bot got caught in a time warp. We're untangling the timeline as we speak.",
    "Looks like our bot wandered into the Bermuda Triangle of coding. We're sending in a rescue team.",
    "Error: Command execution encountered a ghost in the machine. We're calling in the Ghostbusters.",
    "Our bot tried to do a moonwalk but ended up crashing instead. We'll smooth out the steps.",
    "Command failed due to a cosmic alignment issue. We're waiting for the stars to align.",
    "Oops! Our bot got tangled up in a web of code. We're unraveling the mess as we speak.",
    "Looks like our bot stumbled into a parallel universe. We're bringing it back to reality.",
    "Error: Command execution encountered a glitch in the matrix. We're reprogramming the code.",
    "Our bot tried to do a somersault but ended up crashing instead. We'll cushion the landing.",
    "Command failed due to a hiccup in the server matrix. We're recalibrating the system.",
    "Oops! Our bot got caught in a time loop. We're breaking the cycle as we speak.",
    "Looks like our bot took a wrong turn at the intersection of code. We'll reroute it.",
    "Error: Command execution encountered a hiccup in the server space-time continuum. We're recalibrating.",
    "Our bot tried to do a cartwheel but ended up crashing instead. We'll flip it back to reality.",
    "Command failed due to a quantum entanglement issue. We're untangling the mess as we speak.",
    "Oops! Our bot got lost in the labyrinth of code. We're sending in Theseus to rescue it.",
    "Looks like our bot encountered a glitch in the matrix. We're rebooting it to clear the system.",
    "Error: Command execution encountered a cosmic anomaly. Our bot is investigating the anomaly.",
    "Our bot tried to do a magic trick but ended up pulling a disappearing act. We'll bring it back.",
    "Command failed due to a coding conundrum. Our bot is solving the puzzle as we speak.",
    "Oops! Our bot got caught in a time warp. We're untangling the timeline as we speak.",
    "Looks like our bot wandered into the Bermuda Triangle of coding. We're sending in a rescue team.",
    "Error: Command execution encountered a ghost in the machine. We're calling in the Ghostbusters.",
    "Our bot tried to do a moonwalk but ended up crashing instead. We'll smooth out the steps.",
    "Command failed due to a cosmic alignment issue. We're waiting for the stars to align.",
    "Oops! Our bot got tangled up in a web of code. We're unraveling the mess as we speak.",
    "Looks like our bot stumbled into a parallel universe. We're bringing it back to reality.",
    "Error: Command execution encountered a glitch in the matrix. We're reprogramming the code.",
    "Our bot tried to do a somersault but ended up crashing instead. We'll cushion the landing.",
    "Command failed due to a hiccup in the server matrix. We're recalibrating the system.",
    "Oops! Our bot got caught in a time loop. We're breaking the cycle as we speak.",
    "Looks like our bot took a wrong turn at the intersection of code. We'll reroute it.",
    "Error: Command execution encountered a hiccup in the server space-time continuum. We're recalibrating.",
    "Our bot tried to do a cartwheel but ended up crashing instead. We'll flip it back to reality.",
    "Command failed due to a quantum entanglement issue. We're untangling the mess as we speak.",
    "Oops! Our bot got lost in the labyrinth of code. We're sending in Theseus to rescue it.",
    "Looks like our bot encountered a glitch in the matrix. We're rebooting it to clear the system.",
    "Error: Command execution encountered a cosmic anomaly. Our bot is investigating the anomaly.",
    "Our bot tried to do a magic trick but ended up pulling a disappearing act. We'll bring it back.",
    "Command failed due to a coding conundrum. Our bot is solving the puzzle as we speak.",
    "Oops! Our bot got caught in a time warp. We're untangling the timeline as we speak.",
    "Looks like our bot wandered into the Bermuda Triangle of coding. We're sending in a rescue team.",
    "Error: Command execution encountered a ghost in the machine. We're calling in the Ghostbusters.",
    "Our bot tried to do a moonwalk but ended up crashing instead. We'll smooth out the steps.",
    "Command failed due to a cosmic alignment issue. We're waiting for the stars to align.",
    "Oops! Our bot got tangled up in a web of code. We're unraveling the mess as we speak.",
    "Looks like our bot stumbled into a parallel universe. We're bringing it back to reality.",
    "Error: Command execution encountered a glitch in the matrix. We're reprogramming the code.",
    "Our bot tried to do a somersault but ended up crashing instead. We'll cushion the landing.",
    "Command failed due to a hiccup in the server matrix. We're recalibrating the system.",
    "Oops! Our bot got caught in a time loop. We're breaking the cycle as we speak.",
    "Looks like our bot took a wrong turn at the intersection of code. We'll reroute it.",
    "Error: Command execution encountered a hiccup in the server space-time continuum. We're recalibrating.",
    "Our bot tried to do a cartwheel but ended up crashing instead. We'll flip it back to reality.",
    "Command failed due to a quantum entanglement issue. We're untangling the mess as we speak."
]


class ErrorOptionView(discord.ui.View):
    def __init__(self, error, interaction, user: discord.User):
        super().__init__()
        self.user = user
        self._error = error
        self.realinteraction = interaction
        self.logger = logging.getLogger('listener')

    @discord.ui.button(label="Report this Bug!", style=discord.ButtonStyle.green, emoji="📢")
    async def reportError(self, button: discord.ui.Button, interaction: commands.context.ApplicationContext):
        # Set the button to be disabled to prevent spamming. (button.disabled)

        # Check if the user is the same one who originally did the command!
        if interaction.user.id != self.user.id:
            # ephemeral=True adds the "Only you can see this message" message
            await interaction.response.send_message("Only the person who originally ran the command can send a bug report :(", ephemeral=True)
            return
        
        if agb.cogwheel.isDebugEnv:
            # well this is kind of useless
            self.logger.info("Bug reporting was disabled, as this is a debug build.  If you need to test bug reporting, remove the 'DEBUG' environment variable.  Also, be sure to set the 'WEBHOOK' so you can actually send the report!")
            await interaction.response.send_message("Naturally, you shouldn't be able to send a bug report in a debug build, as there are lots of bugs in this.", ephemeral=True)
            return

        data = self.realinteraction.interaction.to_dict()
        arguments = ""
        for x in data["data"]["options"]:
            rtype = type(x["value"])
            if isinstance(x["value"], bool):
                rtype = "Boolean"
            elif isinstance(x["value"], int):
                rtype = "Integer"
            elif isinstance(x["value"], str):
                rtype = "String"
            
            arguments = arguments + "* `{0}: {1}` (Type: `{2}`)\n".format(x["name"], x["value"], rtype)
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
                   repr(self._error),
                   self.realinteraction.command,
                   arguments,
                   ''.join(traceback.format_tb(self._error.__traceback__)),
                   time.ctime())}, "Error report by %s" % self.user.name)
        
        
        # Stop the button from being used again.  Thank you for sending the bug report, but I don't need spam.
        # Just use 'disabled=True' to disable it, and also change the button text to alert the user of the status.

        # We define a success by getting a 200 (OK) or 204 (No Content) response code.  Anything else, we would call
        # an error.  I've only seen Discord send 204 in their webhooks, but I also include 200 because it is better.
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


async def handleApplicationCommandError(interaction: commands.context.ApplicationContext, error):
    embed = agb.cogwheel.embed(title="An error occured...", description="An internal server error has occured, and the bot cannot fulfill your request.  You may be able \
                                                                       to make it work by trying again.\nSorry about that! (awkward face emoji)",
                               color=discord.Color.red())
    if not agb.cogwheel.isDebugEnv:
        embed.add_field(name="Joke", value=random.choice(ERROR_JOKES))
    if agb.cogwheel.isDebugEnv:
        embed.add_field(name="Error message", value="`{0}`".format(repr(error)))
    embed.set_thumbnail(url="https://static.alphagame.dev/alphagamebot/img/error.png")
    try:
        await interaction.response.send_message(embed=embed, view=ErrorOptionView(error, interaction, interaction.user))
    except discord.errors.InteractionResponded:
        logging.debug("Using a followup message to send the error message because the interaction was already responded to.")
        await interaction.followup.send(embed=embed, view=ErrorOptionView(error, interaction, interaction.user))
    if agb.cogwheel.isDebugEnv:
        # Pass the error along to the Python Error Handler (console)
        raise error 
