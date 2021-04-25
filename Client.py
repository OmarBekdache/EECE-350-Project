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

import socket
import time

# First we start by selecting the protocol
protocol = input("Enter the protocol that you want to use: ")
serverIP = input("Enter the IP address of the server: ")

# Fist case: The protocol is UDP
if protocol == "UDP":
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # initialize the socket
    # serverAddress stores the IP address and the port number of the UDP server
    serverAddress = (serverIP, 12349)

    while True:      # while loop used to allow the client to send/receive multiple files
        # get information on whether the client wants to download or upload (receive/send) and store it in mode
        mode = input("Do you want to download or upload? ")
        fileName = input("Enter the name of the file: ")
        # Note: we decided that all files belonging to the UDP server would begin with UDP_SERVER_
        # This is done to distinguish the files that were belonging to servers and the ones belonging to the client
        if mode == "download":
            # we send a message to the server requesting to download and providing the name of the file
            # the name of the file is sent without the added UDP_SERVER_ at the beginning
            msg = "Request_to_download"
            clientSocket.sendto((msg+" "+fileName).encode(), serverAddress)
            # wait until we receive a message from the server saying whether the request is accepted or not
            # it could be refused if a file with name fileName is not found
            serverMsg, serverAddress = clientSocket.recvfrom(1024)
            t1 = time.time()  # record the starting time to be able to calculate the receiving rate in real time
            t2 = time.time()
            size = len(serverMsg)  # start recording the number of bytes received
            if serverMsg.decode() == "Request accepted":  # the server accepted the request and will start sending
                nameHandle = open(fileName, 'wb')  # open a file with name fileName to start writing to
                print("Download starting ...")
                while True:  # loop used to receive the data
                    if t2 - t1 != 0:
                        # if the difference between t2 and t1 becomes different that zero we print the receiving rate
                        print("Receiving rate in real time is: ", (size / (t2 - t1)) * 8, "bits/second")
                        t1 = time.time()  # measure the new t1 after printing
                        size = 0  # reset the size
                    data, serverAddress = clientSocket.recvfrom(1024)  # receive a new chunk of data
                    t2 = time.time()  # update t2 to the time after receiving a packet
                    size = size + len(data)  # add to size the length of data (in bytes)
                    if data == "process finished".encode():  # the server will send a message that the process ended
                        print("File downloaded!")
                        nameHandle.close()
                        break  # in this case the download has ended and we break from loop
                    nameHandle.write(data)  # write to the file the new data received
            elif serverMsg.decode() == "Request denied":
                # the request to download denied by the server, this is the case when the file doesn't exist in server
                # no file with name UDP_SERVER_fileName exists
                print("Request to download denied by server, try again and check that the file exists in the server")

        elif mode == "upload":
            t1 = time.time()  # record the time at the beginning of the sending/uploading process
            # we send a message to the server requesting to upload and providing the name of the file
            # the name of the file is sent without the added UDP_SERVER_ at the beginning
            msg = "Request_to_upload"
            clientSocket.sendto((msg + " " + fileName).encode(), serverAddress)
            size = len((msg + " " + fileName).encode())  # start recording the size of the data sent in the process
            nameHandle = open(fileName, "rb")  # open the file to start reading
            print("Sending...")
            # start sending the data
            data = nameHandle.read(1024)  # read a chunk of data
            while data:  # while there is still data to be read in the file
                clientSocket.sendto(data, serverAddress)  # send the data to server
                size = size + len(data)  # add to size the length of the last chunk of data sent
                time.sleep(0.001)  # Delay added to not overwhelm the receiver
                data = nameHandle.read(1024)  # read a new chunk of data
            clientSocket.sendto("process finished".encode(), serverAddress)  # send a message to server saying process ended
            t2 = time.time()  # record the time at the end of the sending process
            print("File sent!")
            if (t2 - t1) == 0:  # time spent sending is too small to calculate bandwidth
                print("Time spent sending is too small to calculate average bandwidth")
            else:
                print("Average Bandwidth: ", (size / (t2 - t1)) * 8, "bits/second")
            nameHandle.close()  # close the file
        # get info on whether the client wants to keep on sending/receiving to UDP server
        x = input("Do you want to keep on sending or receiving? ")
        if x == "no":
            break


