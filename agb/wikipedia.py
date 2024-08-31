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

import agb.cogwheel
import discord
import urllib.parse
from discord.ext import commands
import json
from agb.system.requestHandler import handler, formatQueryString

class WikipediaCog(agb.cogwheel.Cogwheel):
    group = discord.SlashCommandGroup(name="wikipedia", description="Wikipedia commands!")

    async def _wikipedia_search_autocomplete(self, interaction: discord.context.AutocompleteContext):
        endpoint = agb.cogwheel.getAPIEndpoint("wikipedia", "API_ENDPOINT")

        if interaction.value.strip() == "":
            return []
        
        url = formatQueryString(endpoint, {
            "format": "json",
            "list": "search",
            "action": "query",
            "srlimit": 10,
            "srsearch": interaction.value,
            "srwhat": "text"
        })

        request = handler.get(url, attemptCache=False)
        response = json.loads(request.text)["query"]
        results = []
        for entry in response["search"]:
            results.append(entry["title"])

        return results

    @group.command(name="summary", description="Get a summmary of a Wikipedia article!")
    async def _summary(self, interaction: discord.context.ApplicationContext,
                       page: discord.Option(str, description="The page to summarize!", autocomplete=_wikipedia_search_autocomplete)): # type: ignore
        endpoint = agb.cogwheel.getAPIEndpoint("wikipedia", "API_ENDPOINT") # this is api.php

        
        # get the page id
        pageidrequest = handler.get(
            formatQueryString(
                endpoint,
                {
                    "format": "json",
                    "action": "query",
                    "titles": page,
                    "indexpageids": None
                }
        ), attemptCache=False)
        pageidresponse = json.loads(pageidrequest.text)["query"]
        pageid = pageidresponse["pageids"][0]
        if pageid == "-1": # missing
            await interaction.response.send_message(":x: The page `%s` does not seem to exist... Maybe you misspelled it?" % page)
            return


        url = formatQueryString(endpoint, 
                                {
                                    "format": "json", # respond in a way we can easily read
                                    "action": "query",
                                    "prop": "extracts",
                                    "exintro": None,
                                    "explaintext": None,
                                    "redirects": "1",
                                    "pageids": pageid
                                })
        getSummaryResponse = handler.get(url, attemptCache=False)
        summary = json.loads(getSummaryResponse.text)["query"]

        # this is stupid code lol, make a pr if you know how to fix this
        page = summary["pages"][list(summary["pages"].keys())[0]]

        embed = agb.cogwheel.embed(
            title=page["title"],
            description=page["extract"] if page["extract"] != None else "No Extract Given"
        )


        await interaction.response.send_message(embed=embed)

