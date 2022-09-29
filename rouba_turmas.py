# pip install bs4 lxml requests pillow
import json
import requests
import threading
from enum import Enum
from getpass import getpass
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from multiprocessing import Pool, freeze_support
from PIL import Image
from io import BytesIO
from datetime import datetime
from datetime import timedelta
import time
import difflib

# inserir jsessionid token depois metemos login e deixamos isto mais bonito
# jsessionid_token = ""
# s.cookies.set("JSESSIONID", jsessionid_token, domain=config["domain"])

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

if __name__ == '__main__':
    freeze_support()

    password = getpass()
    login("{}@isec.pt".format(config["student_number"]), password)

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
        subject_name = info_elems[1].text
        subject_href = info_elems[6].find("a")["href"]

        subjects_list[subject_name] = "{}/{}".format(subscribe_href, subject_href)

    print( subjects_list )

    with Pool(processes=8) as pool:
        for class_info in config["classes"]:
            if subjects_list[class_info["name"]]:
                subject_href = subjects_list[class_info["name"]]

                # async
                pool.apply_async(subscribeClass, (subject_href, class_info))