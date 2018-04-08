import os.path

# paths
current_path = os.path.dirname(__file__)
PROXY_EXECUTABLE = os.path.join(current_path, "browsermob-proxy-2.1.4/bin/browsermob-proxy")
FIREFOX_EXECUTABLE = os.path.join(current_path, "geckodriver")
CHROME_EXECUTABLE = os.path.join(current_path, "chromedriver")

LOG_DIR = os.path.join(current_path, 'logs')
SELENIUM_LOGS = os.path.join(current_path, 'logs', 'firefox.log')
PROXYSERVER_LOG = os.path.join(current_path, 'logs', 'server.log')

HAR_DIR = os.path.join(current_path, 'har_files')
OUTPUT_DIR = os.path.join(current_path, 'output')
CACHE_DIR = os.path.join(current_path, 'cache')

VIMEO_TEMPLATE = os.path.join(current_path, 'vimeo_embed_template.html')
VIMEO_EMBED_DIR = OUTPUT_DIR

# traffic shaping
NETWORK_INTERFACE = 'eno1'

# videos

# awakening is a 4:26 long video supporting resolutions from 144p (yt) / 270p (vim) up to 4k
YOUTUBE_AWAKENING = 'https://www.youtube.com/watch?v=6D-A6CL3Pv8'
VIMEO_AWAKENING = 'https://vimeo.com/93003441'

