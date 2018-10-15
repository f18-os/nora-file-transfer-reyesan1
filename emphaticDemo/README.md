# nets-tcp-framed-race

This lab will showcase race conditions and threads.

FramedThreadServer.py` uses threads instead of forking. It waits for a connection, and uses locks to make sure that the file being written to, is only being written to by one thread at a time. If the file does not exist, a serverDirectory is created for server files, and the file is put there and just over written if it already exists. 

FramedThreadClient.py takes a file and runs 100 clients at the same time. You must manually input the file name into the code, and then each thread will run and try to send the file. 

stammerProxy.py is used in the middle of the file transfer from client to server. It works with the multiple clients as well. 

At first, my file was a jumbled mess, but once I implemented locks, it worked. 

Mutex is not supported in Python 3, so I used the threading class with lock() and aquire() and release().

You must run the server file first, and then the file client will run. If you want to use the files with the proxy, you must change the port number in client file from 50001 to 50000. Then you can run the server and then the client. Once the client file is done running the 100 threads, the system exits.
