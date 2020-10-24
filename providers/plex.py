#!/usr/bin/env python3

from urllib import request
import re
import subprocess
import os
import logging
import sys
import json


class Updater():
    service = 'Plex'

    def __init__(self, config=None):
        self.config = config
        self.download_dir = "/var/tmp/plex_{}.zip"
        self.download_url = ""

        self.latest_version = None
        self.current_version = None

    def get_current_version(self):
        try:
            currentVersion = subprocess.check_output("dpkg -l | grep -i plexmediaserver", shell=True)
            currentVersion = re.search(r'(\d+\.)+\d+', str(currentVersion)).group()
            self.current_version = currentVersion
        except Exception as e:
            pass

        return self.current_version

    def get_latest_version(self):
        url = "https://plex.tv/api/downloads/1.json"
        response = request.urlopen(url)
        try:
            releases = json.loads(response.read())['computer']['Linux']['releases']
            for release in releases:
                if release['distro'] == 'debian' and release['build'] == 'linux-x86_64':
                    self.latest_version = re.search(r'(\d+\.)+\d+', release['url']).group()
                    self.download_dir = "/var/tmp/plex_" + self.latest_version + ".deb"
                    self.download_url = release['url']
        except Exception as e:
            logging.critical(e)

        return self.latest_version

    def download(self):
        request.urlretrieve(self.download_url, self.download_dir)

    def install(self):
        if self.current_version is not None:
            subprocess.check_output("/usr/sbin/service plexmediaserver stop", shell=True)
        subprocess.check_output("sudo dpkg -i %s" % (self.download_dir), shell=True)
        subprocess.check_output("rm %s" % (self.download_dir), shell=True)
        subprocess.check_output("/usr/sbin/service plexmediaserver start", shell=True)



if __name__ == "__main__":
    username = str(subprocess.check_output("whoami").decode('utf-8').strip())
    if username != "root":
        logging.critical("You have to be root to run this app, current user is: {}".format(username))
        sys.exit()
    
    
    logging.basicConfig(
        filename='/var/log/updater.log',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    agentdvr = UpdatePlex()
    latest_version = agentdvr.get_latest_version()
    current_version = agentdvr.get_current_version()
    if current_version != latest_version and latest_version is not None:
        agentdvr.download()
        agentdvr.install()
    logging.info("Done")

