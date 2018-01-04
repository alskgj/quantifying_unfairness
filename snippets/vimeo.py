from json import loads
import re
from dateutil.parser import parse
from datetime import timedelta


class VimeoHar:
    def __init__(self, har):
        self.entries = har['log']['entries']


        # only successfully downloaded segments
        self.segments = [e for e in self.entries if 'segment' in e['request']['url'] if e['response']['status'] == 200]

        # Trying to save and play video locally fails atm
        # response = [e['response']['content']['text'] for e in self.segments]
        # with open('t1.mp4', 'wb') as fo:
        #     fo.write(response[0].encode())

        self.video_segments()
        size = self.total_size()
        print(f'loaded vimeohar, with {size} bits downloaded')

    def masterjson(self):
        """Returns the master.json file. Only exists in Vimeo Har files.
        """
        for entry in self.entries:
            if 'json' in entry['response']['content']['mimeType'] and 'master.json' in entry['request']['url']:
                return loads(entry['response']['content']['text'])

    def _url_to_resolution(self, url):
        """Takes a vimeo segment url (.../video/id/chop/segment1.pm4) and returns up all relevant info in master.json"""
        pattern = re.compile(r'/(video|audio)/(\d+)/chop')
        id_ = pattern.findall(url)
        if not id_:
            print(f'url {url} does not contain a vimeo id.')
            print(id_)
            return

        result = None
        type_, id_ = id_[0]
        for element in self.masterjson()[type_]:
            if element['id'] == id_:
                result = element
                break

        if not result:
            print(f'no result found for url {url}')
            return

        if type_ == 'audio':
            return f'audio with {result["avg_bitrate"]} average bitrate'
        elif type_ == 'video':
            return f'video with resolution {result["width"]}x{result["height"]}'

    def video_segments(self):
        video_segments_urls = [segment['request']['url'] for segment in self.segments
                              if 'video' in segment['request']['url']]
        result = list()

        for segment in self.segments:
            data = dict()

            data['req_start'] = parse(segment['startedDateTime'])
            data['req_receive'] = data['req_start'] + timedelta(milliseconds=segment['timings']['receive'])
            print(f'Started request at [{data["req_start"]}], received response at [{data["req_receive"]}]')

            result.append(data)

        return result

    def total_size(self):
        return sum([e['response']['bodySize'] for e in self.entries if e['response']['bodySize']>0])



if __name__ == '__main__':
    from json import load
    data = load(open('../har_files/vimeo_parallel1515014752.har'))
    VimeoHar(data)