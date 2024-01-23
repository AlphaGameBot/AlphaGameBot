import discord
from discord.embeds import *
import webui.sqlConnector
import webui.configuration

def embed(**kwargs):
    """Easy way to set default embed characteristics.  Rather than using discord.Embed, you use cogwheel.embed which
    returns the discord.Embed, with default settings.  These can be overwritten after initalization.
    :returns discord.Embed"""
    _embed = discord.Embed(**kwargs)
    _embed.set_footer(text="AlphaGameBot v1 by AlphaGameDeveloper; alphagame.dev", icon_url="https://static.alphagame.dev/alphagamebot/img/icon.png")
    return _embed

def decoratedFunction(f):
    pass
autoconfig = webui.configuration.getEnvironmentalConfigurationForMySQLServer()

connection = webui.sqlConnector.SQLConnector(**autoconfig)
cursor = connection.cursor

@decoratedFunction
def isCommandDisabled(command, interaction: discord.Interaction):
    query = "SELECT alphagamebot.commands.disabled FROM guilds WHERE guild=%s"
    cursor.execute(query, [interaction.message.guild.id])
    if cursor.fetchall()[0][0] == 1:
        return True
    else:
        return False