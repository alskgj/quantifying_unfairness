import shaper
import extractor
from config import VIMEO_AWAKENING

s = shaper.Shaper(ignore_nonroot=True)

v_url = VIMEO_AWAKENING
s.limit_download(3000)
print('limiting to 3k')

extractor = extractor.Vimeo(v_url, s, capture_har=False)
extractor.start()

input('press enter to reset dl bandwith')
s.reset_ingress()

# todo try to get crash with chrome too
# todo write introduction and stuff
input('Press enter to end script')
