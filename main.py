from selenium_helper import Experiment
from har_helper import youtube_cleaner
from plot_har import plot

import logging
logging.basicConfig(level=logging.INFO)

long_video_url = "https://www.youtube.com/watch?v=DELZ0K_wMjA"
short_video_url = "https://www.youtube.com/watch?v=yXMYqPr5zvc"
ramsey_test = 'https://www.youtube.com/watch?v=wHRXUeVsAQQ'
need_range_clen = 'https://www.youtube.com/watch?v=IKlFBfT1mJU'


e = Experiment(need_range_clen)
capture = e.run(har_identifier="fulltest", capture_content=True)


