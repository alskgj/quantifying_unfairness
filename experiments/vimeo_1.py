"""
Issue: BT-1

Vimeo experiment 1
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

from shaper import Shaper
from extractor import Vimeo
from config import VIMEO_AWAKENING
import logging
from postprocessor.plotter import plot_vimeo_quality_vs_time

logger = logging.getLogger(__name__)

shaper = Shaper()
shaper.limit_download(3000)

name = 'vimeo_e1'

extractor = Vimeo(VIMEO_AWAKENING, shaper=shaper, name=name)
extractor.run()

shaper.reset_ingress()
logger.info('Experiment: vimeo_1 finished')

plot_vimeo_quality_vs_time(name)

