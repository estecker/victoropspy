import logging
import re
from collections import namedtuple

import requests

import Incidents

"""This API may be called a maximum of once a minute."""


class Reports(Incidents.Incidents):
    limit = 100

    def __init__(self, api_base_url=None, api_id=None, api_key=None):
        super().__init__(api_base_url, api_id, api_key)

    def get(self, params):
        """Return a the matching incidents in namedtuple"""
        r = requests.get(self.api_base_url + '/api-reporting/v2/incidents', headers=self.headers, params=params)
        if not r.ok:
            logging.error("Problem with request error code: {} Message: {}".format(r.status_code, r.text))
            r.raise_for_status()
        elif r.json()["total"] > self.limit:  # TODO work on paginated results, VO limits calls to 1 a minute, good luck
            logging.error(
                "There were a total of {} results, but only {} can be returned".format(r.json()["total"], self.limit))
        logging.debug("get() response: offset: {offset}, limit: {limit}, total: {total} ".format(**r.json()))
        for i in r.json()["incidents"]:
            yield namedtuple('incident', i.keys())(**i)

    def search(self, search_kv):
        """search_kv is a list of strings, should be formatted  as key=value"""
        search_params = {"limit": self.limit}
        for kv in search_kv:  # building the search_params dict
            logging.debug("Found search param: {}".format(kv))
            equalsign_regex = re.search('(?P<key>\w+)=(?P<value>\S+)', kv)
            key = equalsign_regex.group('key')
            value = equalsign_regex.group('value')
            logging.debug("Report_param: {} = {}".format(key, value))
            search_params[key] = value
        r = self.get(params=search_params)
        for i in r:
            # TODO filer again on the client based on a regex
            logging.info("{}".format(i))
