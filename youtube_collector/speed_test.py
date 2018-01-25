from time import sleep, clock
from random import choice
from json import dump

from selenium import webdriver
from browsermobproxy import Server

import config
from youtube_helper import check_video_status, VIDEO_PAUSED, VIDEO_ENDED


def download_limit(proxy, limit):
    proxy.limits({'upstream_kbps': limit,
                  'downstream_kbps': limit})


def new_proxy(server):
    proxy = server.create_proxy()
    return proxy


def new_driver(proxy):
    # setting up selenium
    profile = webdriver.FirefoxProfile()
    profile.set_proxy(proxy.selenium_proxy())
    driver = webdriver.Firefox(firefox_profile=profile,
                               executable_path=config.FIREFOX_EXECUTABLE,
                               log_path=config.SELENIUM_LOGS)
    return driver



# server = Server(config.PROXY_EXECUTABLE)
server = Server(r"C:\Users\zen\Desktop\browsermob-proxy-2.1.4\bin\browsermob-proxy.bat", {'port': 8822})

server.start({'log_path': config.LOG_DIR, 'log_file': 'server.log'})

urls = open('videos.txt').read().split()

metadata = dict()


url = choice(urls)

proxy = new_proxy(server)
driver = new_driver(proxy)

proxy.new_har('speedtest.json', options={'captureHeaders': True,
                                         'captureContent': False,
                                         'captureBinaryContent': False})

limit = 200
download_limit(proxy, limit)

driver.get(url)
limits = list()
t = clock()

while True:
    status = check_video_status(driver)
    if status == VIDEO_ENDED or status == VIDEO_PAUSED:
        break

    # toggle limit between 10 and 200
    if limit == 200:
        limit = 10
    else:
        limit = 200

    download_limit(proxy, limit)
    limits.append((clock()-t, limit))

    print(f'limiting download speed to {limit}')

    sleep(30)

with open('har_files/'+'speed_test'+'.json', 'w+') as fo:
    dump(proxy.har, fo)

driver.quit()


# TODO quality variations

print(metadata)
with open('har_files/metadata.json', 'w+') as fo:
    dump(metadata, fo)
