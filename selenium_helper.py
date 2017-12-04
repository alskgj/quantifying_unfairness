from browsermobproxy import Server
from selenium import webdriver

from youtube_helper import check_video_status, VIDEO_ENDED, VIDEO_PAUSED
from json import dumps

from config import PROXY_EXECUTABLE, FIREFOX_EXECUTABLE, SELENIUM_LOGS, LOG_DIR, HAR_DIR
from datetime import datetime
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

    def run(self, har_identifier='test'):
        """This is a blocking function! - if you want to run multiple experiments at the same time,
        implement non-blocking run"""
        # for options see https://github.com/lightbody/browsermob-proxy/blob/master/README.md
        self.proxy.new_har(har_identifier, options={'captureHeaders': True})
        self.driver.get(self.video_url)

        # blocks until video is stopped/paused
        while True:
            status = check_video_status(self.driver)
            if status == VIDEO_ENDED or status == VIDEO_PAUSED:
                break
            time.sleep(0.5)

        timestamp_now = int(datetime.now().timestamp())
        with open(os.path.join(self.har_folder, str(timestamp_now)+'.har'), 'w+') as fo:
            fo.write(dumps(self.proxy.har))

    def __del__(self):
        self.driver.quit()

    @staticmethod
    def cleanup():
        Experiment.server.stop()


atexit.register(Experiment.cleanup)
