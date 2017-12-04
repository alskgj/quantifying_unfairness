from browsermobproxy import Server
from selenium import webdriver

import os
from os.path import join

from youtube_helper import check_video_status, VIDEO_ENDED, VIDEO_PAUSED
from json import dumps

video_url = "https://www.youtube.com/watch?v=FmsLJHikRf8"


# setting up server - on linux use sh file
server = Server(join(os.getcwd(), "browsermob-proxy-2.1.4/bin/browsermob-proxy.bat"))
server.start()
proxy1 = server.create_proxy()
proxy2 = server.create_proxy()

# setting up selenium

# this does not work and I don't know why.
# driver = webdriver.Firefox(proxy=proxy.selenium_proxy())

# deprecated but works better? :S
profile = webdriver.FirefoxProfile()
profile.set_proxy(proxy1.selenium_proxy())
driver1 = webdriver.Firefox(firefox_profile=profile)

profile = webdriver.FirefoxProfile()
profile.set_proxy(proxy2.selenium_proxy())
driver2 = webdriver.Firefox(firefox_profile=profile)


proxy1.new_har("test")
proxy2.new_har("testli")
driver1.get(video_url)
driver2.get("https://www.youtube.com/watch?v=PkOBnYxqj3k")
print(driver1, driver2)
while True:
    status1, status2 = check_video_status(driver1), check_video_status(driver2)
    if status1 == VIDEO_ENDED or status1 == VIDEO_PAUSED:
        if status2 == VIDEO_ENDED or status2 == VIDEO_PAUSED:
            break

# proxy.har actually returns a json object (and not a harstring) - so if we want to copy it to something like
# http://www.softwareishard.com/har/viewer/ we need to convert it to a harstring
print(dumps(proxy1.har))
print(dumps(proxy2.har))
driver1.quit()
driver2.quit()
server.stop()
