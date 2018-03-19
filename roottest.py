import config
from extractor import youtube
from shaper import Shaper

s = Shaper()
url = 'https://www.youtube.com/watch?v=FP9ejX8Q1l0'
with youtube.Youtube(url) as yt:
    yt.run()
print('here')