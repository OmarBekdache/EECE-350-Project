# Note: Most of the code that we came up with was done by all group members together in ZOOM meetings
# Everyone contributed to all parts of the code
# We first divided the tasks amongst us
# UDP upload from client to server was given to Omar Bekdache
# UDP download from server to client was given to Bashar Zougheib
# TCP upload from client to server was given to Sara Abbas
# TCP download from server to client was given to Hussein Harb
# Bandwidth calculation from both sending and receiving side was given to Simon Semaan
# Then we all came together in multiple ZOOM meetings and shared each of our codes and ideas to finally combine them
# into the final code
# comments that clarify the code were added by Omar Bekdache


import socket
import time

# initialize the socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((socket.gethostname(), 12347))
serverSocket.listen(1)

while True:
    # connect to client
    clientSocket, address = serverSocket.accept()
    print("Connected!")
    # receive the file name and mode
    mode, fileName = clientSocket.recv(1024).decode().split()
    if mode == "Request_to_download":
        print("Request to download received")
        # check if file can be found
        # Note: we decided that all files belonging to the UDP server would begin with TCP_SERVER_
        # This is done to distinguish the files that were belonging to servers and the ones belonging to the client
        try:
            t1 = time.time()   # record the time at the beginning of the sending process
            nameHandle = open("TCP_SERVER_"+fileName, "rb")  # open the file with name TCP_SERVER_fileName and start reading
            # send a message to client saying that the request is accepted
            clientSocket.send("Request accepted".encode())
            size = len("Request accepted".encode())  # start recording the size of data sent in bytes
            print("Sending...")
            # start sending the data
            data = nameHandle.read(1024)  # read a chunk of data from file
            while data:
                clientSocket.send(data)  # send a chunk of data to client
                size = size + len(data)  # add to size the size of the data sent
                data = nameHandle.read(1024)  # read a new chunk of data from file
            clientSocket.close()  # close the socket
            t2 = time.time()  # record the time at the end of sending process
            nameHandle.close()
            print("File sent!")
            if (t2 - t1) == 0:  # time spent sending is too small to calculate bandwidth
                print("Time spent sending is too small to calculate average bandwidth")
            else:
                print("Average Bandwidth: ", (size / (t2 - t1)) * 8, "bits/second")
        except FileNotFoundError:
            # if file not found send back appropriate message
            clientSocket.send("Request denied".encode())
            print("File was not found")

    elif mode == "Request_to_upload":
        # opening a file to write to the received content
        nameHandle = open("TCP_SERVER_" + fileName, "wb")
        print("Starting to receive ...")
        t1 = time.time()  # record the starting time to be able to calculate the receiving rate in real time
        t2 = time.time()
        size = 0  # initialize size to 0
        # send a message to the client that we successfully received the file name
        clientSocket.send("Received file name".encode())
        # start receiving the data
        while True:
            if t2 - t1 != 0:
                # if the difference between t2 and t1 becomes different that zero we print the receiving rate
                print("Receiving rate in real time is: ", (size / (t2 - t1)) * 8, "bits/second")
                t1 = time.time()  # measure the new t1 after printing
                size = 0  # reset the size
            data = clientSocket.recv(1024)
            t2 = time.time()  # update t2 to the time after receiving new data
            size = size + len(data)  # add to size the size of data in bytes
            if not data:
                print("File received!")
                nameHandle.close()
                break  # in this case the receiving process has ended and we break from loop
            nameHandle.write(data)  # write to the file the new data received
