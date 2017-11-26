from browsermobproxy import Server
from selenium import webdriver

import os
from os.path import join

from youtube_helper import check_video_status, VIDEO_ENDED, VIDEO_PAUSED

video_url = "https://www.youtube.com/watch?v=eqx41r6H9OU"

# setting up server
server = Server(join(os.getcwd(), "browsermob-proxy-2.1.4/bin/browsermob-proxy.bat"))
server.start()
print(server)
proxy = server.create_proxy()
print(proxy)

# setting up selenium

# this does not work and I don't know why. Also there is a typo in this class...
# driver = webdriver.Firefox(proxy=proxy.selenium_proxy())

# deprecated but works better? :S
profile = webdriver.FirefoxProfile()
profile.set_proxy(proxy.selenium_proxy())
driver = webdriver.Firefox(firefox_profile=profile)


proxy.new_har("test")
driver.get(video_url)
while True:
    status = check_video_status(driver)
    if status == VIDEO_ENDED or status == VIDEO_PAUSED:
        break

from json import loads, dumps
print(dumps(proxy.har))
server.stop()
driver.quit()
# return document.getElementById('movie_player').getPlayerState()