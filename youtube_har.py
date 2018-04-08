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

from dateutil.parser import parse
from datetime import timedelta
from json import load
from urllib.parse import parse_qs
import requests
import sys

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class YoutubeHar:
    GET_VIDEO_INFO = 'https://www.youtube.com/get_video_info?video_id='

    def __init__(self, har, video_id=None):
        har = load(open(har))
        self._video_info = None  # used to cache requests made to youtube video_info server

        self.id = video_id
        self.entries = har['log']['entries']

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

        self.segments = newer_entries

        size = self.total_size()

        if self.video_info:
            self.title = self.video_info.get('title', '_')
            self.length_seconds = self.video_info['length_seconds']  # what to do if this is not here?

            print(f'loaded vimeohar, with {size/1000000:.3f} MB downloaded')

            print(f'average resolution: {self.average_resolution()}')
            print(f'average quality change: {self.average_quality_variations()}')

            self.parse_video_info()

    @property
    def video_info(self):
        """Tries to find video_info. Sadly works only with some videos,
        some of them are protected by copyright.

        Since this function makes a request we need to cache it..."""
        if not self.id:
            logger.error('No video id known - can"t get video info')
            return
        if self._video_info:
            return self._video_info
        else:
            video_info = parse_qs(requests.get(self.GET_VIDEO_INFO+self.id).text)

        if 'status' in video_info and video_info['status'][0] == 'fail':
            print(f'Failed to get video info. Reason: {video_info["reason"][0]}')

        video_info = {
            'title': 'Unknown',
            'length_seconds': None
        }

        self._video_info = video_info
        return video_info

    def parse_video_info(self):
        """I think there are three main ways youtube serves videos:
        https://github.com/rg3/youtube-dl/blob/master/youtube_dl/extractor/youtube.py

        1. rtmp - only livestream?
        2. url_encoded_fmt_stream_map and adaptive_fmts
        3. hlsvp

        2.
        ===============
        most important thing seems to be: adaptive_map = parse_qs(self.video_info['adaptive_fmts'][0])
        # explore this further
        might also be helpful: url_encoded_fmt_stream_map

        adaptive_fmts has:

        key, len(value), value
        ====================
        itag 6 ['137', '140', '171', '249', '250', '251']
        index 17 ['716-1791', '243-1788', '714-1789', '243-1780', '715-1790', '243-1764', '715-1790', '243-1738',
        '714-1789', '242-1711', '713-1788', '242-1710', '592-1187', '4452-5247', '272-1067', '272-1067', '272-1067']
        fps 12 ['30', '30', '30', '30', '30', '30', '30', '30', '30', '30', '30', '30']
        url 17 [omitted]
        init 17 ['0-715', '0-242', '0-713', '0-242', '0-714', '0-242', '0-714', '0-242', '0-713', '0-241', '0-712',
        '0-241', '0-591', '0-4451', '0-271', '0-271', '0-271']
        type 17 ['video/mp4; codecs="avc1.640028"', 'video/webm; codecs="vp9"', 'video/mp4; codecs="avc1.4d401f"',
        'video/webm; codecs="vp9"', 'video/mp4; codecs="avc1.4d401f"', 'video/webm; codecs="vp9"',
        'video/mp4; codecs="avc1.4d401e"', 'video/webm; codecs="vp9"', 'video/mp4; codecs="avc1.4d4015"',
        'video/webm; codecs="vp9"', 'video/mp4; codecs="avc1.4d400c"', 'video/webm; codecs="vp9"',
        'audio/mp4; codecs="mp4a.40.2"', 'audio/webm; codecs="vorbis"', 'audio/webm; codecs="opus"',
        'audio/webm; codecs="opus"', 'audio/webm; codecs="opus"']
        projection_type 17 ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1']
        clen 12 ['240197781', '155916239', '124945969', '86655256', '57412087', '43590983', '26382448', '23725307',
        '8678074', '12713709', '4170823', '5614839']
        size 12 ['1920x1080', '1920x1080', '1280x720', '1280x720', '854x480', '854x480', '640x360', '640x360',
        '426x240', '426x240', '256x144', '256x144']
        bitrate 17 ['4416411', '3193895', '2695845', '1755296', '1348383', '889960', '642067', '480823', '248346',
        '257830', '112644', '114639', '128066', '121140', '55045', '71522', '140868']
        quality_label 12 ['1080p', '1080p', '720p', '720p', '480p', '480p', '360p', '360p', '240p', '240p', '144p',
        '144p']
        xtags 12 [',itag=248', ',itag=136', ',itag=247', ',itag=135', ',itag=244', ',itag=134', ',itag=243',
        ',itag=133', ',itag=242', ',itag=160', ',itag=278', ',clen=7326711']
        """
        if 'rtmp' in self.video_info:
            logging.warning('Found rtmp parameter in video_info. Parsing of livestreams not supported.')
            sys.exit(1)
        elif 'url_encoded_fmt_stream_map' in self.video_info or 'adaptive_fmts' in self.video_info:
            adaptive = map(parse_qs, self.video_info['adaptive_fmts'])
            stream_map = map(parse_qs, self.video_info['url_encoded_fmt_stream_map'])

            print('here', list(adaptive))
            for e in adaptive:
                print(e)
            print(stream_map)

    def extract_param(self, entry, param, location='request'):
        try:
            result = [query for query in entry[location]['queryString'] if query['name'] == param][0]['value']
        except IndexError:
            raise TypeError
        return result

    def extract_header(self, entry, param):
        return [query for query in entry['response']['headers'] if query['name'] == param][0]['value']

    def average_resolution(self):
        """QOE metric: Looks at each video segment and returns the average resolution"""
        # itag: resolution
        # clen: length of the segment
        for entry in self.segments:
            try:
                clen = self.extract_param(entry, 'clen')
            except TypeError:
                clen = 'no clen'
            itag = self.extract_param(entry, 'itag')
            try:
                range = self.extract_param(entry, 'range')
            except TypeError:
                range = 'no range'

            print(range, clen, itag, self.extract_param(entry, 'dur'))

        # api: http://www.youtube.com/get video info?video id=
        return NotImplementedError

    def average_quality_variations(self):
        """QOE metric: Returns an int denoting how much the quality changed during the video.
        0 means there was no quality change at all (and all segments had the same resolution)"""
        return NotImplementedError

    def time_spent_rebuffering(self):
        """QOE metric: Take all video-segments (as a list) V. Sorty V by the date and time the respective video-segment
        was fully received. We do a scanline starting at the time the first segment has been saved.
        The scanline will stop each time the current video-segment has it's full duration played back and checks
        if the next segment is already in buffer. If not the difference between now and the point in time it has been
        received will be added to time_spent_rebuffering. We do this until the whole video has been received."""

        # TODO HOW TO RECOGNIZE PAUSE IN VIDEO PLAYBACK - JUST assume it never happens?
        # If I pause for long enough buffer will eventually be full and stop filling,
        # this function will however interpret that as rebuffering
        # Assumption: Playback starts as soon as first segment is fully loaded

        return NotImplementedError

    def video_segments(self):
        # TODO copied from vimeo, evaluate what to keep
        """Returns a list of dictionaries containing following keys:

        req_start: datetime of request start
        req_receive: datetime of end of request (got a positive or negative response -> segment downloaded)
        video_start: int describing the start of this segment in the video in seconds
        video_end: int describing the end of this segment in the video in seconds
        width: the width of the segment
        height: the height of the segment, forms resolution with width parameter
        total_duration: the total duration of the video. this is encoded in each segment since different qualities have
            very slight differences (360p might have duration of 120s, 1080p duration of 119.89s)"""

        video_segments = [segment for segment in self.segments if 'video' in segment['request']['url']]
        result = list()

        for segment in video_segments:
            master = self._segment_to_masterjson(segment)
            data = dict()

            data['req_start'] = parse(segment['startedDateTime'])  # those are absolut datetimes
            data['req_receive'] = data['req_start'] + timedelta(milliseconds=segment['timings']['receive'])

            data['video_start'] = master['start']  # those times are relative: 6 means 6s from start of the video
            data['video_end'] = master['end']

            data['width'] = master['width']
            data['height'] = master['height']

            data['total_duration'] = master['duration']

            result.append(data)

        return result

    def total_size(self):
        return sum([e['response']['bodySize'] for e in self.entries if e['response']['bodySize'] > 0])

    def plot_yt_time(self):
        """ To easily plot the bandwith against time we need to convert it to the right format.
        Sizeofpacket is in megabytes
        :return: [(0, 0), (t1, sizeofpacket1), (t2, sizeofpacket1+sizeofpacket2), ...]
        """

        sizes = [segment['response']['bodySize']/(1024*1024) for segment in self.segments]
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
        times = [(time-starttime).total_seconds() for time in times]

        return list(zip(times, aggregate_sizes))

    def plot_bandwith_time(self, n=3):
        """ Returns the bandwith in an easily plottable way,
        n seconds moving average, megabits/s

        :return:
        """

        # and parses it to a python datetime object
        times = [parse(self.extract_header(segment, 'Date')) for segment in self.segments]
        starttime = times[0]
        # converts all those datetimes into seconds from start, so now we have an int list [0, ...]
        times = [(time-starttime).total_seconds() for time in times]
        sizes = [segment['response']['bodySize'] / (1024 * 1024) for segment in self.segments]

        times_with_sizes = list(zip(times, sizes))

        moving_sizes = []
        for i in range(int(times[-1])-n):
            chunks = [size for time, size in times_with_sizes if i <= time <= i+n-1]
            moving_sizes.append(sum(chunks)/n*8) # divide by n since it's an average, multiply by 8 to get bits
        return list(enumerate(moving_sizes))


class Resolution:
    def __init__(self, width, height):
        self.width, self.height = width, height

    def __repr__(self):
        return f'{round(self.width)}x{round(self.height)}'


if __name__ == '__main__':

    yt = YoutubeHar('/home/nen/PycharmProjects/bachelor_thesis/har_files/youtube_e1_har.json')

    print(yt.plot_yt_time())
