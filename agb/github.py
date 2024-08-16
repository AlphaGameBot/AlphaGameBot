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
import os
import json
from agb.requestHandler import handler, formatQueryString

"""
{
      "id": 734892011,
      "node_id": "R_kgDOK82P6w",
      "name": "AlphaGameBot",
      "full_name": "AlphaGameBot/AlphaGameBot",
      "private": false,
      "owner": {
        "login": "AlphaGameBot",
        "id": 170033488,
        "node_id": "O_kgDOCiKBUA",
        "avatar_url": "https://avatars.githubusercontent.com/u/170033488?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/AlphaGameBot",
        "html_url": "https://github.com/AlphaGameBot",
        "followers_url": "https://api.github.com/users/AlphaGameBot/followers",
        "following_url": "https://api.github.com/users/AlphaGameBot/following{/other_user}",
        "gists_url": "https://api.github.com/users/AlphaGameBot/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/AlphaGameBot/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/AlphaGameBot/subscriptions",
        "organizations_url": "https://api.github.com/users/AlphaGameBot/orgs",
        "repos_url": "https://api.github.com/users/AlphaGameBot/repos",
        "events_url": "https://api.github.com/users/AlphaGameBot/events{/privacy}",
        "received_events_url": "https://api.github.com/users/AlphaGameBot/received_events",
        "type": "Organization",
        "site_admin": false
      },
"""

class GithubCog(agb.cogwheel.Cogwheel):

    def __init__(self, *args):
        super().__init__(*args)

        token = os.getenv("GITHUB_TOKEN")

        if not token:
            raise NotImplimentedError("No valid GitHub Token!")
            
        self.GITHUB_HEADERS = {
            "Authorization": "Bearer %s" % token
        }
    group = discord.SlashCommandGroup(name="github", description="Interact with GitHub!")

    async def _github_repo_search_autocomplete(self, interaction: discord.context.AutocompleteContext):
            endpoint = agb.cogwheel.getAPIEndpoint("github", "REPO_SEARCH")
    
            if interaction.value.strip() == "":
                return []
            
            results = []

            r = handler.get(
                formatQueryString(endpoint, {
                    "q": interaction.value
                })
            )            

            j = json.loads(r.text)

            for result in j["items"]:
                results.append(
                    discord.OptionChoice(
                        name = result["full_name"],
                        value = result["id"]
                    )
                )
            return results
            
    @group.command(name="octocat", description="Get an octocat!")
    async def _octocat(self, interaction: discord.context.ApplicationContext):
        r = handler.get(
            agb.cogwheel.getAPIEndpoint("github", "OCTOCAT", headers=self.GITHUB_HEADERS),
        )

        await interaction.response.send_message("```\n%s\n```" % r.text)
        

    @group.command(name="repository")
    async def _repository(self, interaction: discord.context.ApplicationContext,
                          repository: discord.Option(int, description="Repository to use", autocomplete=_github_repo_search_autocomplete)):

        await interaction.response.defer()
        
        r = handler.get(
            agb.cogwheel.getAPIEndpoint("github", "GET_REPO_BY_ID").format(repository)
        )

        data = json.loads(r.text)

        author = discord.EmbedAuthor(
            name     = data["full_name"],
            url      = "https://github.com/%s" % data["full_name"],
            icon_url = data["owner"]["avatar_url"]            
        )
        embed = agb.cogwheel.embed(
            title       = data["name"],
            description = "To Be Implimented.",
            author      = author
        )

        
        # Fire off that embed!!
        await interaction.followup.send(embed = embed)
