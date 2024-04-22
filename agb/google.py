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

from googlesearch import search
import discord
import logging
import agb.cogwheel

class GoogleCog(agb.cogwheel.Cogwheel):
    @discord.command(name="google", description="Search on Google (for those of you who don't wanna open Chrome :/)")
    async def _google(self, interaction,
                      query: discord.Option(str, description="The search term that you want"),
                      number: discord.Option(int, description="The number of results you want the bot to yield",
                                             default=5),
                      lang: discord.Option(str, description="The language for the searches!", value="en")):
        self.logger.debug("Google called")
        data = search(query, num_results=number, lang=lang, advanced=True)
        text = ""
        for result in data:
            text = text + "[{0}]({1}) - {2}\n".format(result.title, result.url, result.description)
        if len(text) > 2000:
            await interaction.response.send_message(":x: ERROR: Message body too long ({} > 2000)".format(len(text)))
        await interaction.response.send_message(text)