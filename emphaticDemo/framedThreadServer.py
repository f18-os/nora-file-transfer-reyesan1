#! /usr/bin/env python3
import sys, os, socket, params, time
from threading import Thread
from framedSock import FramedStreamSock
import threading

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

# Creating the lock
lock = threading.Lock()
class ServerThread(Thread):
    requestCount = 0            # one instance / class
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()
    def run(self):

        # Locking the code for one thread at a time
        lock.acquire(1)

        # Getting current directory, to create subdirectory for server files
        cwd = os.getcwd()

        # Creating variable for filename from server
        fileName = ''
        while fileName == '':
            # Recieve first payload and grab filename
            headerPayload = self.fsock.receivemsg()
            if headerPayload:
                pl = headerPayload.decode().split()
            if b'start' in headerPayload:
                fileName = pl[-1]
                # Creating subdirectory if it does not exist
                if not os.path.exists(cwd + '/serverDirectory/'):
                    os.makedirs(cwd + '/serverDirectory')
                # Creating file if it does not exist
                fileOpen = open(os.path.join(cwd + '/serverDirectory/', fileName), 'wb+')
                fileOpen.close()
                break
        while True:
            payload = self.fsock.receivemsg()
            if not payload:
                if self.debug: print(self.fsock, "server thread done")
                return
            requestNum = ServerThread.requestCount
            time.sleep(0.001)
            ServerThread.requestCount = requestNum + 1

            # Replacing newline characters
            payload = payload.decode().replace('~`', '\n')
            if debug: print("rec'd: ", payload)
            # Opening file to write to
            fileOpen = open(cwd + '/serverDirectory/%s' % fileName, 'a')
            try:
                # If the file ending symbol is sent, close and send success message
                if '~fInIs' in payload:
                    fileOpen.close()
                    # Releasing thread because file is done being sent
                    lock.release()
                    return
                else:
                    fileOpen.write(payload)
            except FileNotFoundError:
                print("Error trying to receive file")



while True:
    sock, addr = lsock.accept()
    ServerThread(sock, debug)
