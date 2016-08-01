#!/usr/bin/env python3
import argparse
import logging
import os
import sys

import yaml

import Incidents
import Reports

__author__ = 'estecker@gmail.com'

# Config file that lives in same folder. Added to .gitignore
OX_VO_CONFIG = "config.yml"


def setup(cmd_args):
    conf_file = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + OX_VO_CONFIG
    if not os.path.isfile(conf_file):
        logging.info("Configuration file was not found at {}".format(conf_file))
        logging.info("Looks like you need to setup a few things first")
        api_id = input("What is your API ID?")
        api_key = input("What is your API key? ")
        api_username = input("What is your username?")
        # TODO test out the id/key combo
        config = {"id": api_id, "key": api_key, "api_username": api_username}
        with open(conf_file, 'w') as text_file:  # Write out config file
            text_file.write(yaml.dump(config, default_flow_style=False))
    with open(conf_file, 'r') as conf_file:  # Read in yaml config file every time
        config = yaml.load(conf_file)
        cmd_args.update(config)  # Update cmd_args with new values from config text file
    logging.debug(cmd_args)
    return cmd_args


def main():
    parser = argparse.ArgumentParser(
        epilog="https://portal.victorops.com/dash/open-x/#/api-management")
    parser.add_argument("--action", choices=['list', 'ack-user', 'resolve-user', 'exec', 'report'], required=True,
                        help='"list" will list all active incidents \
                             "ack-user" will acknowledge all incidents assigned to username set in config \
                             "resolve-user" will resolve all incidents assigned to username set in config \
                             "report" will search all incidents')
    parser.add_argument("--regex", default=".*",
                        help="Client side filtering of incidents, Python regex format.")
    parser.add_argument("--report-kv", nargs='*',
                        help="Server side search keys=values. Keys can be found at https://portal.victorops.com/public/api-docs.html")
    parser.add_argument("--exec", default="date", help="Run this command for each matching incident. 'HOSTNAME' and \
                         'INCIDENTNUMBER' will be replaced with the hostname and incident number if found. ")
    parser.add_argument("--verbosity", choices=['warning', 'info', 'debug'], default='info')
    args = parser.parse_args()
    logging.basicConfig(format='%(message)s', stream=sys.stdout, level=args.verbosity.upper())
    setup(vars(args))
    incidents = Incidents.Incidents(api_id=args.api_id, api_key=args.api_key, api_base_url=args.api_base_url)
    reports = Reports.Reports(api_id=args.api_id, api_key=args.api_key, api_base_url=args.api_base_url)
    if args.action == 'list' and args.report_kv:
        logging.error("These combination of arguments are not supported yet")
        parser.print_help()
    if args.action == 'list':
        incident_search = incidents.search(args.regex)
        for i in incident_search:
            logging.info("{}".format(i))
    elif args.action == 'exec' and args.exec:
        incidents.exec(search_string=args.regex, command_line=args.exec)
    elif args.action == 'ack-user':
        incidents.ack_user(args.api_username)
    elif args.action == 'resolve-user':
        incidents.resolve_user(args.api_username)
    elif args.action == 'report' and args.report_kv:
        report_res = reports.search(search_kv=args.report_kv)
        print(report_res)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
