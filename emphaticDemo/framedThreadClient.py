#! /usr/bin/env python3

# Echo client program
import socket, sys, re
import params
from framedSock import FramedStreamSock
from threading import Thread
import time

switchesVarDefaults = (
    (('-s', '--server'), 'server', "localhost:50001"),
    #(('-s', '--server'), 'server', "localhost:50000"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

class ClientThread(Thread):
    def __init__(self, serverHost, serverPort, debug):
        Thread.__init__(self, daemon=False)
        self.serverHost, self.serverPort, self.debug = serverHost, serverPort, debug
        self.start()
    def run(self):
       s = None
       for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
           af, socktype, proto, canonname, sa = res
           try:
               print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
               s = socket.socket(af, socktype, proto)
           except socket.error as msg:
               print(" error: %s" % msg)
               s = None
               continue
           try:
               print(" attempting to connect to %s" % repr(sa))
               s.connect(sa)
           except socket.error as msg:
               print(" error: %s" % msg)
               s.close()
               s = None
               continue
           break

       if s is None:
           print('could not open socket')
           sys.exit(1)

       fs = FramedStreamSock(s, debug=debug)

        # Staring client, asking until user wants to quit
       usrInput = ''
       while usrInput is not 'q':
           # Asking user for input file and put command
           usrInput = input("Entering 'put' and a filename will allow you to transfer a file\n:")
           # Splitting input by space to check if put command and filename is present
           splitInput = usrInput.split(' ')
           if splitInput[0].strip() == 'put':
               usrFileName = splitInput[-1]
               # Try to open file, if not, print that file not found and loop again for input
               try:
                   fileToSend = open(usrFileName, 'rb')

                   # Starting message, to pass in file name and start message (header)
                   fs.sendmsg(b'start ' + usrFileName.encode())

                   # Opening the file as a binary, to be able to send 100 bytes at a time
                   with open(usrFileName.strip(),'rb') as binary_file:
                       # Variable to grab bytes from the file for sending
                       byteData = binary_file.read()

                   # Replacing new lines with special characters to avoid errors and replace them back later
                   byteData = byteData.replace(b'\n',b'~`')

                   # Checking if the length of the byteData is 100 bytes or more, if so, send the data
                   while len(byteData) >= 100:
                       # Send variable for the beginning 100 bytes
                       send = byteData[:100]
                       # Move the byteData from the last sent 100 bytes to the next 100 bytes, or end of the byteData
                       byteData = byteData[100:]
                       # Try to send the 100 bytes of byteData (send)
                       try:
                           fs.sendmsg(send)
                       except BrokenPipeError:
                           print("Broken pipe, exiting")
                           sys.exit(1)

                   # If byteData is still greater than 0, send the remaining bytes that were not apart of the last 100 bytes
                   if len(byteData) > 0:
                       fs.sendmsg(byteData)

                   # Sending the end signal to know that the file is done sending
                   fs.sendmsg(b"~fInIs")
                   recMessage = fs.receivemsg()
                   if recMessage:
                       print("received:", recMessage.decode())

               # Match enclosing try
               except FileNotFoundError:
                   print("Wrong file or file path")
                   continue
               #print("sending file %s" % (usrFileName))

           # Else for enclosing userInput if statement
           elif usrInput.strip() == 'q':
               print("Exiting")
               sys.exit(0)

           else:
               print("Invalid please try again, enter 'q' to exit")

#for i in range(100):
for i in range(1):
    ClientThread(serverHost, serverPort, debug)

