from selenium_helper import Experiment
from har_helper import youtube_cleaner
from plot_har import plot

from har_helper import vimeo_master_json

import logging
logging.basicConfig(level=logging.INFO)

url = 'https://vimeo.com/246869455'

quality = 300

e = Experiment(url, download_kbps=quality, upload_kbps=quality)
har = e.run_generic(har_identifier="vimeo_test" + str(quality))

print(vimeo_master_json(har))



# https://gist.github.com/alexeygrigorev/a1bc540925054b71e1a7268e50ad55cd