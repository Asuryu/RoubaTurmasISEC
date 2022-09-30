# pip install bs4 lxml requests pillow
import json
import requests
import threading
from enum import Enum
from getpass import getpass
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from PIL import Image
from io import BytesIO
from datetime import datetime
from datetime import timedelta
import time
import difflib

class ClassesType(Enum):
    practice = 1
    theoric = 2
    theoric_practice = 3


config = json.load(open("config.json", encoding="utf-8"))

s = requests.Session()

izek_adapter = HTTPAdapter(max_retries=10)
s.mount("https://{}".format(config["domain"]), izek_adapter)

# inserir jsessionid token depois metemos login e deixamos isto mais bonito
# jsessionid_token = ""
# s.cookies.set("JSESSIONID", jsessionid_token, domain=config["domain"])

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


def subscribeClass(href, class_info):
    print("[ + ] Subscribing {}".format(class_info["name"]))

    r = get(href)
    soup = BeautifulSoup(r.text, "lxml")
    table_elems = soup.find("form", attrs={"id": "inscreverFormBean"}).find("table").findChildren("tr", recursive=False)
    
    payload = { "inscrever": [] }
    for i in range(1, 4 if class_info["theoric_practice"] else 3):
        try:
            classes_elems = table_elems[i].find("table", attrs={"class": "displaytable"}).find("tbody").findChildren("tr")
        except:
            print ("[ ! ] There doesn't seem to be any available spots in any class")
            break        
        
        classes_list = {}
        for class_elem in classes_elems:
            info_elems = class_elem.findChildren('td')
            class_name = info_elems[0].text
            class_full = int(info_elems[3].text) == 0
            class_value = int(info_elems[4].find("input")["value"])

            class_subscribed = False
            try:
                class_subscribed = info_elems[5].find("input")["checked"] == "checked"
                classes_list[class_name] = [class_value, class_full, class_subscribed]
            except:
                classes_list[class_name] = [class_value, class_full, class_subscribed]
                continue


        for target_class in class_info[ClassesType(i).name]:
            print("[ + ] Checking {} status".format(target_class))

            try:
                if not classes_list[target_class][1] or classes_list[target_class][2]:
                    payload["inscrever"].append(classes_list[target_class][0])
                    break
            except KeyError:
                print("[ ! ] Class {} not found".format(target_class))
                continue


            print("[ ! ] {} is full, trying the next one".format(target_class))
    
    r = post("{}/inscrever.do?method=submeter".format(subscribe_href), payload)

    print("[ + ] Subscription in {} completed!".format(class_info["name"]))
    return True

def login(user, auto=False, password="", captcha=None):
    while True:
        if (not auto):
            if (config["password"] == ""):
                password = getpass()
            else:
                password = config["password"]
        if captcha:
            data = { "tipoCaptcha": "text", "username": user, "password": password, "captcha": captcha }
        else:
            data = { "tipoCaptcha": "text", "username": user, "password": password }
        r = post("https://{}/nonio/security/login.do?method=submeter".format(config["domain"]), data)
        soup = BeautifulSoup(r.text, 'html.parser') # parse the html so we can inspect it
        error1 = soup.find("div", {"id": "div_erros_preenchimento_formulario"})

        if 'class="captchaTable"' in r.text:
            print("[ ! ] Captcha detected")
            response = get("https://inforestudante.ipc.pt/nonio/simpleCaptchaImg")
            img = Image.open(BytesIO(response.content))
            img.show()
            captcha = input("[ ? ] Enter the captcha you see: ")
            data = { "tipoCaptcha": "text", "username": user, "password": password, "captcha": captcha }
            r = post("https://{}/nonio/security/login.do?method=submeter".format(config["domain"]), data)
            soup = BeautifulSoup(r.text, 'html.parser') # parse the html so we can inspect it
            error2 = soup.find("div", {"id": "div_erros_preenchimento_formulario"})

            if error2 is None: # if no red error div found
                print("[ + ] Login successful")
                break
            else:
                print("[ ! ] " + error2.get_text())
                print("[ ? ] Captcha recieved: |"+ captcha + "|")
                password = getpass() # ask for password again instead of using the one in config.json (use could've mistyped it in the config file)
                login(user, auto=True, password=password, captcha=captcha)
                break # This break statement seems useless but it works so yeah :P
            
        else:
            if error1 is None: # if no red error div found
                print("[ + ] Login successful")
                break
            else:
                print("[ ! ] " + error1.get_text())
                auto = False

    return password

def seconds_left_to_run():
    FMT = '%H:%M:%S'
    tdelta = datetime.strptime(format(config["time_to_run"]), FMT) - datetime.now()
    if tdelta.days < 0:
        tdelta = timedelta(
            days=0,
            seconds=tdelta.seconds,
            microseconds=tdelta.microseconds
        )
        return tdelta.total_seconds().__round__()
    

password = login("{}@isec.pt".format(config["student_number"]))

if format(config["time_to_run"]) != "" :
    print ("[ ? ] The script will run at {} and will login again two minutes before".format(config["time_to_run"]))
    print("[ ? ] Be here two minutes before the time to make sure the login doesn't fail")
    seconds_left = seconds_left_to_run()
    if (seconds_left - 120 >= 0):
        print(f"[ ? ] {seconds_left - 120} seconds to run login again")
        time.sleep(seconds_left - 120)
        login("{}@isec.pt".format(config["student_number"]), auto=True, password=password)

if format(config["time_to_run"]) != "" :
    seconds_left = seconds_left_to_run()
    if (seconds_left <= 43169): # prevent break when user takes longuer than 60s to login in case of captcha
        print(f"[ ? ] The script will start in {seconds_left} seconds")
        if (seconds_left - 6 >= 0):
            time.sleep(seconds_left - 6)
            print(f"[ ? ] The script will start in", end="")
            time.sleep(1)
            for i in range(5,0,-1):
                print(f" {i}", end="")
                time.sleep(1)
            print()
        else:
            time.sleep(seconds_left)

subscribe_href = "https://{}/nonio/inscturmas".format(config["domain"])
r = get("{}/init.do".format(subscribe_href))

soup = BeautifulSoup(r.text, "lxml")
course_href = soup.find("div", attrs={"id": "link_0"}).find("a")["href"]

r = get("{}/{}".format(subscribe_href, course_href))

soup = BeautifulSoup(r.text, "lxml")
subjects_elems = soup.find("form", attrs={"id": "listaInscricoesFormBean"}).find("table", attrs={"class": "displaytable"}).find("tbody").findChildren("tr")

subjects_list = {}
for subject_elem in subjects_elems:
    info_elems = subject_elem.findChildren('td')
    subject_name = info_elems[1].text.rstrip("\xa0 *")
    subject_href_elem = info_elems[6].find("a")
    if subject_href_elem == None:
        continue
    subject_href = subject_href_elem["href"]
    subject_href = info_elems[6].find("a")["href"]
    subjects_list[subject_name] = "{}/{}".format(subscribe_href, subject_href)

threads_ = []

for class_info in config["classes"]:
    if (class_info["name"] in subjects_list):
        class_name = class_info["name"]
    else:
        class_name = difflib.get_close_matches(class_info["name"], subjects_list, n=1, cutoff=0)[0]
        print ("[ ! ] " + '"' + class_info["name"]+ '"' + " Not Found, Using most similar match: " + '"' + class_name + '"')
        class_info["name"] = class_name
    if subjects_list[class_name]:
        subject_href = subjects_list[class_name]

        subscribeClass(subject_href, class_info)