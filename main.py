# pip install py-cpuinfo selenium

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import os
import sys
import time
import json
import cpuinfo
import platform

getCwd = lambda: os.path.dirname(sys.executable) if hasattr(sys, 'frozen') else os.path.dirname(os.path.realpath(sys.argv[0]))

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

def openTab(driver):
    old_tab = driver.current_window_handle
    driver.execute_script("window.open(\"\", \"_blank\");")
    driver.switch_to_window(driver.window_handles[-1])
    return old_tab

def closeTab(driver, new_tab):
    driver.execute_script("window.close();")
    driver.switch_to_window(new_tab)
    return

def isValidNonioPage( driver ):
    try:
        WebDriverWait( driver, 10 ).until( EC.presence_of_element_located( ( By.ID, "flxContainer" ) ) )
        return True
    except:
        return False

def validPage( driver ):
    for i in range( 5 ):
        if isValidNonioPage( driver ):
            break

        print( "Invalid Page, refreshing." )
        time.sleep( 5 )
        driver.refresh( )

    if not isValidNonioPage( driver ):
        print( "Oops, we got a problem here, check your internet and the website and try again later" )
        time.sleep( 5 )
        driver.quit( )
        exit( 1 )

def signClass( driver, class_name ):
    # codigo por desvendar
    return True

def getBinaryPath():
    is_64bits = sys.maxsize > 2**32

    if platform.system() == "Windows":
        return "{}\\geckodriver (Windows x{}).exe".format( getCwd( ), "64" if is_64bits else "86" )
    elif platform.system() == "Linux":
        return "{}\\geckodriver (Linux x{}).exe".format( getCwd( ), "64" if is_64bits else "86" )
    
    return "{}\\geckodriver (MacOS - {}).exe".format( getCwd( ), "M1" if "m1" in cpuinfo.get_cpu_info( ).get( "brand_raw" ).lower( ) else "Intel" )

mostraASCII()
data = lerFicheiro()
password = pedeCredenciais(data["numero_aluno"])
print(lerFicheiro())
binary = FirefoxBinary( getBinaryPath( ) )
driver = webdriver.Firefox( firefox_binary=binary )
driver.get("https://inforestudante.ipc.pt/nonio/security/login.do")
assert "InforEstudante - NONIO IPC" in driver.title

email_input = driver.find_element(By.ID, "username")
email_input.click()
email = "a" + data["numero_aluno"] + "@isec.pt"
for letter in email:
    email_input.send_keys(letter)
    
password_input = driver.find_element(By.ID, "password1")
password_input.click()
for letter in password:
    password_input.send_keys(letter)

login = driver.find_element(By.CLASS_NAME, "button")
login.click()

if not isValidNonioPage( driver ):
    print( "Error logging in. Please check your credentials and try again." )
    time.sleep( 5 )
    driver.quit( )
    exit( 1 )

driver.get("https://inforestudante.ipc.pt/nonio/inscturmas/listaInscricoes.do")

validPage( driver )

subject_table = driver.find_element(By.ID, "displaytable").find_element_by_tag_name( "tbody" )
for subject_row in subject_table.find_elements_by_css_selector( "tr" ):
    for subject_info in data[ "cadeiras" ]:
        if not subject_info[ "nome" ] in subject_row.text:
            continue
        
        link = subject_row.find_element_by_class_name( "botaodetalhes" ).href
        original_tab = openTab( driver )

        driver.get( link )

        validPage( driver )

        for subject_class in subject_info[ "teorica" ]:
            if signClass(driver, subject_class):
                break
        
        for subject_class in subject_info[ "pratica" ]:
            if signClass(driver, subject_class):
                break

        # submit btn se bem me lembro

        closeTab( driver, original_tab )
