from abc import ABC, abstractmethod, abstractproperty
from dateutil.parser import parse
from datetime import timedelta
from json import load
from urllib.parse import parse_qs
import requests
import sys
import re
from postprocessor import util

import logging

logger = logging.getLogger(__name__)


class HarBase(ABC):
    def __init__(self, har):
        har = load(open(har))
        self.entries = har['log']['entries']
        self.segments = self.filterfor_videoentries()
        self.id = self.find_video_id()

    @abstractmethod
    def find_video_id(self):
        pass

    @abstractmethod
    def filterfor_videoentries(self):
        pass

    @property
    @abstractmethod
    def size(self):
        pass


class VimeoHar(HarBase):
    pass


class YoutubeHar(HarBase):
    """
    youtube
    ~~~~~~~~~~~~~~

    Parsing of Youtubehar happens here.
    In particular methods to measure standard QOE metrics are implemented in youtube.Har.

    To compare HAR files from different sources (Vimeo, YT, pensieve...) I want to use the QOE metric as described
    in the original MPC paper (a control theoretic approach to ABR:

    TODO:
    - average quality variations
    - average video resolution
    - time spent rebuffering
    - startup delay

    """

    def __init__(self, har):
        super(YoutubeHar, self).__init__(har)
        logger.info(f'Loaded har with YouTube id {self.id}, {len(self.segments)} segments, size {self.size} downloaded.')

    def find_video_id(self):
        urls = [entry['request']['url'] for entry in self.entries if 'youtube' in entry['request']['url']]
        for url in urls:
            if re.findall(r'watch\?v=([\w-]+)', url):
                return re.findall(r'watch\?v=([\w-]+)', url)[0]

    def filterfor_videoentries(self):
        """For YouTube we first remove all entries not containing an itag,
        then remove everything not containing video as mime type"""
        # sort out everything without itag
        new_entries = []
        for entry in self.entries:
            for request_string in entry['request']['queryString']:
                if 'value' in request_string and 'itag' in request_string['value']:
                    new_entries.append(entry)
                    break

        # sort out everything not video (audio)
        newer_entries = []
        for entry in new_entries:
            mime = [x['value'] for x in entry['request']['queryString'] if x['name'] == 'mime'][0]
            if 'video' in mime:
                newer_entries.append(entry)
        return newer_entries

    # noinspection PyMethodMayBeStatic
    def extract_param(self, entry, param, location='request'):
        try:
            result = [query for query in entry[location]['queryString'] if query['name'] == param][0]['value']
        except IndexError:
            raise TypeError
        return result

    # noinspection PyMethodMayBeStatic
    def extract_header(self, entry, param):
        return [query for query in entry['response']['headers'] if query['name'] == param][0]['value']

    @property
    def size(self):
        return sum([e['response']['bodySize'] for e in self.entries if e['response']['bodySize'] > 0])

    def plot_yt_time(self):
        """ To easily plot the bandwith against time we need to convert it to the right format.
        Sizeofpacket is in megabytes
        :return: [(0, 0), (t1, sizeofpacket1), (t2, sizeofpacket1+sizeofpacket2), ...]
        """

        sizes = [segment['response']['bodySize'] / (1024 * 1024) for segment in self.segments]
        aggregate_sizes = []
        current = 0
        for size in sizes:
            current += size
            aggregate_sizes.append(current)

        # dateutil magic here. gets date of completion (something like 'Thu, 05 Apr 2018 19:50:17 GMT')
        # and parses it to a python datetime object
        times = [parse(self.extract_header(segment, 'Date')) for segment in self.segments]
        starttime = times[0]
        # converts all those datetimes into seconds from start, so now we have an int list [0, ...]
        times = [(time - starttime).total_seconds() for time in times]

        return list(zip(times, aggregate_sizes))

    def plot_bandwith_time(self, n=3):
        """ Returns the bandwith in an easily plottable way,
        n seconds moving average, megabits/s
        """

        # and parses it to a python datetime object
        times = [parse(self.extract_header(segment, 'Date')) for segment in self.segments]
        starttime = times[0]
        # converts all those datetimes into seconds from start, so now we have an int list [0, ...]
        times = [(time - starttime).total_seconds() for time in times]
        sizes = [segment['response']['bodySize'] / (1024 * 1024) for segment in self.segments]

        times_with_sizes = list(zip(times, sizes))

        moving_sizes = []
        for i in range(int(times[-1]) - n):
            chunks = [size for time, size in times_with_sizes if i <= time <= i + n - 1]
            moving_sizes.append(sum(chunks) / n * 8)  # divide by n since it's an average, multiply by 8 to get bits
        return list(enumerate(moving_sizes))


class Resolution:
    def __init__(self, width, height):
        self.width, self.height = width, height

    def __repr__(self):
        return f'{round(self.width)}x{round(self.height)}'


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    yt = YoutubeHar('/home/nen/PycharmProjects/bachelor_thesis/har_files/youtube_combined_e4_har.json')

    print(util.jain([yt, yt]))
