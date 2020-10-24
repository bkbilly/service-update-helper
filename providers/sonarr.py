#!/usr/bin/env python3

from urllib import request
import subprocess
import os
import logging
import sys
import json
import re


class Updater():
    service = 'Sonarr'

    def __init__(self, config=None):
        self.config = config
        self.latest_version = None
        self.current_version = None

    def get_current_version(self):
        url = f"{self.config['url']}/api/v3/system/status?apikey={self.config['api']}"
        response = request.urlopen(url).read()
        self.current_version = json.loads(response)['version']
        
        return self.current_version

    def get_latest_version(self):
        url = "https://download.sonarr.tv/v3/phantom-develop/"
        response = request.urlopen(url).read().decode('utf-8')
        m = re.findall(r'>(\d+\.[\d+\.]*)', response)
        self.latest_version = m[-1]

        return self.latest_version

    def install(self):
        subprocess.check_output("docker-compose -f /opt/docker_compose/docker-compose-downloaders.yml pull", shell=True)
        subprocess.check_output("/usr/bin/systemctl restart downloaders.service", shell=True)




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
    
    agentdvr = UpdateRadarr()
    latest_version = agentdvr.get_latest_version()
    current_version = agentdvr.get_current_version()
    print(current_version, latest_version)
    #if current_version != latest_version and latest_version is not None:
    #    agentdvr.install()
    logging.info("Done")

