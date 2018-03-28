from .baseextractor import BaseExtractor
import os.path
from json import dump
import logging
import time
from config import HAR_DIR, VIMEO_EMBED_DIR, OUTPUT_DIR
from jinja2 import Template
from config import VIMEO_TEMPLATE, LOG_DIR

logger = logging.getLogger(__file__)
logger.addHandler(logging.FileHandler(os.path.join(LOG_DIR, 'vimeo_playback.log')))


# todo save shaper information in log file

class Vimeo(BaseExtractor):

    def run(self, capture_content=True, capture_binary_content=False):

        if not self.experiment_name:
            self.experiment_name = 'vimeo'

        self.url = self.embed(self.url)

        if self.capture_har:
            self.proxy.new_har(self.experiment_name, options={
                'captureHeaders': True,
                'captureContent': capture_content,
                'captureBinaryContent': capture_binary_content}
                               )
        logger.info(f'Starting playback of: {self.url}')
        self.driver.get(self.url)
        starttime = time.time()

        # wait until video is paused
        metadata = []
        last_quality = []
        while True:
            time.sleep(1)

            #####################################################
            # detect if videoplayback was paused or ended.
            #####################################################
            paused = self.driver.execute_script('return paused;')
            ended = self.driver.execute_script('return ended;')
            if paused or ended:
                break

            new_quality = self.driver.execute_script('return quality;')
            if new_quality != last_quality:
                current_time = time.time() - starttime
                logger.info(f'{round(current_time, 2)} Quality: {new_quality}')
                metadata.append({
                    'time': round(current_time, 2),
                    'quality': new_quality,
                    'bandwith': self.shaper.download_limit
                })
                last_quality = new_quality

        # video has ended
        metadata.append({
            'time': round(time.time() - starttime, 2),
            'quality': last_quality,
            'bandwith': self.shaper.download_limit
        })

        # playback has ended - save har and metadata
        filename = f'{OUTPUT_DIR}/{self.experiment_name}_metadata.json'
        with open(filename, 'w+') as fo:
            dump(metadata, fo)
        logger.info(f'dumped metadata file to: {filename}')

        if self.capture_har:
            # save the har
            har = self.proxy.har

            filename = f'{HAR_DIR}/{self.experiment_name}_har.json'
            with open(filename, 'w+') as fo:
                dump(har, fo)
            logger.info(f'dumped har file to:      {filename}')
            self.proxy.close()

        self.driver.quit()

    def embed(self, url):
        """Takes a vimeo url and embeds it in a local template, used so we can use the vimeo javascript api.
        :param url: A on vimeo
        :return: A path to a local file which is setup so that the provided url on vimeo
        will be embeded.
        """
        id_ = url.split('/')[-1]
        url = f'https://player.vimeo.com/video/{id_}'

        vimeo_template = Template(open(VIMEO_TEMPLATE).read()).render(url=url)

        file = os.path.join(VIMEO_EMBED_DIR, f'{self.experiment_name}_embed.html')
        with open(file, 'w') as fo:
            fo.write(vimeo_template)

        logger.info(f'embedded {url} in local file {file}')
        return 'file:///'+file

