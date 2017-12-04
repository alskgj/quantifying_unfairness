from browsermobproxy import Server
from selenium import webdriver

from youtube_helper import check_video_status, VIDEO_ENDED, VIDEO_PAUSED
from json import dumps

from config import PROXY_EXECUTABLE, FIREFOX_EXECUTABLE, SELENIUM_LOGS, LOG_DIR

video_url = "https://www.youtube.com/watch?v=FmsLJHikRf8"


# setting up server - on linux use sh file
server = Server(PROXY_EXECUTABLE)
server.start({'log_path': LOG_DIR, 'log_file': 'server.log'})
proxy = server.create_proxy()
proxy.limits({'upstream_kbps': 100, 'downstream_kbps': 3000})
# setting up selenium

# this does not work and I don't know why.
# driver = webdriver.Firefox(proxy=proxy.selenium_proxy())

# deprecated but works better? :S
profile = webdriver.FirefoxProfile()
profile.set_proxy(proxy.selenium_proxy())
driver = webdriver.Firefox(firefox_profile=profile, executable_path=FIREFOX_EXECUTABLE, log_path=SELENIUM_LOGS)


proxy.new_har("test")
driver.get(video_url)
while True:
    status = check_video_status(driver)
    if status == VIDEO_ENDED or status == VIDEO_PAUSED:
        break

# proxy.har actually returns a json object (and not a harstring) - so if we want to copy it to something like
# http://www.softwareishard.com/har/viewer/ we need to convert it to a harstring
print(dumps(proxy.har))
server.stop()
driver.quit()
