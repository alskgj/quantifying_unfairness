from har_helper import har_timestamp_to_datetime

from constants import itag_to_resolution_num, RESOLUTIONS

import matplotlib.pyplot as plt


def get_timings(entries):
    result = []
    start_time = get_time(entries[0])

    for entry in entries:
        time = get_time(entry)
        timedelta = (time - start_time)
        timedelta = timedelta.seconds + timedelta.microseconds / 1000000

        result.append(timedelta)
    return result


def get_rbufs(entries):
    result = []
    for entry in entries:
        result.append(int(get_param(entry, 'rbuf')))
    return result


def get_resolutions(entries):
    return [itag_to_resolution_num[int(get_param(entry, 'itag'))] for entry in entries]


def plot(har):
    """takes a har and plots range against time"""

    entries = har['log']['entries']
    time_list, rbuf_list = get_timings(entries), get_rbufs(entries)
    resolutions_list = get_resolutions(entries)

    for entry in entries:
        print(itag_to_resolution_num[int(get_param(entry, 'itag'))], get_param(entry, 'itag'),  get_param(entry, 'range'))

    # getting first axis
    fig, ax1 = plt.subplots()
    ax1.plot(time_list, rbuf_list, 'b-')
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('receive buffer', color='b')
    ax1.tick_params('y', colors='b')

    # second axis
    ax2 = ax1.twinx()
    ax2.plot(time_list, resolutions_list, 'r--')
    ax2.set_ylabel('resolution', color='r')
    ax2.tick_params('y', colors='r')
    plt.yticks(RESOLUTIONS)  # manually set ticks to the resolutions form 144p to 1080p

    fig.tight_layout()
    plt.show()
    # TODO save it plt.savefig()


def get_param(entry, param):
    return [query for query in entry['request']['queryString'] if query['name'] == param][0]['value']


def get_time(entry):
    return har_timestamp_to_datetime(entry['startedDateTime'])


