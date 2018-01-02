from json import load
from pprint import pprint

data = load(open('../har_files/vimeo_3min.har'))

entries = data['log']['entries']

mimetypes = set()
jsonentries = list()
for entry in entries:
    mimetypes.add(entry['response']['content']['mimeType'])
    if 'json' in entry['response']['content']['mimeType']:
        jsonentries.append(entry)

for i, entry in enumerate(jsonentries):
    content = entry['response']['content']['text']
    with open(str(i)+'.json', 'w') as fo:
        fo.write(content)

# TODO how are the different chopped segments received? is it posssible to just call <id>/chop/segment-x.m4s? look at example_master.json and at the different requests
