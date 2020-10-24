#!/usr/bin/env python3

from urllib import request
import subprocess
import os
import logging
import sys
import json
import re


class Updater():
    service = 'PI-Hole'

    def __init__(self, config=None):
        self.config = config
        self.latest_version = None
        self.current_version = None

    def get_current_version(self):
        try:
            response = subprocess.check_output("pihole -v  | grep 'Pi-hole'", shell=True)
            m = re.findall(r'v(\d+\.[\d+\.]*)', response.decode('utf-8'))
            self.current_version = m[0]
        except:
            pass
        
        return self.current_version

    def get_latest_version(self):
        url = "https://api.github.com/repos/pi-hole/pi-hole/releases/latest"
        response = request.urlopen(url).read()
        self.latest_version = json.loads(response)['tag_name'].replace('v', '')

        return self.latest_version

    def install(self):
        subprocess.check_output("curl -sSL https://install.pi-hole.net | PIHOLE_SKIP_OS_CHECK=true sudo -E bash /dev/stdin --unattended", shell=True)




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
    
    agentdvr = UpdatePihole()
    latest_version = agentdvr.get_latest_version()
    current_version = agentdvr.get_current_version()
    print(current_version, latest_version)
    #if current_version != latest_version and latest_version is not None:
    #    agentdvr.install()
    #logging.info("Done")

