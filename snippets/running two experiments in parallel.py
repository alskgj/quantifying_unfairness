from selenium_helper import Experiment
from threading import Thread


vimeo_url = 'https://vimeo.com/247589072'
youtube_url = 'https://www.youtube.com/watch?v=-HMU3REMJww'

e1 = Experiment(vimeo_url, upload_kbps=200, download_kbps=200)
e2 = Experiment(youtube_url, upload_kbps=200, download_kbps=200)

t1 = Thread(target=e1.run, args=('vimeo_parallel', True, True))
t2 = Thread(target=e2.run, args=('youtube_parallel',))

t1.start()
t2.start()

t1.join()
t2.join()