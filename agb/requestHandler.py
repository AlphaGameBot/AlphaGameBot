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

import requests_cache
import logging
import requests
import json
import agb.cogwheel
import urllib.parse

class RequestHandler:
    def __init__(self):
        self.logger = logging.getLogger("requesthandler")
        with open("assets/http_codes.json", "r") as f:
            self.RESPONSES = json.load(f)
            self.logger.debug("Loaded %s HTTP Responses!" % len(self.RESPONSES.keys()))
        self.session = requests_cache.CachedSession("request-handler", cache_control=True, expire_after=43200) # 43200 seconds = 12 hours
        self.logger.info("RequestHandler has been initalized!")
        with open("alphagamebot.json", "r") as f:
            self.BOT_INFORMATION = json.load(f)

        self.REQUEST_HEADERS = {
            "User-Agent": self.BOT_INFORMATION["USER-AGENT"].format(
                version=self.BOT_INFORMATION["VERSION"],
                requests=requests.__version__,
                devstatus=(
                    " (DEVELOPMENT EDITION)" if agb.cogwheel.isDebugEnv else ""
                )),  # this can be changed in the config (alphagamebot.json)
            "Accept": "application/json,text/plain,application/xml",
            "x-alphagamebot-version": self.BOT_INFORMATION["VERSION"],
            "x-python-requests-version": requests.__version__,
            "Upgrade-Insecure-Requests": "1",
            "Accept-Encoding": "gzip",
            "Connection": "close" # we dont need a constant connection :)
        }
    def get(self, url: str, attemptCache=True):
        self.logger.debug("Web request was called with URL \"{0}\".  {1}".format(url,
                                                                                 "(CACHING WAS DISABLED)" if attemptCache == False else ""))
        if attemptCache:
            r = self.session.get(url, headers=self.REQUEST_HEADERS)
        else:
            r = requests.get(url, headers=self.REQUEST_HEADERS)  # some sites / APIs don't work well with caching,
            # especially /meme.  It always returns same because of the cache.
        self.logger.info("Web request finished.  StatusCode={0} ({1}), time={2}ms, from_cache:{3}".format(r.status_code,
                                                                                          self.RESPONSES[r.status_code],
                                                                                          round(r.elapsed.total_seconds() * 100),
                                                                                                          ("yes" if r.from_cache else "no") if attemptCache == True else "disabled"))
        return r

    def post(self, url:str, data:dict, description:str=None):
        self.logger.debug("POST request was called with URL \"{0}\".  {1}".format(url, (
            "description:\"%s\"" % description if description is not None else ""
        )))
        r = requests.post(url, data, headers=self.REQUEST_HEADERS)
        self.logger.info("POST request finished.  StatusCode={0} ({1}), time={2}ms".format(
            r.status_code, self.RESPONSES[r.status_code], round(r.elapsed.total_seconds() * 100)
        ))
        return r

handler = RequestHandler()

def formatQueryString(url, params):
    """
    Appends query parameters to a given URL.

    Args:
    - url (str): The base URL to which the query string will be appended.
    - params (dict): A dictionary of query string parameters.

    Returns:
    - str: The URL with the appended query string.
    """
    # Parse the URL into components
    url_parts = list(urllib.parse.urlparse(url))
    
    # Convert the query string parameters to a query string
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.parse.urlencode(query)
    
    # Reassemble the URL with the new query string
    return urllib.parse.urlunparse(url_parts)