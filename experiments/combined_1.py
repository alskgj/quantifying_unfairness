"""
Issue: BT-5

combined experiment 1
1. Limit bandwith to 5k
2. Record har file
3. Display results as graph: bandwith over time
4. Eexplain results
"""

from shaper import Shaper
from extractor import Vimeo, Youtube
from config import VIMEO_AWAKENING, YOUTUBE_AWAKENING
from postprocessor.plotter import *
import logging

logger = logging.getLogger(__name__)

shaper = Shaper()
shaper.limit_download(5000)

NAME = 'combined_e6'

vimeo_extractor = Vimeo(VIMEO_AWAKENING, shaper=shaper, name="vimeo_" + NAME)
youtube_extractor = Youtube(YOUTUBE_AWAKENING, shaper=shaper, name="youtube_" + NAME)

vimeo_extractor.start()
youtube_extractor.start()
vimeo_extractor.join()
youtube_extractor.join()

shaper.reset_ingress()
logger.info(f'Experiment: {NAME} finished')

plot_combined_mb_vs_time(NAME)
plot_combined_bandwidth_vs_time(NAME, n=15)
plot_combined_bandwidth_vs_time_add_youtube_rbuf(NAME, n=15)
plot_combined_quality(NAME)

