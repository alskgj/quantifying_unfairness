from abc import ABC, abstractmethod
from dateutil.parser import parse
from datetime import timedelta
from json import load
from json import loads
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
    def size(self):
        return sum([e['response']['bodySize'] for e in self.entries if e['response']['bodySize'] > 0])

    @ abstractmethod
    def starttime(self):
        """Returns the datetime of the start object"""
        pass


class VimeoHar(HarBase):
    def __init__(self, har):
        super(VimeoHar, self).__init__(har)
        logger.info(f'Loaded har with Vimeo id {self.id}, {len(self.segments)} segments, size {self.size} downloaded.')

    def filterfor_videoentries(self):
        return [e for e in self.entries if 'segment' in e['request']['url'] if e['response']['status'] == 200]

    def find_video_id(self):
        urls = [entry['request']['url'] for entry in self.entries if 'vimeo' in entry['request']['url']]
        for url in urls:
            if re.search(r'video/([\d\w]+)', url):
                return re.findall(r'video/([\d\w]+)', url)[0]

    def quality(self):
        segments = self.video_segments()

        widths = [segment['width'] for segment in segments]
        heigths = [segment['height'] for segment in segments]

        return zip(widths, heigths)

    def plot_time_quality(self):
        """ To easily plot the quality against time we need to convert it to the right format.
        If we have the heigth data points: [270, 360, 360], and total duration 20 we get:

        [270, None (4 times), 270, 360, None (4 times), 360, 360, None (4 times), 360, None (2 times)]
        --> since we know each segment in vimeo is 6 seconds long

        :return: [(0, 270), None, None, None, None (5, 270), None, ...]
        """
        segments = self.video_segments()
        downloaded_duration = len(segments)*6

        ########################################################
        # Get the quality by looking at the request headers,
        # those are sorted by har timings.
        # Only get the newest datapoint for each playbacktime.
        ########################################################
        data = [(s['height'], s['video_start']) for s in segments]
        newdata = {}

        for point in data:
            newdata[point[1]] = point[0]
        data = list(newdata.items())

        ########################################################
        # Insert some datapoints to reflect that a quality
        # stays for the whole duration of the chunk.
        ########################################################
        newdata = []
        oldqual = data[0][1]

        for point in data:
            if point[1] == oldqual:
                newdata.append(point)
            else:
                newdata.append((point[0], oldqual))
                newdata.append(point)
                oldqual = point[1]

        return newdata

    def extract_param(self, entry, param, location='request'):
        try:
            result = [query for query in entry[location]['headers'] if query['name'] == param][0]['value']
        except IndexError:
            raise TypeError
        return result

    def plot_mb_time(self):
        """ To easily plot the bandwith against time we need to convert it to the right format.
        Packetsize is in megabytes
        :return: [(0, 0), (t1, sizeofpacket1), (t2, sizeofpacket1+sizeofpacket2), ...]
        """

        sizes = [segment['response']['bodySize']/1000000 for segment in self.segments]
        aggregate_sizes = []
        current = 0
        for size in sizes:
            current += size
            aggregate_sizes.append(current)

        # dateutil magic here. gets date of completion (something like 'Thu, 05 Apr 2018 19:50:17 GMT')
        # and parses it to a python datetime object
        times = [parse(self.extract_param(segment, 'Date', 'response')) for segment in self.segments]
        starttime = times[0]
        # converts all those datetimes into seconds from start, so now we have an int list [0, ...]
        times = [(time-starttime).total_seconds() for time in times]

        return list(zip(times, aggregate_sizes))

    def plot_bandwidth_time(self, n=3):
        """ Returns the bandwith in an easily plottable way,
        n seconds moving average, megabits/s

        :return:
        """

        # and parses it to a python datetime object
        times = [parse(self.extract_param(segment, 'Date', 'response')) for segment in self.segments]
        starttime = times[0]
        # converts all those datetimes into seconds from start, so now we have an int list [0, ...]
        times = [(time-starttime).total_seconds() for time in times]
        sizes = [segment['response']['bodySize'] / 1000000 for segment in self.segments]

        times_with_sizes = list(zip(times, sizes))

        moving_sizes = []
        for i in range(int(times[-1])-n):
            chunks = [size for time, size in times_with_sizes if i <= time <= i+n-1]
            moving_sizes.append(sum(chunks)/n*8)  # divide by n since it's an average, multiply by 8 to get bits
        return list(enumerate(moving_sizes))

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
            logger.error(f'url {url} does not contain a vimeo id.')
            return

        result = None
        type_, id_ = id_[0]
        for element in self.masterjson()[type_]:
            if element['id'] == id_:
                result = element
                break

        if not result:
            logger.warning(f'no result found for url {url}')
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
            logger.error(f'url {url} does not contain a vimeo id.')
            return

        result = None
        type_, id_ = id_[0]
        for element in self.masterjson()[type_]:
            if element['id'] == id_:
                result = element
                break

        if not result:
            logger.warning(f'no result found for url {url}')
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

    def starttime(self):
        return parse(self.segments[0]['startedDateTime'])

    def buffer_times(self):
        """Gives an estimate of the available buffer at the client for each second of playback"""


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
            if re.search(r'watch\?v=([\w-]+)', url):
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
        try:
            return [query for query in entry['response']['headers'] if query['name'] == param][0]['value']
        except IndexError:
            return None

    def plot_mb_time(self):
        """ To easily plot the data downloaded against time we need to convert it to the right format.
        Sizeofpacket is in megabytes
        :return: [(0, 0), (t1, sizeofpacket1), (t2, sizeofpacket1+sizeofpacket2), ...]
        """

        sizes = [segment['response']['bodySize'] / 1000000 for segment in self.segments]
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

    def _segmenttime(self):
        """Returns a list of times when segments occured relative to the start of the video.
        Starts with 0 and is increasing"""
        # and parses it to a python datetime object
        times = [parse(self.extract_header(segment, 'Date')) for segment in self.segments]
        starttime = times[0]
        # converts all those datetimes into seconds from start, so now we have an int list [0, ...]
        return [(time - starttime).total_seconds() for time in times]

    def plot_bandwidth_time(self, n=3):
        """ Returns the bandwidth in an easily plottable way,
        n seconds moving average, megabits/s
        """

        times = self._segmenttime()
        sizes = [segment['response']['bodySize'] / 1000000 for segment in self.segments]

        times_with_sizes = list(zip(times, sizes))

        moving_sizes = []
        for i in range(int(times[-1]) - n):
            chunks = [size for time, size in times_with_sizes if i <= time <= i + n - 1]
            moving_sizes.append(sum(chunks) / n * 8)  # divide by n since it's an average, multiply by 8 to get bits
        return list(enumerate(moving_sizes))

    def plot_rbuf_time(self):
        """Returns the current rbuf in an easily plottable way,
        megabit/s"""

        times = self._segmenttime()
        rbuf = [round(int(self.extract_param(segment, 'rbuf'))/1000, 2) for segment in self.segments]
        return list(zip(times, rbuf))

    def starttime(self):
        """Returns the datetime of the start object"""
        return parse(self.extract_header(self.segments[0], 'Date'))


class Resolution:
    def __init__(self, width, height):
        self.width, self.height = width, height

    def __repr__(self):
        return f'{round(self.width)}x{round(self.height)}'


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    yt = YoutubeHar('/home/nen/PycharmProjects/bachelor_thesis/har_files/youtube_combined_e4_har.json')
    vime = VimeoHar('/home/nen/PycharmProjects/bachelor_thesis/har_files/vimeo_combined_e4_har.json')
    # print(util.jain([vime, yt]))

    # print(yt.plot_rbuf_time())
    # print(yt.plot_bandwidth_time())
