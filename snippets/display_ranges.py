from json import load
from har_helper import har_timestamp_to_datetime

from har_helper import youtube_cleaner
from constants import itag_to_resolution

import matplotlib.pyplot as plt



har = youtube_cleaner(load(open('../har_files/test_short_video_2.har')))

entries = har['log']['entries']
print(entries)


def get_param(entry, param):
    return [query for query in entry['request']['queryString'] if query['name'] == param][0]['value']


def get_itag(entry):
    """iterate over all parameters in the querystring, find parameter with name itag and return value of it"""
    return int([query for query in entry['request']['queryString'] if query['name'] == 'itag'][0]['value'])


def get_range(entry):
    return [query for query in entry['request']['queryString'] if query['name'] == 'range'][0]['value']


def get_time(entry):
    return har_timestamp_to_datetime(entry['startedDateTime'])


first = True
time_list, rbuf_list = [], []

for entry in entries:
    time = get_time(entry)
    if first:
        first = False
        start_time = time
        print('here')

    timedelta = (time-start_time)
    timedelta = timedelta.seconds+timedelta.microseconds/1000000

    time_list.append(timedelta)
    rbuf_list.append(int(get_param(entry, 'rbuf')))

    itag = itag_to_resolution[get_itag(entry)]
    ranges = get_range(entry).split('-')

    # print(f'time: {time}')
    # print(f"Segment length: {int(get_param(entry, 'clen')):,}, requested_range: {ranges}", end='\t\t')
    # print("resolution %s" % itag)
    # print(get_param(entry, 'rbuf'), '\t', itag)
    # print(get_param(entry, 'dur'))
    # print(get_param(entry, 'rn'))

plt.plot(time_list, rbuf_list, label='linear')

plt.legend()
plt.show()

"""
rbuf is receive buffer, but is it in milliseconds? in bytes?

time is in format: 
"""