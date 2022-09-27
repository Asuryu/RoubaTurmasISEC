# pip install bs4 lxml requests pillow
from ast import While
from asyncio import threads
import json
import requests
import threading
import concurrent.futures
from enum import Enum
from getpass import getpass
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from PIL import Image
from io import BytesIO

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
        classes_elems = table_elems[i].find("table", attrs={"class": "displaytable"}).find("tbody").findChildren("tr")
        
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

            if not classes_list[target_class][1] or classes_list[target_class][2]:
                payload["inscrever"].append(classes_list[target_class][0])
                break

            print("[ ! ] {} is full, trying the next one".format(target_class))
    
    r = post("{}/inscrever.do?method=submeter".format(subscribe_href), payload)

    print("[ + ] Subscription Completed!")
    return True

def login(user):
    while True:
        password = getpass()
        data = { "tipoCaptcha": "text", "username": user, "password": password }
        r = post("https://{}/nonio/security/login.do?method=submeter".format(config["domain"]), data)
        soup = BeautifulSoup(r.text, 'html.parser') # parse the html so we can inspect it
        error = soup.find("div", {"id": "div_erros_preenchimento_formulario"})

        if error is None: # if no red error div found
            print("[ + ] login successful")
            break
        else:
            print("[ ! ] " + error.get_text())

        if 'class="captchaTable"' in r.text:
            print("[ ! ] Captha detected")
            response = requests.get("https://inforestudante.ipc.pt/nonio/simpleCaptchaImg")
            img = Image.open(BytesIO(response.content))
            img.show()
            captcha = input("Enter the captcha you see: ")
            data = { "tipoCaptcha": "text", "username": user, "password": password, "captcha": captcha }
            r = post("https://{}/nonio/security/login.do?method=submeter".format(config["domain"]), data)
            soup = BeautifulSoup(r.text, 'html.parser') # parse the html so we can inspect it
            error = soup.find("div", {"id": "div_erros_preenchimento_formulario"})

            if error is None: # if no red error div found
                print("[ + ] login successful")
                break
            else:
                print("[ ! ] " + error.get_text())
                print("[ ? ] captcha recieved: |"+ captcha + "|")
                print("[ ? ] Captcha not working yet, try logging in the site and solving the captcha and run the script again")
                exit()

login("{}@isec.pt".format(config["student_number"]))

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
    if subjects_list[class_info["name"]]:
        subject_href = subjects_list[class_info["name"]]

        # separating in function to maybe async this later
        x = threading.Thread(target=subscribeClass, args=(subject_href, class_info))
        threads_.append(x)
        x.start()

for thread in threads_: 
    thread.join()