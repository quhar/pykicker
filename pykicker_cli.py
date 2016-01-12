#!/usr/bin/env python3
"""Pykicer CLI allows to add or list short urls."""

import sys
import argparse
import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0


def connect_to_redis(redis_host, redis_port, redis_db):
    """Connect to Redis server."""
    rd_con = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    return rd_con


def add_short_url(rd_con, short_url_name, long_url):
    """Add short url to datastore."""
    rd_con.set(short_url_name, long_url)


def list_short_urls(rd_con):
    return [(key, rd_con.get(key)) for key in rd_con.scan_iter()]


def delete_short_link(rd_con, links):
    rd_con.delete(*links)


def usage(name):
    print("""Usage {name} <list|add> [name] [long_url]""")

def main():
    main_parser = argparse.ArgumentParser("CLI to manage data for pyKicker")
    main_parser.add_argument('--redis_host', '-r', default=REDIS_HOST,
        nargs='?', type=str, help='Host/IP of Redis server')
    main_parser.add_argument('--port', '-p', default=REDIS_PORT, nargs='?',
                             type=int, help="Redis port")
    main_parser.add_argument('--database', '-d', default=REDIS_DB,
        nargs='?', type=str, help='Redis database number')
    subparsers = main_parser.add_subparsers(help='commands', dest='command')
    create_parser = subparsers.add_parser('add', help='Add short link')
    create_parser.add_argument('short_link', type=str, help='Short link')
    create_parser.add_argument('long_link', type=str, help='Long link')
    delete_parser = subparsers.add_parser('del', help='Remove short link(s)')
    delete_parser.add_argument('short_links', type=str, nargs='+',
                               help='Short link')
    list_parser = subparsers.add_parser('list', help='List short links')
    args = main_parser.parse_args(sys.argv[1:])

    if args.command is None:
        main_parser.print_help()
        return

    rd_con = connect_to_redis(args.redis_host, args.port, args.database)

    if args.command == 'list':
        print("Short links")
        for result in list_short_urls(rd_con):
            print(result[0].decode('utf-8'), '\t\t\t', result[1].decode('utf-8'))
        return

    if args.command == 'add':
        add_short_url(rd_con, args.short_link, args.long_link)
        return

    if args.command == 'del':
        delete_short_link(rd_con, args.short_links)
        return


if __name__ == '__main__':
    main()
