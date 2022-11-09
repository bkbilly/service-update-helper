# Service Update Helper

This is a collection of scripts that help update and install services on linux machines which are autodiscovered by Home Assistant. It can be easily expanded for other platforms and supports configuration for each of them. 

Currently supported:
  - AgentDVR
  - Zigbee2mqtt
  - Plex
  - Homeassistant
  - PiHole
  - Bazarr
  - Radarr
  - Sonarr

## Setup
The configuration is done by the `config.yaml` file which contains the provider name as the file name on the providers folder. Some services need configuration so it can be written there. If the service is not in this config, then it will be ignored.

This is an example:
```yaml
mqtt:
  identifier: service_updater
  server: 192.168.1.1
  port: 1883
  auth:
    user: user
    pass: pass
providers:
  plex:
  pihole:
  zigbee2mqtt:
    install_dir: "/opt/zigbee2mqtt"
  homeassistant:
    config_path: "/etc/homeassistant"
  agentdvr:
    install_dir: "/opt/agentdvr"
  bazarr:
    url: "http://localhost:6767"
    api: <key>
  sonarr:
    url: "http://localhost:8989"
    api: <key>
  radarr:
    url: "http://localhost:7878"
    api: <key>
```

Some prerequirements are required which can be installed using the pip command:
```shell
sudo pip3 install -e .
```

## Run
Once the setup is done, run the script as super user `sudo service_updater`.


## Development
The contribution to this repository is really easy. Create a new file on the providers folder with the name of the service and follow this template:

```python

class Updater():
    service = 'NewService'
    image = "https://example.com/icon.png"

    def __init__(self, config=None):
        self.config = config
        self.latest_version = None
        self.current_version = None

    async def get_current_version(self):
        return self.current_version

    async def get_latest_version(self):
        return self.latest_version

    def install(self):
        pass
```

Most services are based on web scrapping, so it is very likely that they will stop working, so please create an issue. Any help is more than welcome.
