from time import sleep, clock
from random import choice, randint
from json import dump

from selenium import webdriver
from browsermobproxy import Server
import requests
import config
from youtube_helper import check_video_status, VIDEO_PAUSED, VIDEO_ENDED


def download_limit(driver, amount):
    driver.set_network_conditions(
        offline=False,
        latency=0,
        download_throughput=amount,
        upload_throughput=amount

    )


def new_driver(proxy):
    options = webdriver.ChromeOptions()
    options.add_argument(f'--proxy-server=127.0.0.1:{proxy.port}')
    options.add_argument('--mute-audio')
    driver = webdriver.Chrome(executable_path=config.CHROME_EXECUTABLE,
                              chrome_options=options)
    return driver


VIDEOS_TO_COLLECT = 50

# server = Server(config.PROXY_EXECUTABLE)
server = Server(r"C:\Users\zen\Desktop\browsermob-proxy-2.1.4\bin\browsermob-proxy.bat", {'port': 8822})

server.start({'log_path': config.LOG_DIR, 'log_file': 'server.log'})

urls = open('videos.txt').read().split()

metadata = dict()
startnum = int(input("number of the first file: "))

for i in range(startnum, startnum+VIDEOS_TO_COLLECT):
    url = choice(urls)

    browsermob_proxy = server.create_proxy()
    driver = new_driver(browsermob_proxy)

    browsermob_proxy.new_har(str(i) + '.json', options={
        'captureHeaders': True,
        'captureContent': False,
        'captureBinaryContent': False
    })

    limit = randint(0, 400_000)
    print(f'Limiting bandwith to {limit}')
    download_limit(driver, limit)
    sleep(5)

    driver.get(url)
    limits = list()

    t = clock()
    limits.append((round(clock() - t), limit))

    while True:

        status = check_video_status(driver)
        if status == VIDEO_ENDED or status == VIDEO_PAUSED:
            print('videoplayback ended')
            break

        # limit with probability 20% -- we don't want to limit too often since browsermobproxy seems to break then
        if not randint(0, 5):
            limit = randint(0, 400_000)
            download_limit(driver, limit)
            limits.append((round(clock()-t), limit))
            print(f'limiting download speed to {limit} at time {round(clock()-t)}')

        sleep(3)

    # save har file and metadata file
    with open('har_files/'+str(i)+'.json', 'w+') as fo:
        dump(browsermob_proxy.har, fo)
    with open('har_files/'+str(i)+'_metadate.json', 'w+') as fo:
        dump({'url': url, 'limits': limits}, fo)

    driver.quit()
    browsermob_proxy.close()


with open('har_files/metadata.json', 'w+') as fo:
    dump(metadata, fo)
