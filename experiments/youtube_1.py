"""
Issue: BT-6

Youtube experiment 1
1. Limit bandwith to 3k
2. Record results (playback characteristics as reported by javascript) and the har file
3. Display results as graph: quality x time -
    with quality as reported by javascript and as seen by inspecting the har file
4. Try to explain results

Problems:
Best way to display results?
Does browsermobproxy work?

Results:
1. Ok
2. Ok - sometimes browsermobproxy crashes
3. Ok
4. Obvious?
"""

import logging

from shaper import Shaper
from extractor import Youtube
from config import YOUTUBE_AWAKENING
from plotter import plot_youtube_quality_vs_time

NAME = 'youtube_e1'

logger = logging.getLogger(__name__)

shaper = Shaper()
shaper.limit_download(3000)

extractor = Youtube(YOUTUBE_AWAKENING, shaper=shaper, name=NAME)
extractor.run()

shaper.reset_ingress()
logger.info(f'Experiment: {NAME} finished')

plot_youtube_quality_vs_time(NAME)

