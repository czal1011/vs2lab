import rpc
import logging
import threading
import time

from context import lab_logging


def onReceivedResponse():
    print(result_list["foo_bar"])


lab_logging.setup(stream_level=logging.INFO)

cl = rpc.Client()
cl.run()



base_list = rpc.DBList({'foo'})
result_list = {}
result_list["foo_bar"] = None

thread = threading.Thread(target=cl.append, args=('bar', base_list, onReceivedResponse, result_list))
thread.start()
counter = 0
for i in range(20):
    time.sleep(1)
    print(i)

result = result_list["foo_bar"]

print(f"Result: {result}")

cl.stop()