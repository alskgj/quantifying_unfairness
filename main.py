from selenium_helper import Experiment
from har_helper import youtube_cleaner
from plot_har import plot

import logging
logging.basicConfig(level=logging.INFO)

long_video_url = "https://www.youtube.com/watch?v=DELZ0K_wMjA"
short_video_url = "https://www.youtube.com/watch?v=yXMYqPr5zvc"
ramsey_test = 'https://www.youtube.com/watch?v=wHRXUeVsAQQ'

captures = []
for quality in range(50, 300, 50):
    e = Experiment(ramsey_test, download_kbps=quality, upload_kbps=quality)
    capture = e.run_youtube(cleaning_func=youtube_cleaner, har_identifier="fullscreen_test" + str(quality), youtube_fullscreen=True)
    captures.append(capture)

for capture in captures:
    plot(capture)

