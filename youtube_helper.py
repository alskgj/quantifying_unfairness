
VIDEO_ENDED = 0
VIDEO_PLAYING = 1
VIDEO_PAUSED = 2


def check_video_status(driver):
    # https://stackoverflow.com/questions/29706101/youtube-selenium-python-how-to-know-when-video-ends
    player_status = driver.execute_script("return document.getElementById('movie_player').getPlayerState()")

    return player_status


methods_of_yt = ['cueVideoById', 'loadVideoById', 'cueVideoByUrl', 'loadVideoByUrl', 'playVideo',
                 'pauseVideo', 'stopVideo', 'clearVideo', 'getVideoBytesLoaded', 'getVideoBytesTotal',
                 'getVideoLoadedFraction', 'getVideoStartBytes', 'cuePlaylist', 'loadPlaylist', 'nextVideo',
                 'previousVideo', 'playVideoAt', 'setShuffle', 'setLoop', 'getPlaylist', 'getPlaylistIndex',
                 'getPlaylistId', 'loadModule', 'unloadModule', 'setOption', 'getOption', 'getOptions',
                 'mute', 'unMute', 'isMuted', 'setVolume', 'getVolume', 'seekTo', 'getPlayerState',
                 'getPlaybackRate', 'setPlaybackRate', 'getAvailablePlaybackRates', 'getPlaybackQuality',
                 'setPlaybackQuality', 'getAvailableQualityLevels', 'getCurrentTime', 'getDuration',
                 'addEventListener', 'removeEventListener', 'getVideoUrl', 'getDebugText', 'getVideoEmbedCode',
                 'getVideoData', 'addCueRange', 'removeCueRange', 'setSize', 'getApiInterface', 'destroy',
                 'showVideoInfo', 'hideVideoInfo', 'getMediaReferenceTime', 'getInternalApiInterface', 'getAdState',
                 'isNotServable', 'getUpdatedConfigurationData', 'sendAbandonmentPing', 'setAutonav', 'setAutonavState',
                 'startInteractionLogging', 'channelSubscribed', 'channelUnsubscribed', 'handleExternalCall',
                 'getPresentingPlayerType', 'addInfoCardXml', 'cueVideoByPlayerVars', 'loadVideoByPlayerVars',
                 'preloadVideoByPlayerVars', 'seekBy', 'updatePlaylist', 'updateLastActiveTime', 'updateVideoData',
                 'getPlayerResponse', 'getStoryboardFormat', 'getProgressState', 'getHousebrandProperties',
                 'setPlaybackQualityRange', 'getCurrentPlaylistSequence', 'canPlayType', 'sendVideoStatsEngageEvent',
                 'setCardsVisible', 'handleGlobalKeyDown', 'getAudioTrack', 'setAudioTrack', 'getAvailableAudioTracks',
                 'getMaxPlaybackQuality', 'getUserPlaybackQualityPreference', 'setSizeStyle', 'forceFrescaUpdate',
                 'showControls', 'hideControls', 'getVisibilityState', 'shouldSendVisibilityState',
                 'getVideoContentRect', 'setSafetyMode', 'setFauxFullscreen', 'cancelPlayback',
                 'getVideoStats', 'updateSubtitlesUserSettings', 'getSubtitlesUserSettings',
                 'resetSubtitlesUserSettings', 'isFastLoad', 'isPeggedToLive', 'setMinimized', 'setInline',
                 'getSphericalConfig', 'setSphericalConfig', 'setBlackout', 'onAdUxClicked', 'getPlayerSize',
                 'setGlobalCrop', 'wakeUpControls', 'isMutedByMutedAutoplay', 'getVideoAspectRatio',
                 'setUseFastSizingOnWatch', '__domApi']
