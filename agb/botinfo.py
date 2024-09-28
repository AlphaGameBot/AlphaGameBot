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

import agb.system.cogwheel
import discord
import os
from discord.ext import commands
    
class FeedbackModal(discord.ui.Modal):
    def __init__(self, bot, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.add_item(discord.ui.InputText(label="Feedback", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        _d = agb.system.cogwheel.getBotInformation()
        owner_embed = agb.system.cogwheel.embed(title="AlphaGameBot Feedback", description="A user has submitted feedback!", colour=discord.Colour.dark_blue())
        owner_embed.add_field(name="Feedback", value=self.children[0].value)
        owner_embed.add_field(name='Username', value=interaction.user.name)
        owner_embed.add_field(name='User ID', value=interaction.user.id)

        agb.system.cogwheel.webhook(dataOverride={"embeds": [owner_embed.to_dict()]})
        
        await interaction.response.send_message("Feedback sent!", ephemeral=True)

class CommandSuggestionModal(discord.ui.Modal):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.add_item(discord.ui.InputText(label="Command Name", style=discord.InputTextStyle.short, placeholder="/amazing-command-idea-generator"))
        self.add_item(discord.ui.InputText(label="Command Description", style=discord.InputTextStyle.long, placeholder="What is your command?  What would it do?  Tell me, tell me! :)"))

    async def callback(self, interaction: discord.ApplicationContext):
        description = "**Command Name**: %s\n\n**Command Description**: %s" % (self.children[0].value, self.children[1].value)
        owner_embed = agb.system.cogwheel.embed(title="AlphaGameBot Command Suggestion", description=description)
        owner_embed.add_field(name="User Name", value=interaction.user.name)
        owner_embed.add_field(name="User ID", value=interaction.user.id)

        agb.system.cogwheel.webhook(dataOverride={"embeds": [owner_embed.to_dict()]})
        await interaction.response.send_message("Command Suggestion Sent.  Thank you!", ephemeral=True)
class AboutView(discord.ui.View):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
        _d = agb.system.cogwheel.getBotInformation()
        addTheBot = discord.ui.Button(
            label="Add the Bot!",                          
            url=_d["BOT_INFORMATION"]["INVITE_URL"], row=1)
        checkItOut = discord.ui.Button(label="Learn More!", url="https://alphagame.dev/alphagamebot/", row=1)
        githubBtn = discord.ui.Button(label="GitHub",
                                      url="https://github.com/AlphaGameDeveloper/AlphaGameBot", row=1)
        self.add_item(item=addTheBot)
        self.add_item(item=checkItOut)
        self.add_item(item=githubBtn)
    
    @discord.ui.button(label="Feedback", style=discord.ButtonStyle.primary, row=0)
    async def feedback(self, button: discord.ui.Button, interaction: discord.Interaction):
        button.disabled = True
        button.label = "Feedback Sent!"
        await interaction.response.send_modal(FeedbackModal(self.bot, title="AlphaGameBot Feedback"))

    @discord.ui.button(label="Command Suggestions", style=discord.ButtonStyle.primary, row=0)
    async def command_suggestions(self, button: discord.ui.Button, interaction: discord.ApplicationContext):
        button.disabled = True
        button.label = "Thanks for the suggestion!"
        await interaction.response.send_modal(CommandSuggestionModal(self.bot, title="AlphaGameBot Command Suggestion"))

class BotInformationCog(agb.system.cogwheel.MySQLEnabledCogwheel):

    def getCommitMessage(self):
        """Get the most recent commit message
        This relies on this information being passed through when being deployed
        via Jenkins... Uses the COMMIT_MESSAGE environment variable"""

        message = os.getenv("COMMIT_MESSAGE")

        if message == None:
            # womp womp we cannot get the message so we are screwed...
            return "Unable to get latest commit message :("
        return message

    @commands.slash_command(name="about", description="About AlphaGameBot!")
    async def _about(self, interaction):
        _d = agb.system.cogwheel.getBotInformation()
        view = AboutView(self.bot)        

        # get users
        if self.canUseDatabase:
            c = self.cnx.cursor()
            c.execute("SELECT COUNT(*) FROM user_settings")
            usercount = c.fetchone()[0]
            c.close()
        else: # use the bot's number (sucks but oh well)
            usercount = 0
            for user in self.bot.get_all_members():
                if user.bot:
                    continue
                usercount += 1
        
        self.logger.debug(f"Got user count of {usercount}.")

        build = os.getenv("BUILD_NUMBER")
        if build != None:
            build_text = "(Build #{0})".format(build)
        else:
            build_text = ""
        embed = discord.Embed(title=f"AlphaGameBot {agb.system.cogwheel.getVersion()}  {build_text}",
                              description=_d["BOT_INFORMATION"]["DESCRIPTION"],
                              colour=discord.Colour.dark_blue())
        embed.add_field(name="Bot Ping", value="{0} milliseconds".format(round(self.bot.latency * 100, 2)))
        embed.add_field(name="Bot version", value=agb.system.cogwheel.getVersion())
        embed.add_field(name="User Count", value=usercount)
        embed.add_field(name="Server Count", value=len(self.bot.guilds))
        embed.add_field(name="Latest Commit Message", value=self.getCommitMessage())

        await interaction.response.send_message(embed=embed, view=view)
