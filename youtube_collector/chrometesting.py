from time import sleep, clock
from random import choice, randint
from json import dump

from selenium import webdriver
from browsermobproxy import Server
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


# server = Server(config.PROXY_EXECUTABLE)
server = Server(r"C:\Users\zen\Desktop\browsermob-proxy-2.1.4\bin\browsermob-proxy.bat", {'port': 8822})

server.start({'log_path': config.LOG_DIR, 'log_file': 'server.log'})

urls = open('videos.txt').read().split()




url = choice(urls)

browsermob_proxy = server.create_proxy()
driver = new_driver(browsermob_proxy)

browsermob_proxy.new_har('chrometesting.json', options={
    'captureHeaders': True,
    'captureContent': False,
    'captureBinaryContent': False
})

limit = 400_000
print(f'Limiting bandwith to {limit}')
download_limit(driver, limit)
sleep(5)

driver.get(url)
sleep(5)


while True:
    print(f'driver text: {driver.text}')

    status = driver.execute_script("return document.getElementById('movie_player').getPlayerState()")
    print(f'status is: {status}')

    if status == VIDEO_ENDED or status == VIDEO_PAUSED:
        print('videoplayback ended')
        break

    limit = 5_000
    download_limit(driver, limit)

    print(f'limiting download speed to {limit}')

    sleep(3)



driver.quit()
browsermob_proxy.close()

