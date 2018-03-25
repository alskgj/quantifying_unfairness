"""
    youtube.py
    ==========

    A module abstracting interaction with youtube
"""

import logging
import os
from pprint import pprint

import time
from har_helper import youtube_cleaner
from json import dump

from config import HAR_DIR, LOG_DIR

from .baseextractor import BaseExtractor

logger = logging.getLogger(__file__)
logger.addHandler(logging.FileHandler(os.path.join(LOG_DIR, 'youtube_playback.log')))


class Youtube(BaseExtractor):

    # https://developers.google.com/youtube/iframe_api_reference#Playback_status
    VIDEO_STATES = {
        -1: 'VIDEO_UNSTARTED',
        0: 'VIDEO_ENDED',
        1: 'VIDEO_PLAYING',
        2: 'VIDEO_PAUSED',
        3: 'VIDEO_REBUFFERING'
    }

    VIDEO_UNSTARTED = -1
    VIDEO_ENDED = 0
    VIDEO_PLAYING = 1
    VIDEO_PAUSED = 2
    VIDEO_REBUFFERING = 3

    def run(self, capture_content=False, capture_binary_content=False, har_name='youtube_out',
            clean_har=False):

        if self.capture_har:
            self.proxy.new_har(f"{har_name}", options={
                'captureHeaders': True,
                'captureContent': capture_content,
                'captureBinaryContent': capture_binary_content}
                               )

        logger.info(f'Starting playback of: {self.url}')
        self.driver.get(self.url)

        data = {}
        starttime = time.time()
        last_datapoint = {}
        i = 0

        # waiting for video to start
        while self.status() == self.VIDEO_UNSTARTED:
            time.sleep(1)

        while self.status() not in [self.VIDEO_ENDED, self.VIDEO_PAUSED]:
            datapoint = dict()
            datapoint['status'] = self.VIDEO_STATES[self.status()]
            datapoint['quality'] = self.quality()
            datapoint['total_dl_bandwith'] = self.shaper.download_limit
            if last_datapoint != datapoint:
                last_datapoint = datapoint.copy()
                datapoint['time'] = time.time()-starttime
                logger.info(f'{round(datapoint["time"], 2)} {datapoint["quality"]}')
                data[i] = datapoint
                i += 1

            time.sleep(0.1)

        datapoint = dict()
        datapoint['status'] = self.VIDEO_STATES[self.status()]
        datapoint['quality'] = self.quality() # TODO get current quality
        datapoint['time'] = time.clock()
        data[i] = datapoint

        # pprint(data)
        # save the data
        filename = f'{HAR_DIR}/{har_name}_meta.json'
        with open(filename, 'w+') as fo:
            dump(data, fo)
            logger.info(f'dumped metadata to {filename}')

        # save the har
        if self.capture_har:
            har = self.proxy.har
            if clean_har:
                har = youtube_cleaner(har)

            filename = f'{HAR_DIR}/{har_name}.json'
            with open(filename, 'w+') as fo:
                dump(har, fo)
                logger.info(f'dumped har file to {filename}')

        self.driver.quit()

    def quality(self):
        """Quality of current playback"""
        return self._execute("getPlaybackQuality()")

    def status(self):
        """Status of current playback"""
        # https://stackoverflow.com/questions/29706101/youtube-selenium-python-how-to-know-when-video-ends
        player_status = self._execute("getPlayerState()")
        return player_status

    def duration(self):
        """Duration of current playback"""
        return self._execute("getDuration()")

    def _execute(self, code):
        """executes a javascript"""
        return self.driver.execute_script("return document.getElementById('movie_player')."+code)



