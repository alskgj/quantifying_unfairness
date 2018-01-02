from browsermobproxy import Server
from selenium import webdriver

from youtube_helper import check_video_status, VIDEO_ENDED, VIDEO_PAUSED, VIDEO_PLAYING
from json import dumps

from config import PROXY_EXECUTABLE, FIREFOX_EXECUTABLE, SELENIUM_LOGS, LOG_DIR, HAR_DIR

import logging
logger = logging.getLogger(__name__)
import os

import atexit
import time


class Experiment:
    server = Server(PROXY_EXECUTABLE)
    server.start({'log_path': LOG_DIR, 'log_file': 'server.log'})

    def __init__(self, video_url, har_folder=HAR_DIR, upload_kbps=None, download_kbps=None):
        self.video_url = video_url
        self.har_folder = har_folder
        self.proxy = self.server.create_proxy()

        # setting up/download limits
        proxy_limits = {}
        if upload_kbps:
            proxy_limits['upstream_kbps'] = upload_kbps
        if download_kbps:
            proxy_limits['downstream_kbps'] = download_kbps
        if proxy_limits:
            self.proxy.limits(proxy_limits)

        # setting up selenium
        profile = webdriver.FirefoxProfile()
        profile.set_proxy(self.proxy.selenium_proxy())
        self.driver = webdriver.Firefox(firefox_profile=profile, executable_path=FIREFOX_EXECUTABLE, log_path=SELENIUM_LOGS)

    def run_youtube(self, har_identifier='test', cleaning_func=None, youtube_fullscreen=False):
        """This is a blocking function! - if you want to run multiple experiments at the same time,
        implement non-blocking run"""
        # for options see https://github.com/lightbody/browsermob-proxy/blob/master/README.md
        self.proxy.new_har(har_identifier, options={'captureHeaders': True})
        self.driver.get(self.video_url)

        # blocks until video is stopped/paused
        while True:
            status = check_video_status(self.driver)
            if status == VIDEO_PLAYING and youtube_fullscreen:
                elem = self.driver.find_element_by_id('movie_player')
                elem.send_keys('f')
                youtube_fullscreen = False
                logging.info('Sending f to youtube (should toggle fullscreen)')

            if status == VIDEO_ENDED or status == VIDEO_PAUSED:
                break
            time.sleep(0.5)

        har = self.proxy.har
        if cleaning_func:
            har = cleaning_func(har)

        with open(os.path.join(self.har_folder, har_identifier+'.har'), 'w+') as fo:
            fo.write(dumps(har))
            logger.info('Saved har file to: %s' % os.path.join(self.har_folder, har_identifier+'.har'))
        return har

    def run_generic(self, har_identifier='test', cleaning_func=None):
        # for options see https://github.com/lightbody/browsermob-proxy/blob/master/README.md
        self.proxy.new_har(har_identifier, options={'captureHeaders': True, 'captureContent': True})
        self.driver.get(self.video_url)

        # blocks until key is pressed
        input('press a key to confirm video finished')

        har = self.proxy.har
        if cleaning_func:
            har = cleaning_func(har)

        with open(os.path.join(self.har_folder, har_identifier+'.har'), 'w+') as fo:
            fo.write(dumps(har))
            logger.info('Saved har file to: %s' % os.path.join(self.har_folder, har_identifier+'.har'))
        return har

    def __del__(self):
        self.driver.quit()

    @staticmethod
    def cleanup():
        Experiment.server.stop()


atexit.register(Experiment.cleanup)
