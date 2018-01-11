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
from copy import deepcopy
from dateutil.parser import parse
from datetime import timedelta
from json import load

class Har:
    def __init__(self, har):
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
        print(f'loaded har, with {size} bits downloaded')

        print(f'average resolution: {self.average_resolution()}')
        print(f'average quality change: {self.average_quality_variations()}')

    def get_param(self, entry, param):
        for e in entry['request']['queryString']:
            #print(e)
            pass


        try:
            result = [query for query in entry['request']['queryString'] if query['name'] == param][0]['value']
        except IndexError:
            raise TypeError
        return result

    def average_resolution(self):
        """QOE metric: Looks at each video segment and returns the average resolution"""
        # itag: resolution
        # clen: length of the segment
        for entry in self.segments:
            try:
                clen = self.get_param(entry, 'clen')
            except TypeError:
                clen = 'no clen'
            itag = self.get_param(entry, 'itag')
            range = self.get_param(entry, 'range')

            print(itag, clen, range)
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


class Resolution:
    def __init__(self, width, height):
        self.width, self.height = width, height

    def __repr__(self):
        return f'{round(self.width)}x{round(self.height)}'


if __name__ == '__main__':

    data = load(open('har_files/fullscreen_test1501515674088.har'))
    Har(data)
