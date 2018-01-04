from json import load, dump, loads
from pprint import pprint

data = load(open('../har_files/vimeo_parallel1515014752.har'))

entries = data['log']['entries']

for entry in entries:
    if 'json' in entry['response']['content']['mimeType'] and 'master.json' in entry['request']['url']:
        master = loads(entry['response']['content']['text'])

with open('master.json', 'w') as fo:
    dump(master, fo)

# TODO how are the different chopped segments received? is it posssible to just call <id>/chop/segment-x.m4s? look at example_master.json and at the different requests
