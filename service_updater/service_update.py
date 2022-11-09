#!/usr/bin/env python3

from . import providers
import json
import threading
import asyncio
import importlib.metadata

version = importlib.metadata.version(__package__ or __name__)


class ServiceUpdate:
    """docstring for ServiceUpdate"""

    def __init__(self, config, mqttclient, version):
        self.version = version
        self.mqttclient = mqttclient
        self.config = config
        self.alive = True

    def start(self):
        self.monitor_run_thread(setup=True)

    def stop(self):
        self.alive = False
        self.monitor.cancel()

    def monitor_run_thread(self, setup=False):
        asyncio.run(self.monitor_run(setup))

        if self.alive:
            self.monitor = threading.Timer(
                self.config['update_interval'],
                self.monitor_run_thread)
            self.monitor.start()

    async def monitor_run(self, setup=False):
        tasks = []
        for provider_name, module in providers.modules.items():
            if provider_name in self.config['providers']:
                provider = module(self.config['providers'][provider_name])
                tasks.append(self.gather_versions(provider))
        for provider in await asyncio.gather(*tasks):
            if setup:
                print("1st time running")
                self.setup_discovery(provider)
            print(provider.current_version, provider.latest_version)
            self.send_info(provider)

    async def gather_versions(self, provider):
        print("checking provider:", provider.service)
        try:
            await provider.get_current_version()
        except Exception as e:
            raise e
        try:
            await provider.get_latest_version()
        except Exception as e:
            raise e
        return provider

    def install(self, provider_name):
        providers.modules[provider_name].install()

    def setup_discovery(self, provider):
        message = {
            "availability": {
                "topic": f"{self.config['mqtt']['identifier']}/lwt",
                "payload_available": "ON",
                "payload_not_available": "OFF",
            },
            "device": {
                "identifiers": [self.config['mqtt']['identifier']],
                "name": self.config['mqtt']['identifier'],
                "model": self.config['mqtt']['identifier'],
                "manufacturer": f"bkbilly",
                "sw_version": f"Service Updater {self.version}",
            },
            "device_class": "firmware",
            "name": provider.service,
            "title": provider.service,
            "unique_id": provider.service,
            "entity_picture": provider.image,
            "state_topic": f"{self.config['mqtt']['identifier']}/{provider.service}",
            "command_topic": f"{self.config['mqtt']['identifier']}/install",
            "payload_install": provider.name,
        }
        topic = f"homeassistant/update/{self.config['mqtt']['identifier']}/{provider.service}/config"
        self.mqttclient.publish(
            topic,
            payload=json.dumps(message),
            retain=True
        )
        print(topic)
        print(json.dumps(message))

    def send_info(self, provider):
        message = {
          "installed_version": provider.current_version,
          "latest_version": provider.latest_version,
          "release_url": provider.changelog,
        }
        topic = f"{self.config['mqtt']['identifier']}/{provider.service}"
        self.mqttclient.publish(
            topic,
            payload=json.dumps(message),
            retain=True
        )
        print(topic)
        print(json.dumps(message))
