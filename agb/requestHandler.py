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
import os

global responses


class RequestHandler:
    def __init__(self):
        self.RESPONSES = {200: 'OK', 201: 'Created', 202: 'Accepted', 203: 'Non-Authoritative Information',
             204: 'No Content', 205: 'Reset Content', 206: 'Partial Content', 400: 'Bad Request', 401: 'Unauthorized',
             402: 'Payment Required', 403: 'Forbidden', 404: 'Not Found', 405: 'Method Not Allowed',
             406: 'Not Acceptable', 407: 'Proxy Authentication Required', 408: 'Request Timeout', 409: 'Conflict',
             410: 'Gone', 411: 'Length Required', 412: 'Precondition Failed', 413: 'Request Entity Too Large',
             414: 'Request-URI Too Long', 415: 'Unsupported Media Type', 416: 'Requested Range Not Satisfiable',
             417: 'Expectation Failed', 100: 'Continue', 101: 'Switching Protocols', 300: 'Multiple Choices',
             301: 'Moved Permanently', 302: 'Found', 303: 'See Other', 304: 'Not Modified', 305: 'Use Proxy',
             306: '(Unused)', 307: 'Temporary Redirect', 500: 'Internal Server Error', 501: 'Not Implemented',
             502: 'Bad Gateway', 503: 'Service Unavailable', 504: 'Gateway Timeout', 505: 'HTTP Version Not Supported'}

        self.logger = logging.getLogger("requesthandler")
        self.session = requests_cache.CachedSession("request-handler", cache_control=True)
        self.logger.info("RequestHandler has been initalized!")
        with open("alphagamebot.json", "r") as f:
            self.BOT_INFORMATION = json.load(f)

        self.REQUEST_HEADERS = {
            "User-Agent": self.BOT_INFORMATION["USER-AGENT"].format(self.BOT_INFORMATION["VERSION"]),  # this can be changed in the config (alphagamebot.json)
            "Accept": "text/plain,application/json,application/xml",
            "x-alphagamebot-version": self.BOT_INFORMATION["VERSION"],
            "Upgrade-Insecure-Requests": "1",
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

handler = RequestHandler()
