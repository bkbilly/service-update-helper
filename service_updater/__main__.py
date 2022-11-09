#!/usr/bin/env python3

import signal
import yaml
import time
import paho.mqtt.client as mqtt
import importlib.metadata
import argparse
import os

from .service_update import ServiceUpdate

version = importlib.metadata.version(__package__ or __name__)


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print("Stopped by user")
        self.kill_now = True


class MqttObj:
    def __init__(self, config):
        self.config = config
        self.client = self.setup_mqtt()
        self.updater = ServiceUpdate(self.config, self.client, version)

    def setup_mqtt(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.username_pw_set(self.config['mqtt']['auth']['user'], self.config['mqtt']['auth']['pass'])
        client.connect(self.config['mqtt']['server'], self.config['mqtt']['port'], 60)
        client.loop_start()
        return client

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT with code {rc}")
        client.subscribe(f"{self.config['mqtt']['identifier']}/install")
        self.client.publish(
            f"{self.config['mqtt']['identifier']}/lwt",
            payload="ON",
            retain=True
        )
        self.updater.start()

    def on_message(self, client, userdata, msg):
        print(f"Message received: {msg.topic}")
        print(msg.payload)
        self.updater.install(msg.payload.decode())

    def disconnect(self):
        self.client.publish(
            f"{self.config['mqtt']['identifier']}/lwt",
            payload="OFF",
            retain=True
        )
        self.updater.stop()


def main():
    parser = argparse.ArgumentParser(
        prog="Service Updater",
        description="Send service update information to MQTT broker")
    parser.add_argument(
        "-c", "--config",
        help="Configuration file",
        required=True)
    args = parser.parse_args()

    config_file = os.path.abspath(args.config)
    # config.setup_config(config_file)
    # config.setup_systemd(config_file)

    with open(config_file) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    mqtt_obj = MqttObj(config)

    killer = GracefulKiller()
    while not killer.kill_now:
        time.sleep(1)
    mqtt_obj.disconnect()


if __name__ == '__main__':
    main()
