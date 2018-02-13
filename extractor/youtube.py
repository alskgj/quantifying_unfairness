"""
    youtube.py
    ==========

    A module abstracting interaction with youtube
"""

import logging
from random import choice
from pprint import pprint

from selenium import webdriver
from browsermobproxy import Server
import config
import time
from har_helper import youtube_cleaner
from json import dump

from config import HAR_DIR


logging.basicConfig(level=logging.INFO)

import threading


class Youtube(threading.Thread):
    ACTIVE = 0  # counts how many objects of this class are active, needed for cleanup
    server = Server(config.PROXY_EXECUTABLE)

    VIDEO_STATES = {
        0: 'VIDEO_ENDED',
        1: 'VIDEO_PLAYING',
        2: 'VIDEO_PAUSED',
        3: 'VIDEO_REBUFFERING'
    }
    VIDEO_ENDED = 0
    VIDEO_PLAYING = 1
    VIDEO_PAUSED = 2
    VIDEO_REBUFFERING = 3

    def __init__(self, urls):
        self.ACTIVE += 1
        if self.ACTIVE == 1:
            self.server.start({'log_path': config.LOG_DIR, 'log_file': 'server.log'})

        # allow single url as argument
        if isinstance(urls, str):
            self.urls = [urls]
        self.proxy = self.server.create_proxy()

        # set up chrome
        options = webdriver.ChromeOptions()
        options.add_argument(f'--proxy-server=127.0.0.1:{self.proxy.port}')
        options.add_argument('--mute-audio')
        self.driver = webdriver.Chrome(
            executable_path=config.CHROME_EXECUTABLE,
            chrome_options=options
        )
        super(Youtube, self).__init__()

    def run(self, times=1, capture_content=False, capture_binary_content=False, har_name = 'out'):
        if not times:
            return

        self.proxy.new_har("har name", options={
            'captureHeaders': True,
            'captureContent': capture_content,
            'captureBinaryContent': capture_binary_content}
                           )

        self.driver.get(choice(self.urls))

        data = {}
        time.clock()
        last_datapoint = {}
        i = 0
        while self.status() not in [self.VIDEO_ENDED, self.VIDEO_PAUSED]:
            datapoint = {}
            datapoint['status'] = self.VIDEO_STATES[self.status()]
            datapoint['quality'] = self.quality()
            if last_datapoint != datapoint:
                print(last_datapoint, datapoint)
                last_datapoint = datapoint.copy()
                datapoint['time'] = time.clock()
                data[i] = datapoint
                i += 1

            time.sleep(0.1)

        datapoint = {}
        datapoint['status'] = self.VIDEO_STATES[self.status()]
        datapoint['quality'] = self.quality()
        datapoint['time'] = time.clock()
        data[i] = datapoint

        pprint(data)

        # save the har
        har = self.proxy.har
        har = youtube_cleaner(har)

        filename = f'{HAR_DIR}/{har_name}_{times}.json'
        with open(filename, 'w+') as fo:
            dump(har, fo)
            logging.info(f'dumped har file to {filename}.json')

        self.run(times=times-1)


    def limit(self, amount, latency=0):
        self.driver.set_network_conditions(
            offline=False,
            latency=latency,
            download_throughput=amount,
            upload_throughput=amount
        )

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

    def __enter__(self):
        """support for with statement to cleanup stuff..."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Cleaning up...")

        self.driver.quit()

        self.proxy.close()
        self.ACTIVE -= 1
        if self.ACTIVE == 0:
            logging.info("Stopping server.")
            self.server.stop()


if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=FP9ejX8Q1l0'
    with Youtube(url) as yt:
        yt.run()


