from .baseextractor import BaseExtractor
import os.path
from json import dump
import logging
import time
from config import HAR_DIR
logging.basicConfig(level=logging.INFO)

class Vimeo(BaseExtractor):

    def run(self, capture_content=True, capture_binary_content=False):

        har_name = 'vimeo'
        self.url = self.embed(self.url)

        self.proxy.new_har(har_name, options={
            'captureHeaders': True,
            'captureContent': capture_content,
            'captureBinaryContent': capture_binary_content}
                           )
        self.driver.get(self.url)


        # wait until video is paused

        last_quality = []
        while True:
            time.sleep(1)
            paused = self.driver.execute_script('return paused;')
            if paused:
                break
            # TODO implement breaking on stop
            new_quality = self.driver.execute_script('return quality;')
            if new_quality != last_quality:
                print('Quality:', new_quality)
                last_quality = new_quality


        # save the har
        har = self.proxy.har

        filename = f'{HAR_DIR}/{har_name}.json'
        with open(filename, 'w+') as fo:
            dump(har, fo)
            logging.info(f'dumped har file to {filename}')

        self.driver.quit()

    def embed(self, url):
        id_ = url.split('/')[-1]
        url = f'https://player.vimeo.com/video/{id_}'

        vimeo_template = f"""<iframe src="{url}" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

        <script src="https://player.vimeo.com/api/player.js"></script>
        <script>
            var iframe = document.querySelector('iframe');
            var player = new Vimeo.Player(iframe);
            var paused = false;
            var quality = [];
            
            player.on('progress', function () {{
                Promise.all([player.getVideoWidth(), player.getVideoHeight()]).then(function(dimensions) {{
                    quality = dimensions;
                }});
            }});

            player.on('pause', function() {{
                console.log('paused!');
                paused = true;
            }});
            player.on('play', function() {{
                console.log('started playing!');
                paused = false;
            }});
            
            player.play().then(function() {{}});

        </script>"""

        with open('vimeo_embed.html', 'w') as fo:
            fo.write(vimeo_template)


        return 'file:///'+os.path.realpath('vimeo_embed.html')
