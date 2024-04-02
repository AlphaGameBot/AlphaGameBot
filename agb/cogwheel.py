import discord
from discord.embeds import *
import os
import json

def getVersion() -> str:
    return json.load(open("alphagamebot.json", "r"))["VERSION"]

def getBotInformation() -> dict:
    return json.load(open("alphagamebot.json", "r"))

def getAPIEndpoint(apiName, process):
    _d = getBotInformation()
    _a = _d["API_ENDPOINTS"][apiName]
    _p = _a[process]
    return _p

def embed(**kwargs) -> discord.Embed:
    """Easy way to set default embed characteristics.  Rather than using discord.Embed, you use cogwheel.embed which
    returns the discord.Embed, with default settings.  These can be overwritten after initalization.
    :rtype: object
    :returns discord.Embed"""

    __IS_DEBUG = (os.getenv("DEBUG_ENV") is not None)

    _embed = discord.Embed(**kwargs)
    _embed.set_footer(text="AlphaGameBot version {0}{1} by AlphaGameDeveloper; alphagame.dev".format(
        getVersion(),
        " (development build)" if __IS_DEBUG else ""
    ),
                      icon_url="https://static.alphagame.dev/alphagamebot/img/icon.png")
    return _embed
