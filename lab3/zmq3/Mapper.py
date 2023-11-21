import pickle
import sys
import time

import zmq

import constPipe

me = str(sys.argv[1])
pull_address1 = "tcp://" + constPipe.SRC + ":" + constPipe.PORT1  # 1st task src
pull_address2 = "tcp://" + constPipe.SRC + ":" + constPipe.PORT2  # 2nd task src

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)  # create a pull socket

pull_socket.connect(pull_address1)  # connect to task source 1
pull_socket.connect(pull_address2)  # connect to task source 2

pub_socket = context.socket(zmq.PUB)

if(me == "1"):
    pub_address = "tcp://" + constPipe.SRC + ":" + constPipe.PORT3
elif(me == "2"):
    pub_address = "tcp://" + constPipe.SRC + ":" + constPipe.PORT4
else:
    pub_address = "tcp://" + constPipe.SRC + ":" + constPipe.PORT5

pub_socket.bind(pub_address)

time.sleep(1) 

print("{} started".format(me))

while True:
    work = pickle.loads(pull_socket.recv())  # receive work from a source
    print("{} received workload {} from Splitter {}".format(me, work[1], work[0]))
    words = str(work[1]).split(' ') # list of words
    print(words)
    for word in words:
        if(word == ''):
            continue
        print(word)
        reducer = constPipe.assignment_schema[word]
        print(f"Reducer: {reducer}")
        pub_socket.send(("MSG_TO_REDUCER_{}: {}".format(reducer, word)).encode())