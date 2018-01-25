from urllib.parse import parse_qs
import requests
import logging
import sys


video_id = input("give me a youtube id please: ")

GET_VIDEO_INFO = 'https://www.youtube.com/get_video_info?video_id='
video_info = parse_qs(requests.get(GET_VIDEO_INFO+video_id).text)

if 'rtmp' in video_info:
    logging.warning('Found rtmp parameter in video_info. Parsing of livestreams not supported.')
    sys.exit(1)
elif 'url_encoded_fmt_stream_map' in video_info or 'adaptive_fmts' in video_info:
    adaptive = list(map(parse_qs, video_info['adaptive_fmts']))[0]
    stream_map = list(map(parse_qs, video_info['url_encoded_fmt_stream_map']))[0]

    print()
    print('Content of adaptive fmts')
    for val, key in adaptive.items():
        print(val, key)

    print()
    print('Content of url encoded fmt stream map')
    for val, key in stream_map.items():
        print(val, key)
