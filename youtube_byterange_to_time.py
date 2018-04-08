"""
    yotube_byterange_to_time
    ========================

    This script provides functionality to convert a youtube byterange, as seen
    in youtube parameters (range param) to a time in a video.

    To use this install youtube-dl and ffprobe

    To provide this functionality the script
    1. Searches for the itag in the segment
    2. Uses `youtube-dl -F url` to download the video if it's not already cached
    3. Uses `ffprobe -show_packets path` to match the byte range to playtime seconds
    4. returns a tuple (starttime, endttime)

    Done 1 and 2
    TODO 3 and 4

"""

from youtube_har import YoutubeHar
from config import CACHE_DIR
import os
import subprocess

import logging
logger = logging.getLogger(__name__)
import config
import shlex
import re


class Ranger:
    """Provides functionality to convert a youtube bytrange to playtime seconds"""

    def __init__(self, videourl, videotitle):
        self.url = videourl
        self.title = videotitle

    def segment_to_playtime(self, segment, return_itag=False):
        """Takes a har entry as input, which is a youtube segment,
        returns a time range."""
        itag = [e for e in segment['request']['queryString'] if e['name'] == 'itag'][0]['value']
        if not self.is_cached(itag):
            logger.warning(f'{self.title} is not cached - downloading it')
            self.download(itag)
        byterange = [e for e in segment['request']['queryString'] if e['name'] == 'range'][0]['value']
        start, end = byterange.split('-')

        if return_itag:
            return self.size_to_time(start, itag), self.size_to_time(end, itag), itag
        else:
            return self.size_to_time(start, itag), self.size_to_time(end, itag)

    def download(self, itag):
        """Creates the caching dir if it doesn't exist, then downloads the video and
        saves it at caching_dir/name_itag"""
        if not os.path.exists(CACHE_DIR):
            logger.warning(f'creating {CACHE_DIR}')
            os.mkdir(CACHE_DIR)
        path = os.path.join(CACHE_DIR, f'{self.title}_{itag}')
        ret = subprocess.run(['youtube-dl', '-f', str(itag), self.url, '-o', path])
        if ret.returncode != 0:
            logger.error(f'Something went horribly wrong while downloading {self.title} at {self.url}')
            return

    def is_cached(self, itag):
        """Returns true if caching_dir/name_itag exists"""
        return os.path.exists(os.path.join(CACHE_DIR, f'{self.title}_{itag}'))

    def size_to_time(self, size, itag):
        size = int(size)
        path = os.path.join(CACHE_DIR, f'{self.title}_{itag}')

        # this pattern matches:
        # pts_time=float - the float is a group
        # an arbitrary amount of whitespaces, digits, letter, underscore, . /, \
        # pos=int        - the int is a group
        pattern = re.compile('pts_time=(\d+\.\d+)[\s\w=\.\/]*pos=(\d+)')

        # for some reason all the output is in err
        process = subprocess.Popen(shlex.split(f'ffprobe -show_packets {path}'),
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)

        data = []
        while True:
            output = process.stdout.read(4000)
            if output == b'' and process.poll() is not None:
                break
            if output:
                output = output.decode()

                data += pattern.findall(output)

        nearest_pos = size-int(data[0][1])
        nearest_time = 0
        for time, pos in data:
            time,  pos = float(time), int(pos)
            if abs(size-pos) < nearest_pos:
                nearest_pos = abs(size-pos)
                nearest_time = time
        logger.info(f'{size} maps approximately to {nearest_time}')

        return nearest_time


if __name__ == '__main__':
    import time
    starttime = time.time()
    yt = YoutubeHar('/home/nen/PycharmProjects/bachelor_thesis/har_files/youtube_combined_e4_har.json')
    example_segment = yt.segments[0]
    ranger = Ranger(config.YOUTUBE_AWAKENING, 'awakening')
    for segment in yt.segments:
        print(ranger.segment_to_playtime(segment, return_itag=True))
    print(f'time needed: {time.time()-starttime}')