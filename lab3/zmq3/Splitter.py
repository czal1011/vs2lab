import pickle
import random
import sys
import time

import zmq

import constPipe

me = str(sys.argv[1])

fileToSplit = open(sys.argv[2], "r").read()

sentences = fileToSplit.split('.')

src = constPipe.SRC  # check task src host
prt = constPipe.PORT1 if me == '1' else constPipe.PORT2  # check task src port

context = zmq.Context()
push_socket = context.socket(zmq.PUSH)  # create a push socket

address = "tcp://" + src + ":" + prt  # how and where to connect
push_socket.bind(address)  # bind socket to address

time.sleep(1) # wait to allow all clients to connect

# splitting

for i in sentences:
    workload = i  # compute workload
    push_socket.send(pickle.dumps((me, workload)))  # send workload to worker