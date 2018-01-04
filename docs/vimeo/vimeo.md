Vimeo - 30.12.2017
===

I discuss my findings while disecting a single videoplayback on vimeo on 30.12.2017.
The played video can be found on https://vimeo.com/166807261.

#### config.json

First a GET request is made to https://player.vimeo.com/video/<video_id>/config with several arguments passed.
An observed invocation had this format (some arguments where removed to shorten the url): 
https://player.vimeo.com/video/166807261/config?autopause=1&byline=0&collections=1&default_to_hd=1&outro=nothing

The response to this is json file which holds information about the video to be played.
Notable:
- Urls on how to get the 'master.json' file (covered later) for different streaming categories.
At the time of writting this the categories are 'dash', 'hls' and 'progressive'.
- Information seemingly needed for ab-testing:
```json
    "ab_tests": {
      "manifest_retry": {
        "data": {
          "duration": 2000
        },
        "group": true
      },
      "loading_animation": {
        "data": {},
        "group": "none"
      }
    }
```
- Information about the video (duration, thumbnail pictures, file codecs, ...)
- Information about the author and the context (settings, if the video is embedded, badges, ...)

#### master.json

After receiving the discussed json file (which I call config.json)
a request is made to one of the cdn-urls contained in the config.json to get the master.json file.

Contained in the master.json file are details about the different segments. In particular the url for the desired resolution is given.

The urls to get the segments start with the same part as the url to get the master.json file and appended to it is a parameter contained
in the master.json file called base url (example: "base_url":"902358530/chop/") this is specific to a resolution,
appended to it is an affix specific to the segment (exampl"url":"segment-14.m4s").
Example for a built url:
https://56skyfiregce-vimeo.akamaized.net/longidhere/248996255/sep/video/902358530/chop/segment-1.m4s