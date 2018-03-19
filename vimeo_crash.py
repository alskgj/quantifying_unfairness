import shaper
import extractor
import time

s = shaper.Shaper()

# not abr enabled v_url = 'https://vimeo.com/126934851'
v_url = 'https://vimeo.com/93003441'
# cv_url = 'https://www.youtube.com/watch?v=afRHSmdg0Nk'
# actually crazy variations with limit = 3k
s.limit_download(3000)
print('limiting to 2.7k')

extractor = extractor.Vimeo(v_url, s)
extractor.start()

time.sleep(30)
input('press enter to reset dl bandwith')
s.reset_ingress()

# todo try to get crash with chrome too
# todo write introduction and stuff
input('Press enter to end script')
