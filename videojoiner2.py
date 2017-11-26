# joining the first two requested segments from https://www.youtube.com/watch?v=BnNIJFK07Vg
# and saving them in combined.webm

with open("michudemo2.webm", "rb") as first:
    with open("michudemo3.webm", "rb") as second:
        with open("combined.webm", "wb") as combined:
            combined.write(first.read()+second.read())



# this works -> each segment in charles is truly a audio/video segment in webm format
# format seems to conform to https://www.matroska.org/technical/specs/index.html#EBMLBasics