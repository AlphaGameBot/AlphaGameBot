import os
from flask import (
    Flask,
    render_template,
    redirect,
    request,
    send_from_directory,
    Response)
import logging
import sys
from . import sqlConnector, configuration
import hashlib
import json
import random
import pathlib

global cachedSessions
cachedSessions = {}
logger = logging.getLogger("webui")
def generate_uuid():
    # Version 4 UUID has the format xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
    uuid = '{:08x}-{:04x}-4{:03x}-{:01x}{:03x}-{:012x}'.format(
        random.getrandbits(32),
        random.getrandbits(16),
        random.getrandbits(12),
        random.getrandbits(4),
        random.getrandbits(12),
        random.getrandbits(48)
    )
    if uuid in cachedSessions.keys():
        # if it already exists, keep making them
        # recursively.
        return generate_uuid()
    return uuid

logging.basicConfig(level=logging.DEBUG)
app = Flask("alphagamebot-web-ui")
config = configuration.getEnvironmentalConfigurationForMySQLServer()
mysql = sqlConnector.SQLConnector(**config)
cursor = mysql.cursor
def messagebox(_type: str, message: str, links=None):
    return render_template("messageBox.html",
                    type=_type,
                    message=message,
                    links=links)

@app.route("/internal")
def _int():
    return cachedSessions
def getAuthToken():
    try:
        return request.cookies.to_dict()["authenticationToken"]
    except KeyError:
        return None
    
def isAuthenticated(uuid:str=None):
    logger.debug("Attempting to authenticate using cookies.")
    try:
        try:
            if not uuid:
                logger.debug("using request info for cookies")
                uuid = request.cookies.to_dict()["authenticationToken"]
        except KeyError:
            logger.debug("Cannot get cookie as it does not exist.")
            return False
        logger.debug(uuid)
        if uuid in cachedSessions.keys():
            if cachedSessions[uuid]["result"] == "SUCCESS":
                logger.debug("Automatic cookie authentication was SUCCESSFUL.")
                return True
    except ValueError:
        return False

def cannotAuthenticateError():
    return messagebox("ERROR", "I cannot automatically authenticate you using cookies.  This may be a bug or the server restarted.  Anyway, I need you to reauthenticate, OK?  :)  Code:isAuth/KeyError", 
                      links=[{"href": "/app", "text": "Authenticate"}])
@app.errorhandler(404)
def _e404(e):
    return messagebox("ERROR", e)

@app.errorhandler(500)
def _e500(e):
    return messagebox("ERROR", e, links=[{"href": "/","text": "Return to root"}])

@app.route("/")
def _index():
    return redirect("/app/login")

@app.route("/post", methods=["POST"])
def _post():
    return request.form.to_dict()



def _cookies():
    return request.cookies.to_dict()

@app.route("/app/auth/session/authenticate/<string:uuid>", methods=["POST"])
def _authenticateSession(uuid:str):
    r = request.form.to_dict()
    context = cachedSessions[uuid]
    if context["type"] != "RequestingAuthentication":
        return Response({"type": "error", "message": "Cannot understand context with UUID {0} due to invalid request type.  The given was {1}.  I cannot use this information.".format(
            uuid, context["type"]
        ), "expected": "RequestingAuthentication"}, status=500)
    guild = context["intention"]["guild"]
    query = "SELECT password FROM guilds WHERE guild = %s"
    cursor.execute(query, [guild]) # has to be a tuple i guess
    serverhash = cursor.fetchall()[0][0]
    hasher = hashlib.sha256()
    hasher.update(bytes(r["password"], 'utf-8'))
    hashed = hasher.hexdigest()
    logger.debug(hashed)
    logger.debug(serverhash)
    isAllowed = (hashed == serverhash)
    if isAllowed:
        context["result"] = "SUCCESS"
        context["satisfied"] = True
        res = redirect(context["destination"])
        res.set_cookie("authenticationToken", uuid)
        return res
    elif serverhash == None:
        context["result"] = "INVALID"
        context["satisfied"] = True
        return messagebox("ERROR", "A big error occured on the backend.  Please alert Damien at damien@alphagame.dev of this error immediately.  Include the code \"ERR01/BOOMERANG\".  Sorry about this \(._.)/")
    else:
        context["result"] = "FAILED"
        context["satisfied"] = True
        return messagebox("ERROR", "Cannot authenticate with password for reason: PASSWORD DENIED", links=[{"href": context["current"], "text": "Try again"}])

@app.route("/app/")
def _app_index():
    if isAuthenticated():
        return redirect(cachedSessions[getAuthToken()]["destination"])
    else:
        return redirect("/app/login")
