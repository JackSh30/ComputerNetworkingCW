# ChristmasServer2.py

# We will need the following module to generate randomized lost packets
import random
from socket import *
import datetime
import pickle
import hashlib
from threading import Thread
from time import sleep

# Present object
class Present:
    def __init__(self, name):
        self.name = name

# Acknowledgment object for sending 'Thank you' messages
class Acknowledgment:
	def __init__(self, name):
		self.name = "Thank you"

# Receipt object
class Receipt:
    def __init__(self, name, receiptNum):
        self.name = name
        self.receiptNum = receiptNum

# Packet object (contains present in data field)
class Packet:
    def __init__(self, srcAddress, destAddress, seqNum, ackNum, length, timeToLive,
    checksum, receiptNum, data):
        self.srcAddress = srcAddress
        self.destAddress = destAddress
        self.seqNum = seqNum
        self.ackNum = ackNum
        self.length = length
        self.timeToLive = timeToLive
        self.checksum = checksum
        self.receiptNum = receiptNum
        self.data = data

# Storage for presents
serverCache = []

# Example presents already on server for testing purposes:
jumper = Present("A jumper")
packet1 = Packet(('127.0.0.1', 12001), ('127.0.0.1', 12001),
 6, 6, 10, 30, 0, 7, jumper)
serverCache.append(packet1)

socks = Present("socks")
packet2 = Packet(('127.0.0.1', 12001), ('127.0.0.1', 12001),
 8, 8, 10, 30, 0, 9, socks)
serverCache.append(packet2)

phone = Present("A phone")
packet3 = Packet(('127.0.0.1', 12001), ('127.0.0.1', 12001),
 10, 10, 10, 30, 0, 11, phone)
serverCache.append(packet3)

# For test 2 - The server doesn't store any more than 10
# presents in its buffer queue at any one time
#packet4 = Packet(('127.0.0.1', 12001), ('127.0.0.1', 12001),
# 8, 8, 10, 30, 0, 9, socks)
#packet5 = Packet(('127.0.0.1', 12001), ('127.0.0.1', 12001),
# 8, 8, 10, 30, 0, 9, socks)
#packet6 = Packet(('127.0.0.1', 12001), ('127.0.0.1', 12001),
# 8, 8, 10, 30, 0, 9, socks)
#packet7 = Packet(('127.0.0.1', 12001), ('127.0.0.1', 12001),
# 8, 8, 10, 30, 0, 9, socks)
#packet8 = Packet(('127.0.0.1', 12001), ('127.0.0.1', 12001),
# 8, 8, 10, 30, 0, 9, socks)
#packet9 = Packet(('127.0.0.1', 12001), ('127.0.0.1', 12001),
# 8, 8, 10, 30, 0, 9, socks)
#packet10 = Packet(('127.0.0.1', 12001), ('127.0.0.1', 12001),
# 8, 8, 10, 30, 0, 9, socks)
#serverCache.append(packet4)
#serverCache.append(packet5)
#serverCache.append(packet6)
#serverCache.append(packet7)
#serverCache.append(packet8)
#serverCache.append(packet9)
#serverCache.append(packet10)


# List of clients connected to the server
connectedClients = []

# Create a UDP socket
# Use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)
# Assign IP address and port number to socket
serverSocket.bind(('', 12000))

# Variable for Christmas day to check whether to send presents
christmasDay = datetime.datetime(2022, 12, 25)
# Varible for boxing day to check whether to disconnect clients
boxingDay = datetime.datetime(2022, 12, 26)

# Initialise random number for disconnecting clients timer
randNum = 0

# Method to receive presents, store them in the cache and distribute them
# to their intended recipients on Christmas day
def presentExchange():
    while True:
        # Date hard-coded as 25th December for testing purposes,
        # but in reality would be date = datetime.datetime.now()
        date = datetime.datetime(2022, 12, 25)
        print("Date is: " + date.strftime("%d") + " " + date.strftime("%b"))

        # Generate random number in the range of 0 to 10
        rand = random.randint(0, 10)

        # Receive the client packet along with the address it is coming from
        data, address = serverSocket.recvfrom(1024)
        print(address)

        # Decode packet
        data_variable = pickle.loads(data)

        # Server cannot hold any more than 10 presents
        if len(serverCache) < 10:
            print("Storing %s on server ..." % data_variable.data.name)
            # Store on server if space
            serverCache.append(data_variable)
        else:
            print("Dropping present. Buffer full.")

        # Check date is Christmas Day before sending packets
        if date == christmasDay:

            # Add client's address to list of connected clients
            connectedClients.append(address)

            # Server only sends presents if it has connected clients
            if len(connectedClients) > 0:
                for packet in serverCache:
                    # If rand is less than 4, we consider the packet lost
                    # and do not respond
                    if rand < 4:
                    	print(str(packet.data.name)+" timing out")
                    	continue

                    # If intended recipient is connected, send present to that cient
                    if packet.destAddress in connectedClients:
                        # Use pickle library to encode object to send over socket
                        data_string = pickle.dumps(packet)

                        print("Sending present: "+str(packet.data.name))
                        # Send present to intended recipient
                        serverSocket.sendto(data_string, packet.destAddress)
                        # Once sent, can remove present from cache
                        serverCache.remove(packet)

            # If currently no  more presents to send, start countdown timer to
            # disconnect all clients
            if len(serverCache) == 0:
                randNum = random.randint(20, 50)
                t2.start() # Start second thread

        # Disconnect clients when no longer Christmas Day
        elif date == boxingDay:
            disconnectClients()
            # Break out of while loop
            break

# Method to halt sending of data and close socket
def disconnectClients():
    print("Disconnecting clients")
    # Tells socket at other end that server will no longer be sending data
    serverSocket.shutdown(1)
    # Closes socket
    serverSocket.close()

# Method to countdown after server cache is empty.
def disconnectClock(randNum):
	for i in range(randNum):
		sleep(1)
	if len(serverCache) == 0:
        # If server cache still empty after timer reaches zero, disconnect clients,
        # otherwise continue present exchange
		disconnectClients()

t1 = Thread(target=presentExchange)
t2 = Thread(target=disconnectClock, args=(randNum))
t1.start() #starts first thread
