#!/usr/bin/env python3

from bs4 import BeautifulSoup
from urllib import request
import re
import subprocess
import zipfile
import os
from aiohttp import ClientSession


class Updater():
    service = 'AgentDVR'

    def __init__(self, config=None):
        self.config = config
        self.changelog = "https://www.ispyconnect.com/producthistory.aspx?productid=27"
        self.install_dir = self.config['install_dir']
        self.install_fileversion = self.install_dir + "/version.txt"
        self.download_dir = "/var/tmp/agentdvr_{}.zip"
        self.download_url = ""
        self.latest_version = None
        self.current_version = None

    async def get_latest_version(self):
        # Download land page for web scraping
        url = "https://www.ispyconnect.com/download.aspx"
        # response = request.urlopen(url).read()
        async with ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()
        soup = BeautifulSoup(response, 'html.parser')

        for link in soup.find_all('a'):
            zip_href = str(link.get('href'))
            if 'zip' in zip_href and 'Linux' in zip_href:
                # The correct zip file has been found
                self.download_url = zip_href
                m = re.search(r'(\d+_?)+', zip_href)
                if m:
                    self.latest_version = m.group(0)[3:].replace("_", ".")
        self.download_dir = self.download_dir.format(self.latest_version)
        return self.latest_version

    async def get_current_version(self):
        #async with ClientSession() as session:
        #    async with session.get(self.config['url']) as resp:
        #        response = await resp.text()
        #soup = BeautifulSoup(response, 'html.parser')
        #scripts = soup.find_all("script")
        #for script in scripts:
        #    print(regex.findall(r"\{(?:[^{}]|(?R))*\}", script))

        if os.path.exists(self.install_fileversion):
            with open(self.install_fileversion, 'r') as version_file:
                self.current_version = version_file.read()
        return self.current_version

    def install(self):
        request.urlretrieve(self.download_url, self.download_dir)
        # Download file
        with zipfile.ZipFile(self.download_dir, 'r') as zip_ref:
            zip_ref.extractall(self.install_dir)

        # Save installed version
        with open(self.install_fileversion, 'w') as version_file:
            version_file.write(self.latest_version)

        service_file = "/etc/systemd/system/agentdvr.service"
        if not os.path.exists(service_file):
            with open(service_file, 'w') as serv:
                serv.write("[Unit]\n")
                serv.write("Description=Agent DVR Server\n\n")
                serv.write("[Service]\n")
                serv.write("ExecStart=/usr/bin/dotnet {}/Agent.dll\n".format(self.install_dir))
                serv.write("Restart=on-abort\n\n")
                serv.write("[Install]\n")
                serv.write("WantedBy=multi-user.target\n")
        subprocess.check_output("/usr/sbin/service agentdvr restart", shell=True)
