#!/usr/bin/env python
from __future__ import print_function 

import socket
import sys
import time
import string
import random
import signal
import sys
import os
import struct


IP="239.10.0.1"
PORT1=65533
PORT2=65534
status = "echo" # "ping"

INTERVAL = 3000  #unit ms
LEN =64
NUM = 100

is_ipv6=0
count=0
count_received = {}
time_dict = {}
time_dict_min = {}
time_dict_max = {}
is_received = {}


def signal_handler(signal, frame):
	if (status =="echo"):
		print()
		print("echo back %d packet"%(count))
	else:
		print('')
		print('--- ping statistics ---')
		if len(time_dict)==0:
			print("no any reply at all")
		else:
			received_sum = 0
			ttl_sum=0
			print("%d packets transmitted"%count)
			for key in time_dict:
				print('for IP: %s, %d packets received, %.2f%% average loss, rtt min/avg/max = %.2f/%.2f/%.2f ms'%(key,count_received[key], (count- count_received[key])*100.0/count, time_dict_min[key],time_dict[key]/count_received[key],time_dict_max[key] ))
				received_sum+=count_received[key]
				ttl_sum+=time_dict[key]/count_received[key]
			print("-----------------------")
			print('In total, %d packets received, %.2f%% average loss, average rtt avg =  %.2f ms'%(received_sum, (count*len(time_dict) - received_sum)*100.0/count, ttl_sum/len(time_dict)))
	os._exit(0)

def random_string(length):
        return ''.join(random.choice(string.ascii_letters+ string.digits ) for m in range(length))


if __name__== "__main__" :
	if len(sys.argv) <5 and len(sys.argv)>2:
		print()
		print(""" usage:""")
		print("""   multicast_ping <status> <dest_ip> <dest_port> <receive_port> [interval <itv>] [number <num>] [length <len>]""")

		print()
		print(" examples:")

		print("   for ping: ")
		print(" ./multicast_ping.py ping 239.10.0.1 5000 5001")
		print(" means it pings to <239.10.0.1:5000> but receive echo from <239.10.0.1:5001>")
		print(" also")
		print(" ./multicast_ping.py ping 239.10.0.1 5000 5001 interval 4000 number 100 length 64")
		print("where 4000 indicates ping interval in ms, default: 3000, ")
		print("100 indicates ping number, default: 100, ")
		print("64 indicates ping number, default: 64")
		print()
		print("   for echo: ")
		print(" ./multicast_ping.py echo 239.10.0.1 5001 5000 length 3000")
		print(" means it receives from <239.10.0.1:5000> with buffer size 3000 and echo back to <239.10.0.1:5001>")
		print()
		exit()
	if (len(sys.argv)>1):
		status = sys.argv[1]
	if len(sys.argv) > 2:
		IP = sys.argv[2]
		PORT1 = int(sys.argv[3])
		PORT2 = int(sys.argv[4])
	if(len(sys.argv)>=6):
		for i in range(5,len(sys.argv),2):
			if(sys.argv[i]=="interval"):
				INTERVAL = int(sys.argv[i+1])
			if(sys.argv[i]=="number"):
				NUM = int(sys.argv[i+1])
			if(sys.argv[i]=="length"):
				LEN = int(sys.argv[i+1])
	if IP.find(":")!=-1:
		is_ipv6 = 1
	if PORT1 == PORT2:
		print("illigal, PORT1 must not equal to PORT2")
		exit()
	signal.signal(signal.SIGINT, signal_handler)

	if status == "ping":
		print("multicast_ping ping %s via port %d with %d bytes of payload, receives echo form port: %d"%(IP,PORT1,LEN,PORT2))
	else:
		print("multicast_ping echo %s via port %d with %d bytes of payload, receives ping form port: %d"%(IP,PORT2,LEN,PORT1))
	sys.stdout.flush()



	if not is_ipv6:
		sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	else:
		sock = socket.socket(socket.AF_INET6,socket.SOCK_DGRAM)

	if status == "ping":
		if not is_ipv6:
			sock_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			sock_receive.bind(('', PORT2))
			mreq = struct.pack('4sl', socket.inet_aton(IP), socket.INADDR_ANY)
			sock_receive.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		else:
			sock_receive = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			sock_receive.bind(('', PORT2))
			mreq = struct.pack('16sI', socket.inet_pton(socket.AF_INET6, IP), socket.INADDR_ANY)
			sock_receive.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
		while True:
			count+=	1
			print("ping iteration", count)
			payload= random_string(LEN)
			sock.sendto(payload.encode(), (IP, PORT1))
			time_of_send=time.time()
			deadline = time.time() + INTERVAL/1000.0
			for key in is_received:
				is_received[key] = 0
			while True:
				timeout = deadline - time.time()
				if timeout <0:
					break
				sock_receive.settimeout(timeout)
				try:
					recv_data, addr = sock_receive.recvfrom(LEN+1024)
					if  recv_data == payload.encode():
						if(addr[0] not in is_received):
							is_received[addr[0]] = 1
							time_dict[addr[0]] = 0
							time_dict_min[addr[0]] = INTERVAL
							time_dict_max[addr[0]] = 0
							count_received[addr[0]] = 0
						is_received[addr[0]] = 1
						temp_ttl = ((time.time()-time_of_send)*1000)
						time_dict[addr[0]] += temp_ttl
						count_received[addr[0]]+=1
						time_dict_max[addr[0]] = max(temp_ttl,time_dict_max[addr[0]])
						time_dict_min[addr[0]] = min(temp_ttl,time_dict_min[addr[0]])
						print("received echo from %s, ttl is %.2f ms"%(addr[0], temp_ttl))
						sys.stdout.flush()
				except socket.timeout:
					break
				except:
					pass

			for key in is_received:
				if (is_received[key]==0):
					print("Timeout for %s, suggest adding interval"%key)
			sys.stdout.flush()
			if(count == NUM):
				signal_handler(0,0)
	elif (status == "echo"):
		if not is_ipv6:
			sock_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			sock_receive.bind(('', PORT1))
			mreq = struct.pack('4sl', socket.inet_aton(IP), socket.INADDR_ANY)
			sock_receive.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		else:
			sock_receive = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			sock_receive.bind(('', PORT1))
			mreq = struct.pack('16sI', socket.inet_pton(socket.AF_INET6, IP), socket.INADDR_ANY)
			sock_receive.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
		while True:
			recv_data,addr = sock_receive.recvfrom(LEN+1024)
			sock.sendto(recv_data,(IP,PORT2))
			count+=	1
	else :
		print("error state")
		exit()
