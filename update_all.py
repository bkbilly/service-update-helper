#!/usr/bin/env python3

import logging
import sys
import subprocess
import providers
import yaml
import argparse

parser = argparse.ArgumentParser(description='Update services on local machine')
parser.add_argument('-c', '--config', help='YAML file with the configuration', default='providers.yaml')
parser.add_argument('-u', '--unattended', help='Install without asking', action='store_true')
parser.add_argument('-s', '--service', help='Run for specific service. More than one can be added sepperated by space', nargs='+', default=[])

args = parser.parse_args()


def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def deside_installation(provider):
    if args.unattended:
        provider.install()
    else:
        if query_yes_no('Start the installation?'):
            provider.install()
    

if __name__ == "__main__":
    # Load config
    with open(args.config) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # Force run with root
    username = str(subprocess.check_output("whoami").decode('utf-8').strip())
    if username != "root":
        logging.critical("You have to be root to run this app, current user is: {}".format(username))
        sys.exit()
    
    # Set logging directory
    #logging.basicConfig(
    #    filename='/var/log/updater.log',
    #    format='%(asctime)s - %(levelname)s - %(message)s',
    #    level=logging.INFO
    #)

    
    for provider_name, module in providers.modules.items():
        if provider_name in config and (len(args.service) == 0 or provider_name in args.service):
            provider = module(config[provider_name])
            latest_version = provider.get_latest_version()
            current_version = provider.get_current_version()
            print(f'{provider.service:15} {current_version:15} {latest_version:14} latest={current_version==latest_version}')

            if latest_version is None:
                print('Error finding latest version')
            elif current_version is None:
                print('Needs fresh install')
                deside_installation(provider)
            elif current_version != latest_version:
                print('Needs update')
                deside_installation(provider)

    #logging.info("Done")