@app.route("/app/login")
def _app_login():
    args = request.args
    if isAuthenticated():
        return redirect(cachedSessions[getAuthToken()]["destination"])
    if args.get("guild") == None:
        return render_template("inputField.html", title="Enter Discord server ID",
                                message="If you don't know, run /webui info",
                                name="Guild ID",
                                action="/app/login",
                                fieldid="guild")
    guild = args.get("guild")
    try:
        int(guild)
    except ValueError:
        return Response(messagebox("ERROR", "The guild ID \"{}\" cannot be parsed as a guild ID.  It is supposed to be numeric, but it cannot be parsed as int().".format(guild),
                                   links=[{"href": "/app/login?source=guildInvalidParsedInt",
                                           "text": "Go back"}]),
                        status=500)
    
    # see if the guild exists by checking if the server id is in the database.
    # If the result is nonzero, it exists, and if it is zero, it doesn't.
    # https://stackoverflow.com/questions/1676551/best-way-to-test-if-a-row-exists-in-a-mysql-table
    findGuildQuery = "SELECT COUNT(*) AS total FROM guilds WHERE guild = %s"
    findSetupQuery = "SELECT setup, needpasswordreset FROM guilds WHERE guild = %s"
    cursor.execute(findGuildQuery, [guild])
    result = cursor.fetchall()
    botcanseeguild = False
    if result[0][0] > 0:
        botcanseeguild = True
    if botcanseeguild == False:
        return Response(messagebox("ERROR", "Guild {} does not exist! (It is also possible that the bot cannot see it because it is not in that guild.)".format(guild)),
                        status=422)
    cursor.execute(findSetupQuery, [guild])
    result = cursor.fetchall()
    
    if result[0][0] == 0:
        return Response(messagebox("ERROR",
                                   "Guild {} was successfully found, but it is not yet set up for the web interface.  Do \"/webui setup\" on the bot to get started.".format(guild)),
                                   status=500)
                    
    if result[0][1] == 1: # password reset needed
        return render_template("password.html", action="/app/{}/dashboard".format(guild), message="Log in with the password that AlphaGameBot gave you.")
    
    # make authentication cachedSession
    uuid = generate_uuid()
    cachedSessions[uuid] = {
        "type": "RequestingAuthentication",
        "intention": {
            "guild": guild
        },
        "result": None,
        "satisfied": False,
        "current": "/app?guild={}".format(guild),
        "destination": "/app/{}/dashboard".format(guild)
    }
    return render_template("password.html", uuid=uuid, message="Log in with your AlphaGameBot WebUI password.")
settings = json.load(open("settings.json", "r"))

@app.route("/app/<int:guild>/dashboard/", methods=["GET", "POST"])
def dashboard(guild):

    authenticated = False
    if isAuthenticated():
        return render_template("settings.html", settings=settings, guild=guild)
    else:
        return cannotAuthenticateError()
    

@app.route("/app/<int:guild>/dashboard/apply", methods=["POST", "GET"])
def apply(guild):
    try:
        args = request.args
        
        if args.get("session") == None:
            uuid = generate_uuid()
            cachedSessions[uuid] = {
                "guild": guild,
                "authenticated": False,
                "form": request.form.to_dict()
            }
            return redirect("/app/{0}/dashboard/apply/authenticate?session={1}".format(guild, uuid))
        else:
            # apply settings or something
            session = args.get("session")
            if cachedSessions[session]["authenticated"] == True:
                return messagebox("INFO", "Settings have been successfully saved, and applied.  Please allow up to a minute for the changes to take effect. :)",
                                links=[{"href": "/", "text": "Return"}])
            else:
                return messagebox("ERROR", "Cannot authenticate in order to change settings. :/")
    except:
        return cannotAuthenticateError()
@app.route("/app/<int:guild>/dashboard/apply/authenticate")
def applyAuthentication(guild):
    args = request.args
    if args.get("session") == None:
        return messagebox("ERROR", "400 Bad Request: No SessionID has been given.  Please try again.")
    if isAuthenticated():
        cachedSessions[args.get("session")]["authenticated"] = True
        return redirect("/app/{0}/dashboard/apply?session={1}".format(guild, args.get("session")))
    return render_template("password.html", action="/app/{}/dashboard/apply".format(guild), message="Please authenticate in order to save the settings.")

@app.route('/static/<path:path>')
def send_report(path):
    # we have to use send_from_directory to prevent directory
    # transversal attacks!  /static takes a user supplied path
    # which leads to the possibility of /static/../privatefile.txt
    return send_from_directory(app.static_folder, path)

@staticmethod
def start():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    app.template_folder = os.path.join(dir_path, "templates")
    app.static_folder = os.path.join(dir_path, "static")
    logger.debug(app.template_folder)
    logger.debug(app.static_folder)
    app.run("0.0.0.0", 5000)