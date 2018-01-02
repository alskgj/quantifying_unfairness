from copy import deepcopy

import logging
logger = logging.getLogger()

import datetime
import re

from json import loads


def youtube_cleaner(json_dump):
    entries = json_dump['log']['entries']
    logger.info('Got har with %s entries' % len(entries))

    # sort out everything without itag
    new_entries = []
    for entry in entries:
        for request_string in entry['request']['queryString']:
            if 'value' in request_string and 'itag' in request_string['value']:
                new_entries.append(entry)
                break

    # sort out everything not video (mostly audio)
    newer_entries = []
    for entry in new_entries:
        mime = [x['value'] for x in entry['request']['queryString'] if x['name']=='mime'][0]
        if 'video' in mime:
            newer_entries.append(entry)

    new_har = deepcopy(json_dump)
    new_har['log']['entries'] = newer_entries

    logger.info('Returning har with %s entries' % len(newer_entries))
    return new_har


def vimeo_cleaner(json_dump):
    entries = json_dump['log']['entries']
    logger.info('Got har with %s entries' % len(entries))

    # sort out everything which doesn't have 'segment' and 'video' in it's url
    new_entries = [e for e in entries if 'video' in e['request']['url'] and 'segment' in e['request']['url']]
    new_har = deepcopy(json_dump)
    new_har['log']['entries'] = new_entries

    logger.info('Returning har with %s entries' % len(new_entries))
    return new_har


def vimeo_master_json(json_dump):
    """Takes a vimeo har file and returns the master.json"""
    entry = [entry for entry in json_dump['log']['entries'] if 'master.json' in entry['request']['url']][0]
    content = loads(entry['response']['content']['text'])
    return content

class HarParser:
    def __init__(self, har):
        self.entries = har['log']['entries']

    def plot_har(self):
        pass


def har_timestamp_to_datetime(timestamp):
    """takes 2017-12-06T16:29:37.284+01:00 and converts it to a proper python datetime object, messing with microseconds
    and timezones is somewhat messy, so we use regex..."""
    result = re.findall(r'\d+', timestamp)[:-2]
    year, month, day, hour, minutes, seconds, milliseconds = map(int, result)
    dt = datetime.datetime(year, month, day, hour, minutes, seconds, milliseconds*1000)
    return dt

if __name__ == '__main__':

    from json import load
    from logging import basicConfig
    basicConfig(level=logging.INFO)
    youtube_cleaner(load(open('har_files/fullscreen_test.har')))