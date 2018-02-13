"""
During testing I found out, that while downloading there is an url for each segment of a youtube video.
Included in this url is a parameter called 'signature'. However I found two different requests with the same signature!

Testing revealed, that we can change another parameter 'range' and the url is still valid.

Hypothesis: Signature is a hash of _some_ of the params in the url.
In this file I try to test all interesting params and test if the url is still valid.
"""

from urllib.parse import urlparse, parse_qs
import requests

# this is a sample url I got while
URL = 'https://r5---sn-4g5e6nlk.googlevideo.com/videoplayback?c=WEB&keepalive=yes&pl=16&itag=244&mime=video%2Fwebm&signature=14FE7CE2B026DC2B82D7AE9CF538EFC820AAABD7.39682833AF078615370D34194C4ED256AF0D21B8&mm=31%2C26&sparams=aitags%2Cclen%2Cdur%2Cei%2Cgir%2Cid%2Cinitcwndbps%2Cip%2Cipbits%2Citag%2Ckeepalive%2Clmt%2Cmime%2Cmm%2Cmn%2Cms%2Cmv%2Cpl%2Crequiressl%2Csource%2Cexpire&ipbits=0&id=o-AD6yUysIMw63BOVR7SZFUx8E6kbLA87Dt_rcgCY0NyML&initcwndbps=1401250&source=youtube&fvip=5&lmt=1517864652534792&key=yt6&ip=77.56.138.110&expire=1518546947&dur=1390.388&requiressl=yes&mv=m&mt=1518525253&ms=au%2Conr&ei=o9uCWrbfJJ-A1gKBsp-wDw&mn=sn-4g5e6nlk%2Csn-h0jeen76&clen=84522484&gir=yes&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C278%2C298%2C299%2C302%2C303&ratebypass=yes&alr=yes&cpn=Vs10W345fM8Sb8m1&cver=2.20180212&range=0-171101&rn=0&rbuf=0'

# hypothesis: I can change: range, rn, rbuf
new_params = dict()
o = urlparse(URL)
for key, val in parse_qs(o.query).items():
    print(f"('{key}', {val}),")
    new_params[key] = val

changes = [
    ('c', ['MP4']),
    ('keepalive', ['no']),
    ('pl', ['12']),
    ('itag', ['247']),
    ('mime', ['video/mp4']),
    ('signature', ['24FE7CE2B026DC2B82D7AE9CF538EFC820AAABD7.39682833AF078615370D34194C4ED256AF0D21B8']),
    ('fvip', ['6']),
    ('lmt', ['1817864652534792']),
    ('expire', ['1518546949']),
    ('dur', ['1390.988']),
    ('clen', ['84522584']),
    ('range', ['0-84522484']),
    ('rn', ['100']),
    ('rbuf', ['100']),
]

changable = []
unchangeable = []
for change in changes:
    key, value = change[0], change[1]
    oldvalue = new_params[key]
    new_params[key] = value

    r = requests.get('https://r5---sn-4g5e6nlk.googlevideo.com/videoplayback', params=new_params, verify=False)
    if r.status_code == 200:
        print(f'Url still valid with changed {key}')
        changable.append(key)
    else:
        print(f'Got status {r.status_code} with changed {key}')
        unchangeable.append(key)
    print(r.url)

    new_params[key] = oldvalue

print(f'Same signature, even if parameter changes: {changable}')
print(f'Different signature: {unchangeable}')
