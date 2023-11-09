import rpc
import logging
import threading
import time

from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()



base_list = rpc.DBList({'foo'})
result_list = {}
result_list["foo_bar"] = None
thread = threading.Thread(target=cl.append, args=('bar', base_list, cl.onReceivedResponse, result_list))
thread.start()
counter = 0
while(True):
    time.sleep(1)
    counter = counter + 1
    print(counter)
    if(result_list["foo_bar"] != None):
        break

result = result_list["foo_bar"]

print(f"Result: {result}")

cl.stop()
