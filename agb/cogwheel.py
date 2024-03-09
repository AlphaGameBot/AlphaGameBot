import discord
from discord.embeds import *

def embed(**kwargs):
    """Easy way to set default embed characteristics.  Rather than using discord.Embed, you use cogwheel.embed which
    returns the discord.Embed, with default settings.  These can be overwritten after initalization.
    :returns discord.Embed"""
    _embed = discord.Embed(**kwargs)
    _embed.set_footer(text="AlphaGameBot v1 by AlphaGameDeveloper; alphagame.dev", icon_url="https://static.alphagame.dev/alphagamebot/img/icon.png")
    return _embed

