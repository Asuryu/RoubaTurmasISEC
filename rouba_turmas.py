import json
import requests
from enum import Enum
from bs4 import BeautifulSoup

class ClassesType(Enum):
    practice = 1
    theoric = 2
    theoric_practice = 3

config = json.load(open("config.json", encoding="utf-8"))

# inserir jsessionid token depois metemos login e deixamos isto mais bonito
jsessionid_token = ""

s = requests.Session()
s.cookies.set("JSESSIONID", jsessionid_token, domain=config["domain"])

def subscribeClass(href, class_info):
    print("[ + ] Subscribing {}".format(class_info["name"]))

    r = s.get( href )
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
            except:
                continue

            classes_list[class_name] = [class_value, class_full, class_subscribed]

        for target_class in class_info[ClassesType(i).name]:
            print("[ + ] Checking {} status".format(target_class))
            
            if not classes_list[target_class][1] or classes_list[target_class][2]:
                payload["inscrever"].append(classes_list[target_class][0])
                break

            print("[ ! ] {} is full, trying the next one".format(target_class))
    
    r.status_code = 0
    while r.status_code != 200:
        r = s.post("{}/inscrever.do?method=submeter".format(subscribe_href), data=payload, timeout=None)

    print("[ + ] Subscription Completed!")
    return True

subscribe_href = "https://{}/nonio/inscturmas".format(config["domain"])
r = s.get("{}/init.do".format(subscribe_href))

soup = BeautifulSoup(r.text, "lxml")
course_href = soup.find("div", attrs={"id": "link_0"}).find("a")["href"]

r = s.get("{}/{}".format(subscribe_href, course_href))

soup = BeautifulSoup(r.text, "lxml")
subjects_elems = soup.find("form", attrs={"id": "listaInscricoesFormBean"}).find("table", attrs={"class": "displaytable"}).find("tbody").findChildren("tr")

subjects_list = {}
for subject_elem in subjects_elems:
    info_elems = subject_elem.findChildren('td')
    subject_name = info_elems[1].text
    subject_href = info_elems[6].find("a")["href"]

    subjects_list[subject_name] = "{}/{}".format(subscribe_href, subject_href)

for class_info in config["classes"]:
    if subjects_list[class_info["name"]]:
        subject_href = subjects_list[class_info["name"]]

        # separating in function to maybe async this later
        subscribeClass(subject_href, class_info)