import pickle
import sys
import time

import zmq

import constPipe

counted_words = {}

me = str(sys.argv[1])

context = zmq.Context()

sub_socket = context.socket(zmq.SUB)  # create a pull socket

# alle 3 Adressen binden

address1 = "tcp://" + constPipe.SRC + ":" + constPipe.PORT3
address2 = "tcp://" + constPipe.SRC + ":" + constPipe.PORT4
address3 = "tcp://" + constPipe.SRC + ":" + constPipe.PORT5

sub_socket.connect(address1)
sub_socket.connect(address2)
sub_socket.connect(address3)

if(me == "1"):
    sub_socket.setsockopt(zmq.SUBSCRIBE, b"MSG_TO_REDUCER_1")
else:
    sub_socket.setsockopt(zmq.SUBSCRIBE, b"MSG_TO_REDUCER_2")

time.sleep(1) 

print("{} started".format(me))

while True:
    work = sub_socket.recv()
    print(f"Reducer {me} received workload.")
    word = work[16:]
    if(word in counted_words):
        counted_words[word] = counted_words[word] + 1
    else:
        counted_words[word] = 1
    print(f"--------------------------\n"
    + f"Reducer {me} added word {word}. Aggregated words:\n")
    for counted_word in counted_words:
        print(f"{str(counted_word)[4:-1]}: {counted_words[counted_word]}")
    print(f"--------------------------\n")