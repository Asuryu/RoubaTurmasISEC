import json
from enum import Enum
from getpass import getpass
from session import get, post
from multiprocessing import Pool, freeze_support

class ClassesType(Enum):
    practice = 1
    theoric = 2
    theoric_practice = 3

config = json.load(open("../config.json", encoding="utf-8"))

def login(email, password):
    data = { "tipoCaptcha": "text", "username": email, "password": password }
    r = post("https://inforestudante.ipc.pt/nonio/security/login.do?method=submeter".format(config["domain"]), data=data)

    print(r.text)

# console version
if __name__ == '__main__':
    freeze_support()

    # enforce security (not storing passwords)
    while True:
        password = getpass()
        email = "{}@isec.pt".format(config["student_number"])

        login(email, password)