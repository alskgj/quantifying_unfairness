"""
Issue: BT-5

combined experiment 1
1. Limit bandwith to 5k
2. Record har file
3. Display results as graph: bandwith over time
4. Try to explain results


Results:
1.
2.
3.
4.
"""

from shaper import Shaper
from extractor import Youtube
from config import YOUTUBE_LONG

import logging
import time

logger = logging.getLogger(__name__)

shaper = Shaper()
shaper.limit_download(4000)

NAME = '2yt_delayed_long'

URL = 'https://www.youtube.com/watch?v=CZv6DkDap-M'

youtube_extractor1 = Youtube(YOUTUBE_LONG, shaper=shaper, name="youtube_firefox_" + NAME)
youtube_extractor2 = Youtube(YOUTUBE_LONG, shaper=shaper, name="youtube_chrome_" + NAME, browser='chrome')

time.sleep(5)
youtube_extractor1.start()
youtube_extractor2.start()
# stopped at 30:00
youtube_extractor1.join()
youtube_extractor2.join()

shaper.reset_ingress()
logger.info(f'Experiment: {NAME} finished')
