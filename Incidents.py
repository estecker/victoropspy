import logging
import re
import subprocess
from collections import namedtuple

import requests

"""
Class to get and search for incidents. An incident is currently open, acknowledged or recently resolved, otherwise
it can be found via the reports API.
"""


class Incidents(object):

    def __init__(self, api_base_url=None, api_id=None, api_key=None):
        self.api_base_url = api_base_url
        self.api_id = api_id
        self.api_key = api_key
        self.headers = {'X-VO-Api-Id': self.api_id, 'X-VO-Api-Key': self.api_key}

    def get(self):
        """Using namedtuple so I can reference keys like class objects"""
        r = requests.get(self.api_base_url + '/api-public/v1/incidents', headers=self.headers)
        logging.debug("Incident.get: {}".format(r.url))
        incidents = r.json()["incidents"]
        for i in incidents:
            yield namedtuple('incident', i.keys())(**i)

    def search(self, search_string):
        """Searching using client side regex on all returned incidents"""
        logging.debug("Starting search with search_string of: {}".format(search_string))
        incidents = self.get()
        equalsign_regex = re.search('(?P<key>\w+)=(?P<value>\w+)', search_string)
        if equalsign_regex:  # Search string contains a '=' so I assume it's just key=value for search
            logging.debug("Found a '=' in your search regex, will assume it's key=value")
            key = equalsign_regex.group('key')
            value = equalsign_regex.group('value')
            for i in incidents:
                if key in i._fields:  # First check if key is even there
                    if getattr(i, key) == str(value):
                        yield(i)
        else:  # Just try to find the search_string anywhere in the json
            r = re.compile(search_string)
            for i in incidents:
                match = r.search(str(i))  # Turn the dict into a string for the search
                if match:
                    yield(i)

    def exec(self, command_line, search_string):
        """Run command_line for every incident matching search_string"""
        for i in self.search(search_string):
            command_line_list = command_line.split(' ')
            command = []
            for arg in command_line_list:
                if arg == 'HOSTNAME':
                    command.append(i.host)
                elif arg == 'INCIDENTNUMBER':
                    command.append(i.incidentNumber)
                else:
                    command.append(arg)
            logging.debug("Will run this command: {} on {}".format(command, i))
            subprocess.run(command)

    def ack(self):
        """TODO PATCH /api-public/v1/incidents/ack
        This will be a bit more complicated since you have to find the incident first.
        PATCH data:
        {
          "userName": "string",
          "incidentNames": [
            "string"
          ],
          "message": "string"
        }
        """

    def ack_user(self, username):
        """ This will ack any incident assigned to you, even if the incident is already acked"""
        body = {"userName": username, "message": "Acked via victoropspy"}
        r = requests.patch(self.api_base_url + '/api-public/v1/incidents/byUser/ack', headers=self.headers, json=body)
        if r.ok and r.json()['results']:
            logging.info("Acknowledged these incidents:")
            for i in r.json()['results']:
                logging.info(i)
        else:
            logging.info("Nothing happened. Are there any incidents assigned to {}?".format(username))

    def resolve(self):
        """TODO PATCH PATCH /api-public/v1/incidents/resolve"""

    def resolve_user(self, username):
        """ This will resolve all incidents assigned to username set in config"""
        body = {"userName": username, "message": "Resolved via victoropspy"}
        r = requests.patch(self.api_base_url + '/api-public/v1/incidents/byUser/resolve', headers=self.headers, json=body)
        if r.ok and r.json()['results']:
            logging.info("Resolved these incidents:")
            for i in r.json()['results']:
                logging.info(i)
        else:
            logging.info("Nothing happened. Are there any incidents assigned to {}?".format(username))
