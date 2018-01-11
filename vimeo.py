"""
    vimeo
    ~~~~~~~~~~~~~~

    Parsing of Vimeohar happens here.
    In particular methods to measure standard QOE metrics are implemented in vimeo.VimeoHar.

    To compare HAR files from different sources (Vimeo, YT, pensieve...) I want to use the QOE metric as described
    in the original MPC paper (a control theoretic approach to ABR:

    Implemented:
    - average video resolution
    - average quality variations

    TODO:
    - time spent rebuffering
    - startup delay

"""


from json import loads
import re
from dateutil.parser import parse
from datetime import timedelta


class VimeoHar:
    def __init__(self, har):
        self.entries = har['log']['entries']

        self.segments = [e for e in self.entries if 'segment' in e['request']['url'] if e['response']['status'] == 200]

        size = self.total_size()
        print(f'loaded vimeohar, with {size} bits downloaded')

        print(f'average resolution: {self.average_resolution()}')
        print(f'average quality change: {self.average_quality_variations()}')

    def masterjson(self):
        """Returns the master.json file. Only exists in Vimeo Har files.
        """
        for entry in self.entries:
            if 'json' in entry['response']['content']['mimeType'] and 'master.json' in entry['request']['url']:
                return loads(entry['response']['content']['text'])

    def _url_to_resolution(self, url):
        """Takes a vimeo segment url (.../video/id/chop/segment1.pm4) and returns up all relevant info in master.json"""
        pattern = re.compile(r'/(video|audio)/(\d+)/chop')
        id_ = pattern.findall(url)
        if not id_:
            print(f'url {url} does not contain a vimeo id.')
            return

        result = None
        type_, id_ = id_[0]
        for element in self.masterjson()[type_]:
            if element['id'] == id_:
                result = element
                break

        if not result:
            print(f'no result found for url {url}')
            return

        if type_ == 'audio':
            return f'audio with {result["avg_bitrate"]} average bitrate'
        elif type_ == 'video':
            return f'video with resolution {result["width"]}x{result["height"]}'

    def _segment_to_masterjson(self, segment):
        """Takes an entry which represents a GET request to a segment -> url is .../segment-1.m4s or similar
        returns the json object within the master.json that describes attributes of this object"""
        url = segment['request']['url']
        pattern = re.compile(r'/(video|audio)/(\d+)/chop')
        id_ = pattern.findall(url)
        if not id_:
            print(f'url {url} does not contain a vimeo id.')
            return

        result = None
        type_, id_ = id_[0]
        for element in self.masterjson()[type_]:
            if element['id'] == id_:
                result = element
                break

        if not result:
            print(f'no result found for url {url}')
            return

        for seg in result['segments']:
            if seg['url'] in url:
                result['start'], result['end'] = seg['start'], seg['end']

        return result

    def average_resolution(self):
        """QOE metric: Looks at each video segment and returns the average resolution"""
        video_segments = self.video_segments()
        average_width = sum([segment['width'] for segment in video_segments])/len(video_segments)
        average_height = sum([segment['height'] for segment in video_segments])/len(video_segments)
        return Resolution(width=average_width, height=average_height)

    def average_quality_variations(self):
        """QOE metric: Returns an int denoting how much the quality changed during the video.
        0 means there was no quality change at all (and all segments had the same resolution)"""
        video_segments = self.video_segments()
        width, height = 0, 0
        for i in range(len(video_segments) - 1):
            width += abs(video_segments[i]['width'] - video_segments[i+1]['width'])
            height += abs(video_segments[i]['height'] - video_segments[i+1]['height'])
        width, height = width/len(video_segments), height/len(video_segments)
        return Resolution(width, height)

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

        vs = self.video_segments()

        # sort video segments by time data was received
        vs = sorted(vs, key=lambda a: a['req_receive'])
        current_segment = [v for v in vs if v['video_start'] == 0][0]
        current_time = current_segment['req_receive']
        while True:
            if current_segment['video_end'] == current_segment['total_duration']:
                print('yay')
                break

            # TODO THIS WILL CRASH ON HAR FILE WHICH HASN"T PLAYED FULL VIDEO, maybe try and break if no next segmetn
            next_segment = [s for s in vs if s['video_start'] == current_segment['video_end']][0]
            break

    def video_segments(self):
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
    from json import load
    data = load(open('../har_files/vimeo_parallel1515014752.har'))
    VimeoHar(data)