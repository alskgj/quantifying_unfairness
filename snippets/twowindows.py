"""
I need to have two windows open with the same driver, to limit bandwith for both of them -- does this work?
how can I position them both and tell them both to go fullscreen?
"""

from config import CHROME_EXECUTABLE
from selenium import webdriver
driver = webdriver.Chrome(CHROME_EXECUTABLE)

url = 'https://stackoverflow.com/questions/3816073/in-a-multi-monitor-display-environment-how-do-i-tell-selenium-which-display-to'

driver.get(url)
while True:
    limit = int(input('limit to: '))
    driver.set_network_conditions(
        latency=0,
        download_throughput=limit,
        upload_throughput=limit
    )
