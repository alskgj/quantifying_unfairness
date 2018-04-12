"""
Issue: BT-5

newcommers experiment 1
1. Limit bandwith to 5k
2. Start vimeo first, wait 45 seconds, then start youtube
2. Record har files
3. Display results as graph: bandwith over time
4. Try to explain results

TODO: read timings from har file

Results:
1.
2.
3.
4.
"""

from shaper import Shaper
from extractor import Vimeo, Youtube
from config import VIMEO_AWAKENING, YOUTUBE_AWAKENING
from postprocessor.plotter import plot_combined_bandwidth_vs_time
import logging
import time

logger = logging.getLogger(__name__)

shaper = Shaper()
shaper.limit_download(5000)

NAME = 'vimeo_first_1'

vimeo_extractor = Vimeo(VIMEO_AWAKENING, shaper=shaper, name="vimeo_" + NAME)
youtube_extractor = Youtube(YOUTUBE_AWAKENING, shaper=shaper, name="youtube_" + NAME)

time.sleep(5)
vimeo_extractor.start()
time.sleep(20)
youtube_extractor.start()

vimeo_extractor.join()
youtube_extractor.join()

shaper.reset_ingress()
logger.info(f'Experiment: {NAME} finished')

plot_combined_bandwidth_vs_time(NAME, n=15)


