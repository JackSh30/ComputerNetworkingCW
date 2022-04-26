# ChristmasClient2.py

# We will need the following module to generate randomized lost packets
import random
import sys
import socket
import time
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

# Create a UDP socket
UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 12000


socket.setdefaulttimeout(1)
clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Assign IP address and port number to socket
clientSock.bind(('', 12001))

# List of addresses of this client's family and friends
# For testing purposes, client is sending presents to itself
familyFriendsList = [('127.0.0.1', 12001)]

# List of presents that client will try to send to server
packetsToSend = []

# List of receipts for presents to send if requested
receipts = []

# Example presents that client will send
bike = Present("A bike")
packet1 = Packet(('127.0.0.1', 12001), ('127.0.0.1', 12001),
 1, 1, 10, 30, 0, 2, bike)
packetsToSend.append(packet1)

guitar = Present("A guitar")
packet2 = Packet(('127.0.0.1', 12001), ('127.0.0.1', 12001),
 3, 3, 10, 30, 0, 4, guitar)
packetsToSend.append(packet2)

dog = Present("A dog")
packet3 = Packet(('127.0.0.1', 12001), ('127.0.0.1', 12001),
 5, 5, 10, 30, 0, 6, dog)
packetsToSend.append(packet3)

# Example receipts client has
receipt1 = Receipt("Receipt for bike", 2)
receipts.append(receipt1)
receipt2 = Receipt("Receipt for guitar", 4)
receipts.append(receipt2)

# Variable for randomised timeout number to start timeOutClock when packet is sent
randTimeout = 0

# Boolean for if 'thank you' received after present sent
thankYouRcvd = False

# Upper bound for timeOutClock
# Starts at 10 when first packet sent and increases by 10 each time it reaches zero
upperBound = 0

# Initialise data_string variable for sending packet over socket
data_string = ''

# Initialise variable used to prevent program from attempting to start
# thread 2 more than once
clockInUse = False

# Method telling client how to send presents, receipt requests, receipts and
# acknowledgments, and what to do when it receives them
def presentExchange():
	for packet in packetsToSend:
		# Send data
		print('sending "%s"' % packet.data.name)
		try:
			cur_time=time.time() *1000
			# Encode packet using pickle library
			data_string = pickle.dumps(packet)

			# Calculate checksum of packet before sending
			packet.checksum = hashlib.md5(data_string).hexdigest()

			# Encode again now checksum field given a value
			data_string = pickle.dumps(packet)

			# Set upperBound back to zero for new packet
			upperBound = 0

			# Only send presents to family or friends
			if packet.destAddress in familyFriendsList:
				print('Intended recipient in family/friends list')
				sendPacket(upperBound, data_string, clockInUse)
			else:
				print('Unknown destination address')

			# Receive response
			print('waiting to receive')
			data, server = clientSock.recvfrom(4096)
			#Decode received packet
			data_variable = pickle.loads(data)

			# Store checksum found in header of received data packet
			rcvdChecksum = data_variable.checksum

			# Calculate checksum on received packet
			data_variable.checksum = 0
			data_string = pickle.dumps(data_variable)
			calcChecksum = hashlib.md5(data_string).hexdigest()

			# Only open presents from family or friends and if checksums match (uncorrupted)
			if data_variable.srcAddress in familyFriendsList and rcvdChecksum == calcChecksum:
				if data_variable.data.name != "Thank you" and data_variable.data.name != "Receipt Request":
					print('"Merry Christmas, you received "%s" after "%2.3f" ms' %
					 (data_variable.data.name, (time.time() *1000)-cur_time))

					# Send thank you message to sender
					ack = Acknowledgment()
					data_variable.data = ack
					data_variable.srcAddress = data_variable.destAddress
					data_variable.destAddress = data_variable.srcAddress
					data_string = pickle.dumps(data_variable)
					clientSock.sendto(data_string, data_variable.destAddress)

					# Ask user if they want a receipt, and if they do then send a
					# request for one
					print("Do you need a receipt? Y/N")
					input = input()
					if input == 'Y':
						receipt = Receipt("Receipt Request", data_variable.receiptNum)
						data_variable.data = receipt
						data_string = pickle.dumps(data_variable)
						clientSock.sendto(data_string, data_variable.destAddress)

				# If Receipt Request received, loop through list of receipts to find
				# corresponding receipt and then send it via socket
				elif data_variable.data.name == "Receipt Request":
					for receipt in receipts:
						if receipt.receiptNum == data_variable.receiptNum:
							data_variable.data = receipt
					data_variable.srcAddress = data_variable.destAddress
					data_variable.destAddress = data_variable.srcAddress
					data_string = pickle.dumps(data_variable)
					clientSock.sendto(data_string, data_variable.destAddress)

				elif data_variable.data.name == "Thank you":
					thankYouRcvd = True
					print("Present successfully delivered. Deleting present ...")
					# Packet successfully sent so can remove from packetsToSend list
					packetsToSend.remove(packet)
					# Move onto next packet to send if packet successfully delivered
					continue

				elif rcvdChecksum != calcChecksum:
					print("Checksum mismatch")

		except socket.timeout as inst:
			print('Request timed out')
	print ('closing socket')
	clientSock.close()

# Method for sending packet over socket
def sendPacket(upperBound, data_string, clockInUse):
	upperBound += 10 # increase timer by 10 each time it reaches zero
	print("Sending present to server ...")
	sent=clientSock.sendto(data_string, (UDP_IP_ADDRESS, UDP_PORT_NO))
	randTimeout = random.randint(0, upperBound)
	# Start randomised timeout countdown as long as not already in use
	while True:
		if clockInUse != True:
			clockInUse = True
			t2.start()
			break

# Method to re-send packet once timeout countdown reaches zero
def timeOutClock(randNum, thankYouRcvd, upperBound, data_string, clockInUse):
	for i in range(randNum):
		sleep(1)
	# If 'thank you' not received, re-send packet
	if thankYouRcvd == False:
		sendPacket(upperBound, data_string, clockInUse)
		clockInUse = False

t1 = Thread(target=presentExchange)
t2 = Thread(target=timeOutClock, args=(randTimeout, thankYouRcvd, upperBound, data_string, clockInUse))
t1.start() #starts first thread
