"""
Takes as input multiple har files and calculagtes jains fairness index.
"""
from json import load

def bytes(har_path):
    """Returns the amount of bits downloaded in the har file"""
    har = load(open(har_path))

    return sum([e['response']['headersSize']+
                e['response']['bodySize']
                for e in har['log']['entries']])

# TODO visualize amount of data downloaded
if __name__ == '__main__':
    vimeo = bytes('vimeo.json')
    youtube = bytes('youtube_out.json')
    print(youtube, vimeo)
