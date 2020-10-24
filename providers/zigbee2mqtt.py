#!/usr/bin/env python3

from urllib import request
import subprocess
import os
import logging
import sys
import json


class Updater():
    service = 'Zigbee2mqtt'

    def __init__(self, config=None):
        self.config = config
        self.latest_version = None
        self.current_version = None

    def get_current_version(self):
        version_file = f"{self.config['install_dir']}/npm-shrinkwrap.json"
        with open(version_file) as ofile:
            self.current_version = json.loads(ofile.read())['version']
        
        return self.current_version

    def get_latest_version(self):
        url = "https://api.github.com/repos/Koenkk/zigbee2mqtt/releases/latest"
        response = request.urlopen(url)
        self.latest_version = json.loads(response.read())['tag_name']

        return self.latest_version

    def install(self):
        if self.current_version is None:
            subprocess.check_output("curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -", shell=True)
            subprocess.check_output("apt-get install -y nodejs git make g++ gcc", shell=True)
            subprocess.check_output(f"git clone https://github.com/Koenkk/zigbee2mqtt.git {self.config['install_dir']}", shell=True)
            subprocess.check_output("npm ci", shell=True, cwd=self.config['install_dir'])

            service_file = "/etc/systemd/system/zigbee2mqtt.service"
            if not os.path.exists(service_file):
                with open(service_file, 'w') as serv:
                    serv.write("[Unit]\n")
                    serv.write("Description=zigbee2mqtt\n")
                    serv.write("After=network.target\n\n")
                    serv.write("[Service]\n")
                    serv.write("ExecStart=/usr/bin/npm start\n")
                    serv.write(f"WorkingDirectory={self.config['install_dir']}\n")
                    serv.write("StandardOutput=inherit\n")
                    serv.write("StandardError=inherit\n")
                    serv.write("Restart=always\n")
                    serv.write("User=root\n\n")
                    serv.write("[Install]\n")
                    serv.write("WantedBy=multi-user.target\n")
            subprocess.check_output("/usr/bin/systemctl enable zigbee2mqtt.service", shell=True)
            subprocess.check_output("/usr/bin/systemctl start zigbee2mqtt.service", shell=True)
        else:
            subprocess.check_output("/usr/bin/systemctl stop zigbee2mqtt.service", shell=True)
            subprocess.check_output("cp -R data data-backup", shell=True, cwd=self.config['install_dir'])
            subprocess.check_output("git checkout HEAD -- npm-shrinkwrap.json", shell=True, cwd=self.config['install_dir'])
            subprocess.check_output("git pull", shell=True, cwd=self.config['install_dir'])
            subprocess.check_output("npm ci", shell=True, cwd=self.config['install_dir'])
            subprocess.check_output("cp -R data-backup/* data", shell=True, cwd=self.config['install_dir'])
            subprocess.check_output("rm -rf data-backup", shell=True, cwd=self.config['install_dir'])
            subprocess.check_output("/usr/bin/systemctl start zigbee2mqtt.service", shell=True)




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
    
    agentdvr = UpdateZigbee2mqtt()
    latest_version = agentdvr.get_latest_version()
    current_version = agentdvr.get_current_version()
    if current_version != latest_version and latest_version is not None:
        agentdvr.install()
    logging.info("Done")

