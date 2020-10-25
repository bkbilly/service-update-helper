#!/usr/bin/env python3

import subprocess
import json
import re
from aiohttp import ClientSession


class Updater():
    service = 'Sonarr'

    def __init__(self, config=None):
        self.config = config
        self.latest_version = None
        self.current_version = None

    async def get_current_version(self):
        url = f"{self.config['url']}/api/v3/system/status?apikey={self.config['api']}"
        async with ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()
        self.current_version = json.loads(response)['version']

        return self.current_version

    async def get_latest_version(self):
        url = "https://download.sonarr.tv/v3/phantom-develop/"
        async with ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()
        m = re.findall(r'>(\d+\.[\d+\.]*)', response)
        self.latest_version = m[-1]

        return self.latest_version

    def install(self):
        subprocess.check_output("docker-compose -f /opt/docker_compose/docker-compose-downloaders.yml pull", shell=True)
        subprocess.check_output("/usr/bin/systemctl restart downloaders.service", shell=True)
