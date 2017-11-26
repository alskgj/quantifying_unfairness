
VIDEO_ENDED = 0
VIDEO_PLAYING = 1
VIDEO_PAUSED = 2


def check_video_status(driver):
    # https://stackoverflow.com/questions/29706101/youtube-selenium-python-how-to-know-when-video-ends
    player_status = driver.execute_script("return document.getElementById('movie_player').getPlayerState()")

    return player_status
