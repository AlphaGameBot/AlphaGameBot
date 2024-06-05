import agb.cogwheel
import mysql.connector
import discord
import logging
import os

async def handleOnMessage(ctx: discord.Message, CAN_USE_DATABASE, cnx: mysql.connector.connection.MySQLConnection):
    cnx.commit() # get new information
    bi = agb.cogwheel.getBotInformation()
    cogw = logging.getLogger("cogwheel")
    # check for message count consent
    
    if CAN_USE_DATABASE:
        agb.cogwheel.initalizeNewUser(cnx, ctx.author.id)
        c = cnx.cursor()
        query = "UPDATE user_stats SET messages_sent = messages_sent + 1 WHERE userid = %s"
        values = [ctx.author.id]
        c.execute(query, values)
        cnx.commit()
        c.close()
    if agb.cogwheel.getUserSetting(cnx, ctx.user.id, "message_tracking_consent") == 0 or not CAN_USE_DATABASE:
        await ctx.channel.send("not tracking messages because of consent settings owo")
        return
    #   As this is a public Discord bot, I can see multiple people getting
    #   scared of this function, possibly processing their messages.  I want
    #   to point out the order of the if statements that follow.  Nothing is
    #   processed, (except for message count) unless the discord server is in 
    #   SAY_EXCEPTIONS.
    if ctx.content.startswith("..") == False:
        return
    if ctx.content.startswith("...") == True: 
        # Sometimes, I make sarcastic comments, starting with ...
        # Example: "... blah blah blah", and the bot responds to it as
        # ". blah blah blah".  This prevents the bot from responding.
        return


    # Disable the say command for all servers except for the ones in which they are explicitly
    # enabled in alphagamebot.json, key "SAY_EXCEPTIONS"
    if ctx.guild.id not in bi["SAY_EXCEPTIONS"]:
        return
    
    # When I run 2 instances of AlphaGameBot at the same time, both will reply to my message.
    # What it does is that if it is in a debug environment, it will ignore the command.  When testing,
    # I will just remove the `DEBUG=1` environment variable.
    if agb.cogwheel.isDebugEnv:
        cogw.info("Say was ignored as I think this is a development build.")
        return EnvironmentError("Bot is in development build")
    
    if ctx.author.id != os.getenv("ALPHAGAMEBOT_OWNER_ID", 420052952686919690):
        cogw.warning("{0} tried to make me say \"{1}\", but I successfully ignored it.".format(ctx.author.name,
                                                                                               ctx.content))
        await ctx.reply("> \"You can go fuck yourself with that!\", Brewstew, *Devil Chip*")
        return

    text = ctx.content
    text = text[2:]
    if text == None:
        # No text given, so give up...
        return
    
    # Put in the console that it was told to say something!
    logging.info("I was told to say: \"%s\"." % text)
    await ctx.channel.send(text)

    # Delete the original message, so it looks better in the application!
    await ctx.delete()