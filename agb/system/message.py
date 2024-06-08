import agb.cogwheel
import mysql.connector
import discord
import logging
import os

async def handleOnMessage(ctx: discord.Message, CAN_USE_DATABASE, cnx: mysql.connector.connection.MySQLConnection):
    cnx.commit() # get new information
    bot_information = agb.cogwheel.getBotInformation()
    logger = logging.getLogger("system")
    # check for message count consent
    if CAN_USE_DATABASE:
        if agb.cogwheel.getUserSetting(cnx, ctx.author.id, "message_tracking_consent") == 0:
            logger.debug("Not tracking message {} because user {} has not consented to message tracking.".format(ctx.id, ctx.author.id))
            return
        else:
            agb.cogwheel.initalizeNewUser(cnx, ctx.author.id)
            cursor = cnx.cursor()
            query = "UPDATE user_stats SET messages_sent = messages_sent + 1 WHERE userid = %s"
            values = [ctx.author.id]
            cursor.execute(query, values)
            cnx.commit()
            cursor.close()
        
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
    if ctx.guild.id not in bot_information["SAY_EXCEPTIONS"]:
        return
    
    # When I run 2 instances of AlphaGameBot at the same time, both will reply to my message.
    # What it does is that if it is in a debug environment, it will ignore the command.  When testing,
    # I will just remove the `DEBUG=1` environment variable.
    if agb.cogwheel.isDebugEnv:
        logger.info("Say was ignored as I think this is a development build.")
        return EnvironmentError("Bot is in development build")
    
    if ctx.author.id != os.getenv("ALPHAGAMEBOT_OWNER_ID", 420052952686919690):
        logger.warning("{0} tried to make me say \"{1}\", but I successfully ignored it.".format(ctx.author.name,
                                                                                               ctx.content))
        await ctx.reply("> \"You can go fuck yourself with that!\", Brewstew, *Devil Chip*")
        return

    text = ctx.content
    text = text[2:]
    if text == None:
        # No text given, so give up...
        return
    
    # Put in the console that it was told to say something!
    logger.info("I was told to say: \"%s\"." % text)
    await ctx.channel.send(text)

    # Delete the original message, so it looks better in the application!
    await ctx.delete()