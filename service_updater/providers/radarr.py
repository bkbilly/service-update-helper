#!/usr/bin/env python3

import subprocess
import json
from aiohttp import ClientSession


class Updater():
    service = 'Radarr'
    image = "https://brands.home-assistant.io/_/radarr/icon.png"

    def __init__(self, config=None):
        self.config = config
        self.changelog = f"{self.config['url']}/system/updates"
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
        url = "https://api.github.com/repos/Radarr/Radarr/releases"
        async with ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()
        self.latest_version = json.loads(response)[0]['tag_name'].replace('v', '')

        return self.latest_version

    def install(self):
        subprocess.check_output("docker-compose -f /opt/docker_compose/docker-compose-downloaders.yml pull", shell=True)
        subprocess.check_output("/usr/bin/systemctl restart downloaders.service", shell=True)
