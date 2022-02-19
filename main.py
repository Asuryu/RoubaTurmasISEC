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


def lerFicheiro():
    # Ler ficheiro turmas.json e guardar as cadeiras numa lista
    with open("turmas.json", "r") as f:
        data = json.load(f)

    return data
    

def pedeCredenciais(nr_aluno):
    print("ALUNO", nr_aluno)
    password = input("Introduz a tua password: ")
    while(password == ""):
        password = input("Introduz a tua password: ")
    
    return password




mostraASCII()
data = lerFicheiro()
password = pedeCredenciais(data["numero_aluno"])
print(lerFicheiro())

driver = webdriver.Firefox()
driver.get("https://inforestudante.ipc.pt/nonio/security/login.do")
assert "InforEstudante - NONIO IPC" in driver.title

email_input = driver.find_element("id", "username")
email_input.click()
email = "a" + data["numero_aluno"] + "@isec.pt"
for letter in email:
    email_input.send_keys(letter)
    
password_input = driver.find_element("id", "password1")
password_input.click()
for letter in password:
    password_input.send_keys(letter)

login = driver.find_element("class name", "button")
login.click()

time.sleep(10)
driver.close()

#driver.get("https://inforestudante.ipc.pt/nonio/inscturmas/listaInscricoes.do")