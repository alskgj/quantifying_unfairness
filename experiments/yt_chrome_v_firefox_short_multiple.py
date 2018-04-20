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

import logging
import time

logger = logging.getLogger(__name__)

shaper = Shaper()

NAME = '2yt_delayed_long'

URLS = [
    'https://www.youtube.com/watch?v=_bMDzCHPXmM',
    'https://www.youtube.com/watch?v=GDkAL65tSQ0',
    'https://www.youtube.com/watch?v=0HOjmAB4WaA',
    'https://www.youtube.com/watch?v=6EhHdS--HBM'
]

for i, url in enumerate(URLS):
    shaper.limit_download(4000)
    youtube_extractor1 = Youtube(url, shaper=shaper, name=f"youtube_{i}_firefox_" + NAME)
    youtube_extractor2 = Youtube(url, shaper=shaper, name=f"youtube_{i}_chrome_" + NAME, browser='chrome')

    time.sleep(5)
    youtube_extractor1.start()
    youtube_extractor2.start()
    # stopped at 30:00
    youtube_extractor1.join()
    youtube_extractor2.join()

    shaper.reset_ingress()
    logger.info(f'Experiment: {NAME} finished')
    time.sleep(10)
