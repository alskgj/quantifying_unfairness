"""
    baseextractor.py
    ==========

    base class for youtube/vimeo and possibly other extractors
"""

import logging
import os

from selenium import webdriver
from browsermobproxy import Server
import config
import time
from har_helper import youtube_cleaner
from json import dump

from config import HAR_DIR, LOG_DIR


logging.basicConfig(level=logging.INFO)

import threading


class BaseExtractor(threading.Thread):
    server = Server(config.PROXY_EXECUTABLE)

    def __init__(self, url, shaper, browser='firefox', capture_har=True, name=None):
        """
        :param url: A single url or a list of url which will be visited - must be on youtube
        :param shaper: A shaper object
        :param browser: string, firefox or chrome
        """
        self.shaper = shaper
        self.capture_har = capture_har
        self.url = url
        self.experiment_name = name  # self.name is used by Thread superclass internally

        if not capture_har:
            logging.warning('capture_har is set to false and no browsermobproxy will be used.')
        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)

        if self.capture_har:
            self.server.start({'log_path': LOG_DIR, 'log_file': 'server.log'})
            self.proxy = self.server.create_proxy()

        # setup webdriver
        if browser == 'firefox':
            self.driver = self._setup_firefox()
        elif browser == 'chrome':
            self.driver = self._setup_chrome()
        else:
            logging.error(f'{browser} not supported. Use \'firefox\' or \'chrome\'')
            raise NotImplementedError

        # we need to call the superclass, since we are inheriting from threading.Thread
        super(BaseExtractor, self).__init__()

    def _setup_chrome(self):
        options = webdriver.ChromeOptions()
        if self.capture_har:
            options.add_argument(f'--proxy-server=127.0.0.1:{self.proxy.port}')
        options.add_argument('--mute-audio')
        return webdriver.Chrome(
            executable_path=config.CHROME_EXECUTABLE,
            chrome_options=options
        )

    def _setup_firefox(self):
        profile = webdriver.FirefoxProfile()
        if self.capture_har:
            profile.set_proxy(self.proxy.selenium_proxy())

        return webdriver.Firefox(
            firefox_profile=profile,
            executable_path=config.FIREFOX_EXECUTABLE,
            log_path=os.path.join(LOG_DIR, 'geckodriver.log')
        )

    def __enter__(self):
        """support for with statement to cleanup stuff..."""
        # todo does this even work with threads?
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Cleaning up...")

        self.driver.quit()

        if self.capture_har:
            self.proxy.close()



