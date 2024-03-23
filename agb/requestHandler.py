import requests_cache
import logging
import requests

global responses
responses = {200: 'OK', 201: 'Created', 202: 'Accepted', 203: 'Non-Authoritative Information', 204: 'No Content',
             205: 'Reset Content', 206: 'Partial Content', 400: 'Bad Request', 401: 'Unauthorized',
             402: 'Payment Required', 403: 'Forbidden', 404: 'Not Found', 405: 'Method Not Allowed',
             406: 'Not Acceptable', 407: 'Proxy Authentication Required', 408: 'Request Timeout', 409: 'Conflict',
             410: 'Gone', 411: 'Length Required', 412: 'Precondition Failed', 413: 'Request Entity Too Large',
             414: 'Request-URI Too Long', 415: 'Unsupported Media Type', 416: 'Requested Range Not Satisfiable',
             417: 'Expectation Failed', 100: 'Continue', 101: 'Switching Protocols', 300: 'Multiple Choices',
             301: 'Moved Permanently', 302: 'Found', 303: 'See Other', 304: 'Not Modified', 305: 'Use Proxy',
             306: '(Unused)', 307: 'Temporary Redirect', 500: 'Internal Server Error', 501: 'Not Implemented',
             502: 'Bad Gateway', 503: 'Service Unavailable', 504: 'Gateway Timeout', 505: 'HTTP Version Not Supported'}


class RequestHandler:
    def __init__(self):
        self.logger = logging.getLogger("cogwheel")
        self.session = requests_cache.CachedSession("request-handler", cache_control=True)
        self.logger.info("RequestHandler has been initalized!")

    def get(self, url: str, attemptCache=True):
        self.logger.debug("Web request was called with URL \"{0}\".  {1}".format(url,
                                                                                 "(CACHING WAS DISABLED)" if attemptCache == False else ""))
        headers = {"User-Agent": "AlphaGameBot/1; https://alphagame.dev; +damien@alphagame.dev"}
        if attemptCache:
            r = self.session.get(url, headers=headers)
        else:
            r = requests.get(url, headers=headers)  # some sites / APIs don't work well with caching,
            # especially /meme.  It always returns same because of the cache.
        self.logger.info("Web request finished.  StatusCode={0} ({1}), time={2}ms, from_cache:{3}".format(r.status_code,
                                                                                          responses[r.status_code],
                                                                                          round(r.elapsed.total_seconds() * 100),
                                                                                               "yes" if r.from_cache else "no"))
        return r


handler = RequestHandler()
