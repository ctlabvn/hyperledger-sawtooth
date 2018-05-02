# Copyright 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import os
import sys
import logging
import asyncio
import argparse
from urllib.parse import urlparse
import platform
import pkg_resources
from aiohttp import web

from zmq.asyncio import ZMQEventLoop

from simple_rest_api.route_handlers import RouteHandler
from simple_rest_api.config import RestApiConfig

import uvloop

LOGGER = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line flags added to `rest_api` command.
    """
    parser = argparse.ArgumentParser(
        description='Starts the REST API application and connects to a '
        'specified validator.')

    parser.add_argument('-B', '--bind',
                        help='identify host and port for API to run on \
                        default: http://localhost:8080)',
                        action='append')
    parser.add_argument('-t', '--timeout',
                        help='set time (in seconds) to wait for validator \
                        response')
    parser.add_argument('-v', '--verbose',
                        action='count',
                        default=0,
                        help='enable more verbose output to stderr')   

    parser.add_argument(
        '-V', '--version',
        action='version',
        version='1.0',
        help='display version information')

    return parser.parse_args(args)


def start_rest_api(host, port, timeout):
    """Builds the web app, adds route handlers, and finally starts the app.
    """
    loop = asyncio.get_event_loop()    
    app = web.Application(loop=loop)        

    handler = RouteHandler(loop, timeout)

    app.router.add_get('/state/{address}', handler.fetch_state)
    app.on_shutdown.append(lambda app: print("Shutting down"))

    # Start app
    LOGGER.info('Starting REST API on %s:%s', host, port)

    web.run_app(
        app,
        host=host,
        port=port,
        access_log=LOGGER,
        access_log_format='%r: %s status, %b size, in %Tf s')


def main():
    # loop = ZMQEventLoop()
    # asyncio.set_event_loop(loop)

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    try:
        opts = parse_args(sys.argv[1:])
        print(opts)
        rest_api_config = RestApiConfig(
            bind=opts.bind,            
            timeout=opts.timeout)   

        try:
            host, port = rest_api_config.bind[0].split(":")
            port = int(port)
        except ValueError as e:
            print("Unable to parse binding {}: Must be in the format"
                  " host:port".format(rest_api_config.bind[0]))
            sys.exit(1)                 

        start_rest_api(
            host,
            port,            
            rest_api_config.timeout)
        # pylint: disable=broad-except
    except Exception as e:
        LOGGER.exception(e)
        sys.exit(1)
    finally:
        print("Stopped")
