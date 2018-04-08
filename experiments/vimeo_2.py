"""
Vimeo experiment 2
We try to limit the bandwith to different values to force frequent quality changes.
Used to determine if getVideoHeight() and getVideoWidth() from Vimeos api returns the current quality being played
or the current quality that is being downloaded right now.

Results:
"""

from shaper import Shaper
from extractor import Vimeo
from config import VIMEO_AWAKENING
import logging
from plotter import plot_vimeo_quality_vs_time
import time

logger = logging.getLogger(__name__)

limit = 3000

shaper = Shaper()
shaper.limit_download(limit)

name = 'vimeo_e2'

extractor = Vimeo(VIMEO_AWAKENING, shaper=shaper, name=name)
extractor.start()

for i in range(30):
    time.sleep(10)
    limit += 1000
    shaper.limit_download(limit)

    if not extractor.is_alive():
        break

shaper.reset_ingress()
logger.info(f'Experiment: {name} finished')

plot_vimeo_quality_vs_time(name)

