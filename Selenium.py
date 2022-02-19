import Misc

import os
import time
import requests
from zipfile import ZipFile
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.remote.command import Command
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class Binary:
    def MakeBinaryUndetectable(path):
        readedBytes = None
        with open(path, "rb") as f:
            readedBytes = f.read()

        if readedBytes == None:
            return None
        readedBytes = readedBytes.replace(b'$cdc_', b'$eoqx')

        with open(path, "wb") as f:
            f.write(readedBytes)

        return True

    def GetNewestWebDriver():
        chromeBinary = "{}\\Google\\Chrome\\Application\\chrome.exe".format(os.getenv("PROGRAMFILES(X86)"))
        version = Misc.GetFileVersion(chromeBinary)
        if version == None:
            return None

        version = version.split(".")[0]
        r = requests.get("http://chromedriver.chromium.org/downloads")
        if r.status_code != 200 or not "Downloads - ChromeDriver - WebDriver for Chrome" in r.text:
            return None

        soup = BeautifulSoup(r.content, "lxml")
        linkElems = soup.find("td", attrs={"class": "sites-layout-tile sites-tile-name-content-1"}).find("div").find("div").find_all("li")
        downloadVersion = None
        for link in linkElems:
            if "Chrome version {},".format(version) in link.text:
                downloadVersion = link.find("a")['href'].replace("https://chromedriver.storage.googleapis.com/index.html?path=", "").replace("/", "")

        if downloadVersion == None:
            return None
        downloadLink = "https://chromedriver.storage.googleapis.com/{}/chromedriver_win32.zip".format(downloadVersion)

        r = requests.get(downloadLink)
        with open("{}/chromedriver.zip".format(Misc.GetCwd()), "wb") as f:
            f.write(r.content)

        with ZipFile("{}/chromedriver.zip".format(Misc.GetCwd()), 'r') as chromeZip:
            chromeZip.extractall(Misc.GetCwd())

        Misc.DeleteFile("{}/chromedriver.zip".format(Misc.GetCwd()))

        if Binary.MakeBinaryUndetectable("{}/chromedriver.exe".format(Misc.GetCwd())):
            return version
        return None

class WebDriver:
    def IsValidDriver(driver):
        if driver == None:
            return False
        try:
            driver.execute(Command.STATUS)
        except (socket.error, httplib.CannotSendRequest):
            return False
        return True

    def OpenTab(driver):
        bak = driver.current_window_handle
        driver.execute_script("window.open(\"\", \"_blank\");")
        driver.switch_to_window(driver.window_handles[-1])
        return bak

    def CloseTab(driver, tab):
        driver.execute_script("window.close();")
        driver.switch_to_window(oTab)
        return
    
    def WaitForElementByTag(driver, tag):
        try:
            elementPresence = EC.presence_of_element_located( (By.TAG_NAME, tag) )
            WebDriverWait( driver, 30 ).until(elementPresence)
        except TimeoutException:
            return False
        return True
    
    def IsValidElementById(driver, id):
        try:
            driver.find_element_by_id(id)
        except NoSuchElementException:
            return False
        return True


    def OpenDriver(proxyStr):
        driverOptions = webdriver.ChromeOptions()
        if proxyStr != None:
            driverOptions.add_argument("--proxy-server={}".format(proxyStr))
        
        driverOptions.add_argument("--incognito")
        driverOptions.add_argument("--disable-gpu")
        driverOptions.add_argument("--start-maximized")
        driverOptions.add_experimental_option("excludeSwitches", ['enable-automation', 'load-extension', 'enable-logging'])

        driver = webdriver.Chrome(executable_path="{}\\chromedriver.exe".format(Misc.GetCwd()), chrome_options=driverOptions)
        return driver
