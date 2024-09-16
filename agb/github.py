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

import agb.system.cogwheel
import discord
import os
import json
import time
from validators import url as is_valid_url
from requests import Response
from agb.system.requestHandler import handler, formatQueryString

class NoGitHubCredentialsError(Exception):
    """Error for when GitHub credentials are not defined"""
    pass

class GitHubAPIError(Exception):
    """Error for when the GitHub API returns an error"""
    pass

class GithubCog(agb.system.cogwheel.Cogwheel):

    def __init__(self, *args):
        super().__init__(*args)

        token = os.getenv("GITHUB_TOKEN")

        if not token:
            raise NoGitHubCredentialsError("No valid GitHub Token!")
            
        self.GITHUB_HEADERS = {
            "Authorization": "Bearer %s" % token
        }
    group = discord.SlashCommandGroup(name="github", description="Interact with GitHub!")

    async def _github_repo_search_autocomplete(self, interaction: discord.context.AutocompleteContext):
            endpoint = agb.system.cogwheel.getAPIEndpoint("github", "REPO_SEARCH")
    
            if interaction.value.strip() == "":
                return []
            
            results = []

            r = handler.get(
                formatQueryString(endpoint, {
                    "q": interaction.value
                }), headers=self.GITHUB_HEADERS, attemptCache=False
            )            
            if not await self.cushionGitHubAPIResponse(r, interaction, autoResponse=False):
                raise GitHubAPIError("GitHub API Request failed!")
            
            j = json.loads(r.text)

            for result in j["items"]:
                results.append(
                    discord.OptionChoice(
                        name = result["full_name"],
                        value = result["id"]
                    )
                )
            return results

    async def _github_user_search_autocomplete(self, interaction: discord.context.AutocompleteContext):
            endpoint = agb.system.cogwheel.getAPIEndpoint("github", "USER_SEARCH")
    
            if interaction.value.strip() == "":
                return []
            
            results = []

            r = handler.get(
                formatQueryString(endpoint, {
                    "q": interaction.value
                }), headers=self.GITHUB_HEADERS, attemptCache=False
            )            
            if not await self.cushionGitHubAPIResponse(r, interaction, autoResponse=False):
                raise GitHubAPIError("GitHub API Request failed!")
            j = json.loads(r.text)

            for result in j["items"]:
                results.append(
                    discord.OptionChoice(
                        name = result["login"],
                        value = result["id"]
                    )
                )
            return results

    async def cushionGitHubAPIResponse(self,
                                       request: Response,
                                       interaction: discord.context.ApplicationContext,
                                       autoResponse: bool = True) -> bool:
        """Checks if the GitHub API response is valid and can continue.
        
        Returns an boolean, `True` if it is OK, and `False` if not.  Automatic Responses can be configured
        with the `autoResponse` argument (defaults to `True`)."""
        requestOK = True
        reason = "No Reason!"
        
        # log ratelimiting information
        self.logger.debug("GitHub ratelimit remaining for resource '%s': Used: %s (%s remaining), Resets: %s (in %s seconds).", 
                          request.headers["x-ratelimit-resource"],
                          request.headers["x-ratelimit-used"],
                          request.headers["x-ratelimit-remaining"], 
                          request.headers["x-ratelimit-reset"], 
                          round(int(request.headers["x-ratelimit-reset"]) - time.time()))

        if request.status_code not in [200, 204]:
            # uhhh... this is not ok... lemme check.
            if request.headers["x-ratelimit-remaining"] == 0:
                reason = "Ratelimited"
                requestOK = False
            
            if not requestOK and autoResponse:
                await interaction.response.send_message(":x: Can't do that right now...", ephemeral=True)
                self.logger.warning("GitHub API Request failed: %s" % reason)
            
        return requestOK

        
    @group.command(name="octocat", description="Get an octocat!")
    async def _octocat(self, interaction: discord.context.ApplicationContext):
        r = handler.get(
            agb.system.cogwheel.getAPIEndpoint("github", "OCTOCAT"), headers=self.GITHUB_HEADERS, attemptCache=False,
        )
        if not await self.cushionGitHubAPIResponse(r, interaction):
            return
        await interaction.response.send_message("```\n%s\n```" % r.text)
        

    @group.command(name="repository", description="Get GitHub repository information!")
    async def _repository(self, interaction: discord.context.ApplicationContext,
                          repository: discord.Option(int, description="Repository to use", autocomplete=_github_repo_search_autocomplete)): # type: ignore

        await interaction.response.defer()
        
        r = handler.get(
            agb.system.cogwheel.getAPIEndpoint("github", "GET_REPO_BY_ID").format(repository),
            headers=self.GITHUB_HEADERS,
            attemptCache=False
        )

        if not await self.cushionGitHubAPIResponse(r, interaction):
            return
        
        data = json.loads(r.text)
        
        # get contributor information
        r2 = handler.get( #r2d2 lol
            data["contributors_url"],
            headers=self.GITHUB_HEADERS,
            attemptCache=False
        )
        canDoContributors = True
        if not await self.cushionGitHubAPIResponse(r2, interaction, autoResponse=False):
            canDoContributors = False    

        author = discord.EmbedAuthor(
            name     = data["full_name"],
            url      = data["html_url"],
            icon_url = data["owner"]["avatar_url"]            
        )
        embed = agb.system.cogwheel.embed(
            title       = data["name"],
            description = data["description"],
            author      = author
        )

        if data["license"] is not None:
            embed.add_field(name="License", value="[%s](https://choosealicense.com/licenses/%s)" % (
                data["license"]["name"],
                data["license"]["spdx_id"].lower() # hacky solution...
            ))

        embed.add_field(name="Language", value = data["language"], inline=True)        
        embed.add_field(name="Stargazers", value=data["stargazers_count"], inline=True)        
        embed.add_field(name="Open Issues/PRs", value=data["open_issues_count"], inline=True)
        vi = discord.ui.View()

        topicstr = ", ".join(data["topics"])

        if len(data["topics"]) > 0:
            embed.add_field(name="Topics", 
                            value=topicstr)
        
        if canDoContributors:
            contributors = json.loads(r2.text)
            contributorstr = "%s: " % str(len(contributors)) + ", ".join([c["login"] for c in contributors])
            embed.add_field(name="Contributors", value=contributorstr)

        if is_valid_url(data["homepage"]):
            self.logger.debug("Yep, the URL \"%s\" from the homepage seems to be valid.  Passing it along to the button!", data["homepage"])
            vi.add_item(
                discord.ui.Button(
                    label = "Project Homepage",
                    url   = data["homepage"]
                )
            )
        else:
            self.logger.debug("Well, that sucks.  The URL \"%s\" is not valid, so I can't use the button.", data["homepage"])
        
        # Fire off that embed!!
        await interaction.followup.send(embed = embed, view = vi)

    @group.command(name="user", description="Get a GitHub user's information!")
    async def _user(self, interaction: discord.context.ApplicationContext,
                    user: discord.Option(int, description="User to search for!", autocomplete=_github_user_search_autocomplete)): # type: ignore
        await interaction.response.defer()
        endpoint = agb.system.cogwheel.getAPIEndpoint("github", "GET_USER_BY_ID")

        r = handler.get(
            endpoint.format(user),
            headers=self.GITHUB_HEADERS,
            attemptCache=False
        )
        if not await self.cushionGitHubAPIResponse(r, interaction):
            return
        data = json.loads(r.text)

        author = discord.EmbedAuthor(
            name = "%s (%s)" % (data["name"], data["login"]),
            url  = data["html_url"]
        )
        embed = agb.system.cogwheel.embed(
            description = data["bio"],
            author      = author
        )
        embed.set_thumbnail(url=data["avatar_url"])

        embed.add_field(name="Location", value=data["location"])
        embed.add_field(name="Repositories", value=data["public_repos"], inline=True)
        embed.add_field(name="Followers", value=data["followers"], inline=True)
        embed.add_field(name="Following", value=data["following"], inline=True)

        vi = discord.ui.View()

        if is_valid_url(data["blog"]):
            vi.add_item(discord.ui.Button(
                label="Blog",
                url = data["blog"]
            ))
            
        await interaction.followup.send(embed = embed, view=vi)