# Second case: The protocol is TCP
elif protocol == "TCP":
    while True:  # while loop used to allow the client to send/receive multiple files
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # initialize the socket
        clientSocket.connect((serverIP, 12347))  # connect to the TCP server using appropriate IP and port
        # get information on whether the client wants to download or upload (receive/send) and store it in mode
        mode = input("Do you want to download or upload? ")
        fileName = input("Enter the name of the file: ")
        # Note: we decided that all files belonging to the TCP server would begin with TCP_SERVER_
        # This is done to distinguish the files that were belonging to servers and the ones belonging to the client
        if mode == "download":
            # we send a message to the server requesting to download and providing the name of the file
            # the name of the file is sent without the added TCP_SERVER_ at the beginning
            msg = "Request_to_download"
            clientSocket.send((msg+" "+fileName).encode())
            # wait until we receive a message from the server saying whether the request is accepted or not
            # it could be refused if a file with name fileName is not found
            serverMsg = clientSocket.recv(1024)
            t1 = time.time()  # record the starting time to be able to calculate the receiving rate in real time
            t2 = time.time()
            size = len(serverMsg)  # start recording the number of bytes received
            if serverMsg.decode() == "Request accepted":  # the server accepted the request and will start sending
                nameHandle = open(fileName, 'wb')  # open a file with name fileName to start writing to
                print("Download starting ...")
                while True:  # loop used to receive the data
                    if t2 - t1 != 0:
                        # if the difference between t2 and t1 becomes different that zero we print the receiving rate
                        print("Receiving rate in real time is: ", (size / (t2 - t1)) * 8, "bits/second")
                        t1 = time.time()  # measure the new t1 after printing
                        size = 0  # reset the size
                    data = clientSocket.recv(1024)  # receive a chunk of data
                    t2 = time.time()  # update t2 to the time after receiving a packet
                    size = size + len(data)  # add to size the length of data (in bytes)
                    if not data:
                        print("File downloaded!")
                        nameHandle.close()
                        break  # in this case the download has ended and we break from loop
                    nameHandle.write(data)
            elif serverMsg.decode() == "Request denied":
                # the request to download denied by the server, this is the case when the file doesn't exist in server
                # no file with name UDP_SERVER_fileName exists
                print("Request to download denied by server, try again and check that the file exists in the server")

        elif mode == "upload":
            t1 = time.time()  # record the time at the beginning of the sending/uploading process
            # we send a message to the server requesting to upload and providing the name of the file
            # the name of the file is sent without the added TCP_SERVER_ at the beginning
            msg = "Request_to_upload"
            clientSocket.send((msg + " " + fileName).encode())
            size = len((msg + " " + fileName).encode())  # start recording the size of the data sent in the process
            nameHandle = open(fileName, "rb")  # open the file to start reading
            print("Sending...")
            # wait to make sure file name was successfully sent
            if clientSocket.recv(1024).decode() == "Received file name":
                # start sending the data
                data = nameHandle.read(1024)  # read a chunk of data
                while data:
                    clientSocket.send(data)  # send the data to the server
                    size = size + len(data)  # add to size the length of data in bytes
                    data = nameHandle.read(1024)  # read a new chunk of data
            nameHandle.close()  # close the file
            clientSocket.close()  # close the socket
            t2 = time.time()  # record the time at the end of the sending process
            print("File sent")
            if (t2 - t1) == 0:  # time spent sending is too small to calculate bandwidth
                print("Time spent sending is too small to calculate average bandwidth")
            else:
                print("Average Bandwidth: ", (size / (t2 - t1)) * 8, "bits/second")

        # get info on whether the client wants to keep on sending/receiving to UDP server
        x = input("Do you want to keep on sending or receiving? ")
        if x == "no":
            break



