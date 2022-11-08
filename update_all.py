#!/usr/bin/env python3

import logging
import sys
import subprocess
import providers
import yaml
import argparse
import asyncio
import json
import timeit
from packaging import version

parser = argparse.ArgumentParser(description='Update services on local machine')
parser.add_argument('-c', '--config', help='YAML file with the configuration', default='providers.yaml')
parser.add_argument('-u', '--unattended', help='Install without asking', action='store_true')
parser.add_argument('-s', '--service', help='Run for specific service. More than one can be added sepperated by space', nargs='+', default=[])
parser.add_argument('-d', '--display', help="Don't ask for installation/update", action='store_true')
parser.add_argument('-j', '--json', help='Display results as json', action='store_true')

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


def deside_installation(provider, query=None):
    if args.unattended or query is None:
        provider.install()
    else:
        if query_yes_no(query):
            provider.install()


async def run_service(provider):
    service_info = {}
    runserv_start = timeit.default_timer()
    try:
        latest_version = await provider.get_latest_version()
    except Exception as e:
        latest_version = '0'

    try:
        current_version = await provider.get_current_version()
    except Exception as e:
        current_version = '0'

    runserv_stop = timeit.default_timer()
    runserv_total = round(runserv_stop - runserv_start, 3)

    service_info['service'] = provider.service
    service_info['latest_version'] = latest_version
    service_info['current_version'] = current_version
    service_info['total_time'] = runserv_total
    service_info['latest'] = version.parse(current_version) >= version.parse(latest_version)
    service_info['provider'] = provider

    return service_info


async def main():
    tasks = []
    for provider_name, module in providers.modules.items():
        if provider_name in config and (len(args.service) == 0 or provider_name in args.service):
            provider = module(config[provider_name])
            tasks.append(run_service(provider))

    services_sum = {
        'srv_toupdate': [],
        'srv_toinstall': [],
        'srv_uptodate': [],
        'needs_update': False,
    }
    for provider in await asyncio.gather(*tasks):
        if provider['current_version'] is None:
            services_sum['srv_toinstall'].append(provider['service'])
        elif provider['latest']:
            services_sum['srv_uptodate'].append(provider['service'])
        else:
            services_sum['srv_toupdate'].append(provider['service'])
            services_sum['needs_update'] = True

        if not args.json:
            print(f"{provider['service']:20} {provider['current_version']:15} {provider['latest_version']:14} latest={provider['latest']} \ttime={provider['total_time']}s")

        if not args.display:
            if provider['latest'] is None:
                print(f'Error finding latest version for {provider.service}')
            elif provider['current_version'] is None:
                deside_installation(provider['provider'], f'Start fresh installation for {provider["service"]}?')
            elif not provider['latest']:
                deside_installation(provider['provider'], f'Start update for {provider["service"]}?')
    if args.json:
        print(json.dumps(services_sum))

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

    asyncio.run(main())

    #logging.info("Done")

