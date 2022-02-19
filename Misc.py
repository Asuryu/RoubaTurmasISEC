import os
import sys
import win32api
import requests

Cls = lambda: os.system('cls' if os.name == 'nt' else 'clear')
Title = lambda title: os.system("title {}".format(title))
GetCwd = lambda: os.path.dirname(sys.executable) if hasattr(sys, 'frozen') else os.path.dirname(os.path.realpath(sys.argv[0]))
FileExists = lambda path: True if os.path.exists(path) else False
DeleteFile = lambda path: os.remove(path) if FileExists(path) else None

def GetFileVersion(path):
    try:
        info = win32api.GetFileVersionInfo(path, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        version = "{}.{}.{}.{}".format(win32api.HIWORD(ms), win32api.LOWORD (ms), win32api.HIWORD (ls), win32api.LOWORD (ls))
        return version
    except:
        return None