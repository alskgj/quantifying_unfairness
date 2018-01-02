from plot_har import plot
from json import load
from har_helper import youtube_cleaner
from glob import glob

for har_file in glob('../har_files/fullscreen_test*'):
    print(har_file)
    plot(youtube_cleaner(load(open(har_file))))