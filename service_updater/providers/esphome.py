#!/usr/bin/env python3

import subprocess
import os
import json
import re
from aiohttp import ClientSession
from importlib.metadata import version 


class Updater():
    service = 'esphome'
    image = "https://brands.home-assistant.io/_/esphome/icon.png"

    def __init__(self, config=None):
        self.config = config
        self.changelog = "https://esphome.io/changelog/index.html"
        self.latest_version = None
        self.current_version = None

    async def get_current_version(self):
        try:
            self.current_version = version('esphome')
        except:
            pass

        return self.current_version

    async def get_latest_version(self):
        url = "https://pypi.org/pypi/esphome/json"
        async with ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()
        self.latest_version = json.loads(response)['info']['version']

        return self.latest_version

    def install(self):
        if self.current_version is None:
            subprocess.check_output("pip install --upgrade esphome", shell=True)

            service_file = "/etc/systemd/system/esphomeDashboard.service"
            if not os.path.exists(service_file):
                with open(service_file, 'w') as serv:
                    serv.write("[Unit]\n")
                    serv.write("Description=ESPHome Dashboard\n")
                    serv.write("After=network-online.target\n\n")
                    serv.write("[Service]\n")
                    serv.write(f"ExecStart=/usr/local/bin/esphome /etc/esphome dashboard --username {self.config['user']} --password {self.config['password']}'\n")
                    serv.write("Type=simple\n")
                    serv.write("Restart=on-failure\n")
                    serv.write("RestartSec=5s\n")
                    serv.write("User=root\n\n")
                    serv.write("[Install]\n")
                    serv.write("WantedBy=multi-user.target\n")
            subprocess.check_output("/usr/bin/systemctl restart esphomeDashboard.service", shell=True)
        elif self.current_version != self.latest_version:
            subprocess.check_output("pip install --upgrade esphome", shell=True)
            subprocess.check_output("/usr/bin/systemctl restart esphomeDashboard.service", shell=True)
        else:
            pass

