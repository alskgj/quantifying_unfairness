"""
    constants
    ~~~~~~~~~

    we call them constants but google changes stuff often,
    so some of them will need updating...
"""

#   youtube itag lookup table
#   ~~~~~~~~~~~~~~~~~~~
#
#   data from http://www.genyoutube.net/formats-resolution-youtube-videos.html

RESOLUTIONS = [144, 240, 360, 480, 720, 1080]

# DASH MP4 video, no audio
itag_mp4_to_resolution = {
    133: 240,
    134: 360,
    135: 480,
    136: 720,
    137: 1080,
    138: 2160,
    160: 144,
    264: 1440,
    298: '720*60',
    299: '1080*60',
    266: '2160*60'
}


# DASH WEBM video, no audio
itag_webm_to_resolution = {
    242: 240,
    243: 360,
    244: 480,
    245: 480,
    246: 480,
    247: 720,
    248: 1080,
    271: 1440,
    272: 2160,
    302: '2160*60',
    303: '1080*60',
    308: '1440*60',
    315: '2160*60',
    167: 360,
    168: 480,
    218: 480,
    219: 144,
    169: 720,
    170: 1080,
    138: 2160,
    160: 144,
    264: 1440,
    298: '720*60',
    299: '1080*60',
    266: '2160*60',
    278: 144  # from a random github comment on youtube dl, but seems to be true
}

itag_to_resolution = {}
for key in itag_mp4_to_resolution:
    itag_to_resolution[key] = "[mp4]  " + str(itag_mp4_to_resolution[key])
for key in itag_webm_to_resolution:
    itag_to_resolution[key] = "[webm] " + str(itag_webm_to_resolution[key])

itag_to_resolution_num = {}
for key in itag_mp4_to_resolution:
    itag_to_resolution_num[key] = itag_mp4_to_resolution[key]
for key in itag_webm_to_resolution:
    itag_to_resolution_num[key] = itag_webm_to_resolution[key]
