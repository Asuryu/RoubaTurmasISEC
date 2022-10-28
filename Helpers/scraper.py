import json
from enum import Enum
from PIL import Image
from io import BytesIO
from getpass import getpass
from bs4 import BeautifulSoup
from session import get, post
from multiprocessing import Pool, freeze_support

class ClassesType(Enum):
    practice = 1
    theoric = 2
    theoric_practice = 3

config = json.load(open("../config.json", encoding="utf-8"))

def login(email, password):
    data = { "tipoCaptcha": "text", "username": email, "password": password }
    r = post("https://{}/nonio/security/login.do?method=submeter".format(config["domain"]), data=data)

    if r.status_code == 302:
        return True

    if "Utilizador ou palavra-chave inválidos. Por favor, tente novamente." in r.text and not "divCaptcha_text" in r.text:
        return False

    if "divCaptcha_text" in r.text:
        r = get("https://{}/nonio/simpleCaptchaImg".format(config["domain"]))
        img = Image.open(BytesIO(r.content))
        img.show()
        data = { "tipoCaptcha": "text", "username": email, "password": password, "captcha": input("[ ? ] Enter the captcha you see: ") }
        r = post("https://{}/nonio/security/login.do?method=submeter".format(config["domain"]), data)
        if r.status_code == 302:
            return True

    return False

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

def listClasses():
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
    
    return subjects_list

# console version
if __name__ == '__main__':
    freeze_support()

    # enforce security (not storing passwords)
    while True:
        password = getpass()
        email = "{}@isec.pt".format(config["student_number"])

        if login(email, password):
            break

        print("Invalid Username/Password or Captcha")
        
    subjects_list = listClasses()

    with Pool(processes=8) as pool:
        for class_info in config["classes"]:
            if subjects_list[class_info["name"]]:
                subject_href = subjects_list[class_info["name"]]

                # async
                pool.apply_async(subscribeClass, (subject_href, class_info))