#!/usr/bin/env python3

from urllib import request
import re
import subprocess
import json
from aiohttp import ClientSession


class Updater():
    service = 'Plex'

    def __init__(self, config=None):
        self.config = config
        self.changelog = 'https://forums.plex.tv/t/plex-media-server/30447'
        self.download_dir = "/var/tmp/plex_{}.zip"
        self.download_url = ""

        self.latest_version = None
        self.current_version = None

    async def get_current_version(self):
        try:
            currentVersion = subprocess.check_output("dpkg -l | grep -i plexmediaserver", shell=True)
            currentVersion = re.search(r'(\d+\.)+\d+', str(currentVersion)).group()
            self.current_version = currentVersion
        except:
            pass

        return self.current_version

    async def get_latest_version(self):
        url = "https://plex.tv/api/downloads/1.json"
        async with ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()
        try:
            releases = json.loads(response)['computer']['Linux']['releases']
            for release in releases:
                if release['distro'] == 'debian' and release['build'] == 'linux-x86_64':
                    self.latest_version = re.search(r'(\d+\.)+\d+', release['url']).group()
                    self.download_dir = "/var/tmp/plex_" + self.latest_version + ".deb"
                    self.download_url = release['url']
        except Exception as e:
            print(e)

        return self.latest_version

    def install(self):
        request.urlretrieve(self.download_url, self.download_dir)
        if self.current_version is not None:
            subprocess.check_output("/usr/sbin/service plexmediaserver stop", shell=True)
        subprocess.check_output("sudo dpkg -i %s" % (self.download_dir), shell=True)
        subprocess.check_output("rm %s" % (self.download_dir), shell=True)
        subprocess.check_output("/usr/sbin/service plexmediaserver start", shell=True)
