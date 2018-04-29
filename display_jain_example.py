from postprocessor.har import YoutubeHar
from config import HAR_DIR
from os import path
from postprocessor.util import jain

NAME = '2yt_delayed_long'

hars = [(YoutubeHar(path.join(HAR_DIR, f"youtube_{i}_firefox_" + NAME+'_har.json')),
         YoutubeHar(path.join(HAR_DIR, f"youtube_{i}_chrome_" + NAME+'_har.json')))
        for i in range(4)]

for ff, chrome in hars:
    print(jain([ff, chrome]))
    print(ff.size, chrome.size)
