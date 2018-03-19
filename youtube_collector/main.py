from time import sleep, clock
from random import choice, randint
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

    profile.set_preference("media.volume_scale", "0.0")

    driver = webdriver.Firefox(
        firefox_profile=profile,
        executable_path=config.FIREFOX_EXECUTABLE,
        log_path=config.SELENIUM_LOGS
    )

    return driver


VIDEOS_TO_COLLECT = 50

# server = Server(config.PROXY_EXECUTABLE)
server = Server(config.PROXY_EXECUTABLE, {'port': 8822})

server.start({'log_path': config.LOG_DIR, 'log_file': 'server.log'})

urls = open('videos.txt').read().split()

metadata = dict()
startnum = int(input("number of the first file: "))

for i in range(startnum, startnum+VIDEOS_TO_COLLECT):
    url = choice(urls)



    browsermob_proxy = new_proxy(server)


    driver = new_driver(browsermob_proxy)

    browsermob_proxy.new_har(str(i) + '.json', options={
        'captureHeaders': True,
        'captureContent': False,
        'captureBinaryContent': False}
                             )

    driver.get(url)
    limits = list()

    limit = randint(1, 80)
    download_limit(browsermob_proxy, limit)
    print(f'limited to {limit}')
    sleep(5)

    t = clock()
    limits.append((round(clock() - t), limit))

    while True:
        print(driver.execute_script("return document.getElementById('movie_player').getVideoLoadedFraction()"))
        status = check_video_status(driver)
        if status == VIDEO_ENDED or status == VIDEO_PAUSED:
            print('videoplayback ended')
            break

        # limit with probability 10% -- we don't want to limit too often since browsermobproxy seems to break then
        if not randint(0, 100):
            limit = randint(0, 80)
            download_limit(browsermob_proxy, limit)
            limits.append((round(clock()-t), limit))
            print(f'limiting download speed to {limit} at time {round(clock()-t)}')

        sleep(0.3)

    with open('har_files/'+str(i)+'.json', 'w+') as fo:
        dump(browsermob_proxy.har, fo)
    with open('har_files/'+str(i)+'_metadate.json', 'w+') as fo:
        dump({'url': url, 'limits': limits}, fo)

    driver.quit()
    browsermob_proxy.close()

print(metadata)
with open('har_files/metadata.json', 'w+') as fo:
    dump(metadata, fo)
