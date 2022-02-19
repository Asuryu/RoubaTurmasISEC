from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import json

def mostraASCII():
    print(R" _____             _        _______                              ")
    print(R"|  __ \           | |      |__   __|                             ")
    print(R"| |__) |___  _   _| |__   __ _| |_   _ _ __ _ __ ___   __ _ ___  ")
    print(R"|  _  // _ \| | | | '_ \ / _` | | | | | '__| '_ ` _ \ / _` / __| ")
    print(R"| | \ \ (_) | |_| | |_) | (_| | | |_| | |  | | | | | | (_| \__ \ ")
    print(R"|_|  \_\___/ \__,_|_.__/ \__,_|_|\__,_|_|  |_| |_| |_|\__,_|___/ ")
    print("")


def pedeCredenciais():
    email = input("Introduz o teu email do ISEC: ")
    while(email == ""):
        email = input("Introduz o teu email do ISEC: ")
    password = input("Introduz a tua password: ")
    while(password == ""):
        password = input("Introduz a tua password: ")
    
    return email, password


def introduzirCadeiras():
    # Ler ficheiro turmas.json e guardar as cadeiras numa lista
    with open("turmas.json", "r") as f:
        turmas = json.load(f)

    cadeiras = []
    for cadeira in turmas["cadeiras"]:
        cadeiras.append(cadeira)

    return cadeiras





mostraASCII()
email, password = pedeCredenciais()
turmas = introduzirCadeiras()
print(introduzirCadeiras())

driver = webdriver.Firefox()
driver.get("https://inforestudante.ipc.pt/nonio/security/login.do")
assert "InforEstudante - NONIO IPC" in driver.title

email_input = driver.find_element("id", "username")
email_input.click()
for letter in email:
    email_input.send_keys(letter)
    
password_input = driver.find_element("id", "password1")
password_input.click()
for letter in password:
    password_input.send_keys(letter)

login = driver.find_element("class name", "button")
login.click()

#driver.get("https://inforestudante.ipc.pt/nonio/inscturmas/listaInscricoes.do")