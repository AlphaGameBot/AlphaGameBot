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

import agb.cogwheel
import discord
import os
from discord.ext import commands

class BotInformationCog(agb.cogwheel.MySQLEnabledCogwheel):

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
        _d = agb.cogwheel.getBotInformation()
        view = discord.ui.View()
        linkStyle = discord.ButtonStyle.link
        addTheBot = discord.ui.Button(style=linkStyle, label="Add the Bot!",
                                      url=_d["BOT_INFORMATION"]["INVITE_URL"])
        checkItOut = discord.ui.Button(style=linkStyle, label="Learn More!", url="https://alphagame.dev/alphagamebot/")
        githubBtn = discord.ui.Button(style=linkStyle, label="GitHub",
                                      url="https://github.com/AlphaGameDeveloper/AlphaGameBot")
        view.add_item(item=addTheBot)
        view.add_item(item=checkItOut)
        view.add_item(item=githubBtn)

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
        embed = discord.Embed(title=f"AlphaGameBot {agb.cogwheel.getVersion()}  {build_text}",
                              description=_d["BOT_INFORMATION"]["DESCRIPTION"],
                              colour=discord.Colour.dark_blue())
        embed.add_field(name="Bot Ping", value="{0} milliseconds".format(round(self.bot.latency * 100, 2)))
        embed.add_field(name="Bot version", value=agb.cogwheel.getVersion())
        embed.add_field(name="User Count", value=usercount)
        embed.add_field(name="Server Count", value=len(self.bot.guilds))
        embed.add_field(name="Latest Commit Message", value=self.getCommitMessage())

        await interaction.response.send_message(embed=embed, view=view)