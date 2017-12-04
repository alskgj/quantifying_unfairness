from json import loads, dumps
from copy import deepcopy

f = open('../har_files/1512386649.har').read()
har = loads(f)
entries = har['log']['entries']
print(len(entries))

new_entries = []
for entry in entries:
    for header in entry['response']['headers']:
        if 'value' in header and 'video' in header['value']:
            new_entries.append(entry)
            break
print(len(new_entries))

print(entries[0]['response']['headers'])

new_har = deepcopy(har)
new_har['log']['entries'] = new_entries

print(dumps(har))
print(dumps(new_har))

print(len(har['log']['entries']))