# script to get a browsermob proxy proxy
# https://github.com/lightbody/browsermob-proxy

import requests

r = requests.post("http://localhost:8080/proxy")
print(r.text)
