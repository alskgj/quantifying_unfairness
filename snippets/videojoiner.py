# joining the first two requested segments from https://www.youtube.com/watch?v=BnNIJFK07Vg
# and saving them in combined.webm

with open("first.webm", "rb") as first:
    with open("second.webm", "rb") as second:
        with open("combined.webm", "wb") as combined:
            combined.write(first.read()+second.read())

with open("videoplayback_audio1.webm", "rb") as first:
    with open("videoplayback_audio2.webm", "rb") as second:
        with open("combined_audio.webm", "wb") as combined:
            combined.write(first.read()+second.read())

# this works -> each segment in charles is truly a audio/video segment in webm format
# format seems to conform to https://www.matroska.org/technical/specs/index.html#EBMLBasics
