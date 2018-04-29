"""
Issue: BT-5

combined experiment 1
1. Limit bandwith to 5k
2. Record har file
3. Display results as graph: bandwith over time
4. Try to explain results

-> Using chrome
"""

from shaper import Shaper
from extractor import Vimeo, Youtube
from config import VIMEO_AWAKENING, YOUTUBE_AWAKENING
from postprocessor.plotter import *
import logging

logger = logging.getLogger(__name__)

shaper = Shaper()
shaper.limit_download(5000)

NAME = 'combined_e2_chrome'

vimeo_extractor = Vimeo(VIMEO_AWAKENING, shaper=shaper, name="vimeo_" + NAME, browser='chrome')
youtube_extractor = Youtube(YOUTUBE_AWAKENING, shaper=shaper, name="youtube_" + NAME, browser='chrome')

vimeo_extractor.start()
youtube_extractor.start()
vimeo_extractor.join()
youtube_extractor.join()

shaper.reset_ingress()
logger.info(f'Experiment: {NAME} finished')
