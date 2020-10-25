#!/usr/bin/env python3

import subprocess
import os
import json
import re
from aiohttp import ClientSession


class Updater():
    service = 'Homeassistant'

    def __init__(self, config=None):
        self.config = config
        self.latest_version = None
        self.current_version = None

    async def get_current_version(self):
        try:
            version_pip = subprocess.check_output("pip freeze | grep homeassistant", shell=True).decode("utf-8")
            m = re.search(r'.*==([\d*\.*]*)', version_pip)
            self.current_version = m.group(1)
        except:
            pass

        return self.current_version

    async def get_latest_version(self):
        url = "https://pypi.org/pypi/homeassistant/json"
        async with ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()
        self.latest_version = json.loads(response)['info']['version']

        return self.latest_version

    def install(self):
        if self.current_version is None:
            subprocess.check_output("pip install --upgrade homeassistant", shell=True)

            service_file = "/etc/systemd/system/homeassistant.service"
            if not os.path.exists(service_file):
                with open(service_file, 'w') as serv:
                    serv.write("[Unit]\n")
                    serv.write("Description=Home Assistant\n")
                    serv.write("After=network.target postgresql.service\n\n")
                    serv.write("[Service]\n")
                    serv.write(f"ExecStart=/usr/local/bin/hass -c '{self.config['config_path']}'\n")
                    serv.write("Type=simple\n")
                    serv.write("User=root\n\n")
                    serv.write("[Install]\n")
                    serv.write("WantedBy=multi-user.target\n")
            subprocess.check_output("/usr/bin/systemctl restart homeassistant.service", shell=True)
        elif self.current_version != self.latest_version:
            subprocess.check_output("pip install --upgrade homeassistant", shell=True)
            subprocess.check_output("/usr/bin/systemctl restart homeassistant.service", shell=True)
        else:
            pass
