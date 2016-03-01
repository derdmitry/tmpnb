# -*- coding: utf-8 -*-

import datetime
import json
import os
import re
import uuid

from concurrent.futures import ThreadPoolExecutor

import tornado
import tornado.options
from tornado.log import app_log
from tornado.web import RequestHandler, HTTPError, RedirectHandler

from tornado import gen, web

import dockworker
from spawnpool import SpawnPool

STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        spawner = dockworker.DockerSpawner(docker_host='https://192.168.99.100:2376')
        command_default = (
            'jupyter notebook --no-browser'
            ' --port {port} --ip=0.0.0.0'
            ' --NotebookApp.base_url=/{base_path}'
            ' --NotebookApp.port_retries=0'
        )
        username = self.get_argument("username")
        if username:
            container_config = dockworker.ContainerConfig(
                    image='morpheuz/jupyther-notebook-minimal-nfs',
                    command=command_default,
                    mem_limit='512m',
                    cpu_shares=None,
                    container_ip='127.0.0.1',
                    container_port='8888',
                    container_user=username,
                    host_network=False,
                    host_directories=None
            )
            spawnpool = SpawnPool(proxy_endpoint='http://127.0.0.1:8001',
                                  proxy_token='',
                                  spawner=spawner,
                                  container_config=container_config,
                                  capacity=1,
                                  max_age=None,
                                  static_files=None,
                                  static_dump_path=STATIC_PATH,
                                  pool_name='JUPHUB',
                                  user_length=32
                                  )


            self.write("Start container with %s" % username)
            container = spawnpool._launch_container(user=username)
        else:
            self.write("Need username")


def main():
    app = tornado.web.Application([
        (r"/", MainHandler),
    ])
    app.listen(9999)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
