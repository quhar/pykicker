"""Pyckier is simple redirect service.

It redirects user using short links like go.domain.com/nicephoto to longer
https://very.long.url.com/evenlonger?path&to=resource&which_is=hard
"""

import re
import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

REQUEST_RE = re.compile(r'^[a-zA-Z0-9\-_.]+$')
NO_CACHE = ('cache-control', 'no-cache, no-store, max-age=0, must-revalidate')

def connect_to_redis():
    """Connect to Redis server."""
    rd_con = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    return rd_con


def parse_request(path_info):
    """Parse PATH_INFO from environment and return valided short URL."""
    path_info = path_info[1:]
    if not REQUEST_RE.match(path_info):
        raise ValueError
    return path_info.lower()


def return404(start_response):
    """Return 404."""
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return []


def return_redirct(start_response, long_path):
    """Return 301 REDIRECT response with found location."""
    start_response('301 Redirect',
                   [('Location', long_path.decode('ascii')), NO_CACHE])
    return []


def return500(start_response):
    """In case of any error return 500 response code."""
    start_response('500 INTERNAL SERVER ERROR',
                   [('Content-Type', 'text/plain')])
    return []


def application(environ, start_response):
    """Main WSGI application."""
    try:
        rd_con = connect_to_redis()
        path = parse_request(environ['PATH_INFO'])
        long_url = rd_con.get(path)
        if not long_url:
            return return404(start_response)
        return return_redirct(start_response, long_url)
    except Exception:
        return return500(start_response)

