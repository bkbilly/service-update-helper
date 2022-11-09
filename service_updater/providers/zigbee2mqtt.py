#!/usr/bin/env python3

from urllib import request
import subprocess
import os
import json
from aiohttp import ClientSession


class Updater():
    service = 'Zigbee2mqtt'
    image = "https://www.zigbee2mqtt.io/logo.png"

    def __init__(self, config=None):
        self.config = config
        self.changelog = "https://github.com/Koenkk/zigbee2mqtt/releases"
        self.latest_version = None
        self.current_version = None

    async def get_current_version(self):
        version_file = f"{self.config['install_dir']}/package-lock.json"
        if os.path.exists(version_file):
            with open(version_file) as ofile:
                self.current_version = json.loads(ofile.read())['version']

        return self.current_version

    async def get_latest_version(self):
        url = "https://api.github.com/repos/Koenkk/zigbee2mqtt/releases/latest"
        # response = request.urlopen(url).read()
        async with ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()
        self.latest_version = json.loads(response)['tag_name']

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
