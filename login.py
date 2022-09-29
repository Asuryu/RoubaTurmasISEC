# pip install bs4 lxml requests
from asyncio import threads
import json
import requests
import threading
import sys
from enum import Enum
from getpass import getpass
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

s = requests.Session()

izek_adapter = HTTPAdapter(max_retries=10)
s.mount("https://inforestudante.ipc.pt", izek_adapter)

def get(url):
    while True:
        try:
            r = s.get(url, timeout=15)
        except:
            continue

        if r.status_code == 200 or r.status_code == 500:
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

def login(user, password):
    data = { "tipoCaptcha": "text", "username": user, "password": password }
    r = post("https://inforestudante.ipc.pt/nonio/security/login.do?method=submeter", data)

config = json.loads(sys.argv[1])
login(config["student_number"] + "@isec.pt", config["password"])
subscribe_href = "https://inforestudante.ipc.pt/nonio/inscturmas"
r = get("{}/init.do".format(subscribe_href))
if(r.status_code == 500):
    obj = {
        "status": 500,
    }
    print(json.dumps(obj))
    exit(0)
soup = BeautifulSoup(r.text, "lxml")
course_href = soup.find("div", attrs={"id": "link_0"}).find("a")["href"]

r = get("{}/{}".format(subscribe_href, course_href))

soup = BeautifulSoup(r.text, "lxml")
subjects_elems = soup.find("form", attrs={"id": "listaInscricoesFormBean"}).find("table", attrs={"class": "displaytable"}).find("tbody").findChildren("tr")

subjects_list = {
    "cadeiras": []
}
for subject_elem in subjects_elems:
    info_elems = subject_elem.findChildren('td')
    subjects_list["cadeiras"].append(info_elems[1].text.rstrip("\xa0 *"))

print(json.dumps(subjects_list))