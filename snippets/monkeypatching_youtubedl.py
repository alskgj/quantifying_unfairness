import youtube_dl
import sys

video_id = 'iKXd9zW1OuI'

# simulating regular input (same as python -m youtube_dl <video_id>) downloads video found on youtube with id=<video_id)
sys.argv.append(video_id)
youtube_dl.main()

