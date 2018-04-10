import shaper
import extractor
import time
from postprocessor import jain
from config import HAR_DIR

s = shaper.Shaper()

url = 'https://www.youtube.com/watch?v=afRHSmdg0Nk'
v_url = 'https://vimeo.com/channels/staffpicks/257798097'
extractors = [extractor.Youtube(url, s), extractor.Vimeo(v_url, s)]
# extractors = [extractor.Youtube(url, s)]
for extractor in extractors:
    extractor.start()

time.sleep(30)
print('Limited download speed to 1000kbit/s')
s.limit_download(1000)
input('press enter to reset dl bandwith')

s.reset_ingress()
print('bandwith reset')
# todo try vimeo mobile version
# todo try to get crash with chrome too
# todo write introduction and stuff

for extractor in extractors:
    extractor.join()

vimeo_bytes = jain.bytes(HAR_DIR + '/vimeo.json')
youtube_bytes = jain.bytes(HAR_DIR + '/youtube_out.json')

print(f'KBytes downloaded by Vimeo:   {round(vimeo_bytes/1000)}')
print(f'KBytes downloaded by Youtube: {round(youtube_bytes/1000)}')

# both players seem to be really bad

# youtube correctly scales down but
# takes ages (multiple minutes) to scale up again
# interestingly the javascript calls (player.getplaybackquality)
# reacts MUCH fast - as if it reports the parts that are beeing downloaded
# for the future. maybe youtube plays the whole remaining buffer - even if the quality
# is really bad.

# vimeo just never reduces the quality.
# even if the platform has to rebuffer for 10+ seconds it stays on
# 1080p.
# didn't manage to find abr downscale behaviour on vimeo.

