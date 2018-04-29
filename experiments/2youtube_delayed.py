"""
Running two YouTube instances
Download speed limited to 4k
Delayed by 30 seconds
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

URL = 'https://www.youtube.com/watch?v=w0nbemVmjDI'

youtube_extractor1 = Youtube(YOUTUBE_LONG, shaper=shaper, name="youtube_1_" + NAME)
youtube_extractor2 = Youtube(YOUTUBE_LONG, shaper=shaper, name="youtube_2_" + NAME)

youtube_extractor1.start()

time.sleep(30)

youtube_extractor2.start()

youtube_extractor1.join()
youtube_extractor2.join()

shaper.reset_ingress()
logger.info(f'Experiment: {NAME} finished')
