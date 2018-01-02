from selenium_helper import Experiment

vimeo_3min = 'https://vimeo.com/166807261'
e = Experiment(vimeo_3min)
e.run('vimeo_3min', capture_content=True)

