from json import load

from vimeo_har import VimeoHar

data = load(open('../har_files/vimeo_parallel.har'))
VimeoHar(data)

data = load(open('../har_files/youtube_parallel.har'))
entries = data['log']['entries']
size = sum([e['response']['bodySize'] for e in entries if e['response']['bodySize'] > 0])
print(f'loaded ytubehar, with {size} bits downloaded')