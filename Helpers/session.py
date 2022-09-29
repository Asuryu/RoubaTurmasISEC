import json
import atexit
import pickle
import requests
from requests.adapters import HTTPAdapter

config = json.load(open("../config.json", encoding="utf-8"))

s = requests.Session()
adapter = HTTPAdapter(max_retries=10)
s.mount("https://{}".format(config["domain"]), adapter)

def save():
    with open('cache', 'wb') as f:
        pickle.dump(s.cookies, f)

def load():
    with open('cache', 'rb') as f:
        s.cookies.update(pickle.load(f))

# save and load cookies
if config["save_cookies"]:
    load()
    atexit(save)

def get(url):
    while True:
        try:
            r = s.get(url, timeout=15)
        except:
            continue

        if r.status_code == 200:
            break
    return r

def post(url, data):
    while True:
        try:
            r = s.post(url, data=data, timeout=15)
        except:
            continue

        if r.status_code == 200:
            break
    return r