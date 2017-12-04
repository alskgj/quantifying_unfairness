from selenium_helper import Experiment

video_url = "https://www.youtube.com/watch?v=FmsLJHikRf8"
video_url2 = "https://www.youtube.com/watch?v=jEnd8JIMii4"

e = Experiment(video_url2, download_kbps=250, upload_kbps=250)
e.run()



