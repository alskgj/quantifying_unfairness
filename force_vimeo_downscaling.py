import shaper
import extractor
import time
from har_files import jain
from config import HAR_DIR

s = shaper.Shaper()

v_url = 'https://vimeo.com/channels/staffpicks/257798097'
extractor = extractor.Vimeo(v_url, s)
extractor.start()

time.sleep(30)

start_limit = 10_000
for limit in range(start_limit, 0, -1000):
    print(f'Limited download speed to {limit}kbit/s')
    s.reset_ingress()
    s.limit_download(limit)
    time.sleep(20)

input('press enter to reset dl bandwith')

s.reset_ingress()
print('bandwith reset')
# todo try vimeo mobile version
# todo try to get crash with chrome too
# todo write introduction and stuff

vimeo_bytes = jain.bytes(HAR_DIR+'/vimeo.json')

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

