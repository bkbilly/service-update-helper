#!/usr/bin/env python3

from urllib import request
import subprocess
import os
import logging
import sys
import json
import re


class Updater():
    service = 'Homeassistant'

    def __init__(self, config=None):
        self.config = config
        self.latest_version = None
        self.current_version = None

    def get_current_version(self):
        try:
            version_pip = subprocess.check_output("pip freeze | grep homeassistant", shell=True).decode("utf-8")
            m = re.search(r'.*==([\d*\.*]*)', version_pip)
            self.current_version = m.group(1)
        except:
            pass
        
        return self.current_version

    def get_latest_version(self):
        url = "https://pypi.org/pypi/homeassistant/json"
        response = request.urlopen(url)
        self.latest_version = json.loads(response.read())['info']['version']

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
    
    updater = UpdateHomeassistant()
    latest_version = updater.get_latest_version()
    current_version = updater.get_current_version()
    print(latest_version, current_version)
    #if current_version != latest_version and latest_version is not None:
    #    updater.install()
    #logging.info("Done")

