#!/usr/bin/env python3

import logging
import sys
import subprocess
import providers
import yaml
import argparse
import asyncio
import timeit

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
        if query_yes_no(f'Start the installation for {provider.service}?'):
            provider.install()


async def run_service(provider):
    runserv_start = timeit.default_timer()
    latest_version, current_version = await asyncio.gather(
        provider.get_latest_version(),
        provider.get_current_version()
    )
    runserv_stop = timeit.default_timer()
    print(f'{provider.service:15} {current_version:15} {latest_version:14} latest={current_version==latest_version} time:{runserv_stop - runserv_start}')

    if latest_version is None:
        print(f'Error finding latest version for {provider.service}')
    elif current_version is None:
        print(f'{provider.service} needs fresh install')
        deside_installation(provider)
    elif current_version != latest_version:
        print(f'{provider.service} needs update')
        deside_installation(provider)


async def main():
    tasks = []
    for provider_name, module in providers.modules.items():
        if provider_name in config and (len(args.service) == 0 or provider_name in args.service):
            provider = module(config[provider_name])
            tasks.append(run_service(provider))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    start = timeit.default_timer()
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
    stop = timeit.default_timer()

    print('Time: ', stop - start)  

    #logging.info("Done")

