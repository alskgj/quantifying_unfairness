import os

# paths
current_path = os.path.dirname(__file__)
PROXY_EXECUTABLE = os.path.join(current_path, "browsermob-proxy-2.1.4/bin/browsermob-proxy")
FIREFOX_EXECUTABLE = os.path.join(current_path, "geckodriver")
CHROME_EXECUTABLE = os.path.join(current_path, "chromedriver")

SELENIUM_LOGS = os.path.join(current_path, 'logs', 'firefox.log')
PROXYSERVER_LOG = os.path.join(current_path, 'logs', 'server.log')

LOG_DIR = os.path.join(current_path, 'logs')
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

# Card Draw & Card Advantage | The Command Zone #127 (55min)
YOUTUBE_LONG = 'https://www.youtube.com/watch?v=w0nbemVmjDI'

# mixtrn.com - Houdini Engine to Unreal Engine Workflow Promo 11:31
YOUTUBE_HOUDINI = 'https://www.youtube.com/watch?v=B7RrPMvLFqI'
VIMEO_HOUDINI = 'https://vimeo.com/255482875'

for path in [HAR_DIR, OUTPUT_DIR, LOG_DIR, CACHE_DIR]:
    if not os.path.exists(path):
        os.mkdir(path)
