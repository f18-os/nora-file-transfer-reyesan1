#! /usr/bin/env python3
import sys, os, socket, params, time
from threading import Thread
from framedSock import FramedStreamSock

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

class ServerThread(Thread):
    requestCount = 0            # one instance / class
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()
    def run(self):
        cwd = os.getcwd()
        fileName = ''
        while fileName == '':
            # Recieve filename and
            headerPayload = self.fsock.receivemsg()
            if headerPayload:
                pl = headerPayload.decode().split()
            if b'start' in headerPayload:
                fileName = pl[-1]
                if not os.path.exists(cwd + '/serverDirectory/'):
                    os.makedirs(cwd + '/serverDirectory')
                    # fileOpen = open(fileName, 'wb+')
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
            #msg = ("%s! (%d)" % (msg, requestNum)).encode()
            #     print("payload is: %s " % payload)
            payload = payload.decode().replace('~`', '\n')
            if debug: print("rec'd: ", payload)
            fileOpen = open(cwd + '/serverDirectory/%s' % fileName, 'a')
            try:
                if '~fInIs' in payload:
                    fileOpen.close()
                    success = b"File finished sending"
                    # print(success)
                    self.fsock.sendmsg(success)
                    sys.exit(0)
                else:
                    fileOpen.write(payload)
                    # framedSend(sock, payload, debug)
            except FileNotFoundError:
                print("Error trying to receive file")



while True:
    sock, addr = lsock.accept()

    ServerThread(sock, debug)
