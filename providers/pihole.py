#!/usr/bin/env python3

import subprocess
import json
import re
from aiohttp import ClientSession


class Updater():
    service = 'PI-Hole'

    def __init__(self, config=None):
        self.config = config
        self.latest_version = None
        self.current_version = None

    async def get_current_version(self):
        try:
            response = subprocess.check_output("pihole -v  | grep 'Pi-hole'", shell=True)
            m = re.findall(r'v(\d+\.[\d+\.]*)', response.decode('utf-8'))
            self.current_version = m[0]
        except:
            pass

        return self.current_version

    async def get_latest_version(self):
        url = "https://api.github.com/repos/pi-hole/pi-hole/releases/latest"
        async with ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()
        self.latest_version = json.loads(response)['tag_name'].replace('v', '')

        return self.latest_version

    def install(self):
        subprocess.check_output("curl -sSL https://install.pi-hole.net | PIHOLE_SKIP_OS_CHECK=true sudo -E bash /dev/stdin --unattended", shell=True)
