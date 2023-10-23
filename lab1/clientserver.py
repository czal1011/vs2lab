"""
Client and server using classes
"""

import logging
import socket

import const_cs
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)  # init loging channels for the lab

# pylint: disable=logging-not-lazy, line-too-long, logging-fstring-interpolation

class Server:
    """ The server """
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True
    _phone_database = {}

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)  # time out in order not to block forever
        self._logger.info("Server bound to socket " + str(self.sock))
        self.add_phone_number("Rufus", 1234567890)
        self.add_phone_number("Karl-Heinz-Dietrich", 987654321)
        self.add_phone_number("Peter", 89555521)
        self.add_phone_number("Peter 2", 2222222223)
        self.add_phone_number("Sonic the Hedgehog", 9876567811)

    def add_phone_number(self, name: str, number: int):
        """Adds a phone number to the phone number database"""
        self._logger.info(f"Adding phone number {number} belonging to {name}...")
        if '|' in name:
            self._logger.info(f"Warning: Name {name} contains an invalid letter ( | ).")
            return
        self._phone_database[name] = number
        self._logger.info(f"Successfully added {name} ({number}) to the database!")

    def serve(self):
        """ Serve echo """
        self.sock.listen(1)
        while self._serving:  # as long as _serving (checked after connections or socket timeouts)
            try:
                # pylint: disable=unused-variable
                (connection, address) = self.sock.accept()  # returns new socket and address of client
                while True:  # forever
                    data = connection.recv(1024)  # receive data from client
                    if not data:
                        break  # stop if client stopped
                    data_decoded = data.decode('ascii')
                    if data_decoded == 'get_all':
                        if len(self._phone_database) == 0:
                            connection.send("Warning: Phone number database is empty.".encode('ascii'))
                        else:
                            return_string = "GETALL|"  # return string format: "GETALL|name: number|name: number|..."
                            for entry in self._phone_database.items():
                                name = entry[0]
                                number = entry[1]
                                name_number_pair_string = f"{name}: {number}|"
                                return_string += name_number_pair_string
                            connection.send(return_string[:-1].encode('ascii'))  # send return string, minus the last '|' character
                    elif data_decoded.startswith("get/"):
                        if data_decoded == 'get/':
                            connection.send("Warning: Invalid parameter '' for method 'GET'.".encode('ascii'))
                            break
                        name = data_decoded[4:]
                        if name in self._phone_database:
                            # return string format: "name: number"
                            number = self._phone_database[name]
                            return_string = f"{name}: {number}"
                            connection.send(return_string.encode('ascii'))
                        else:
                            connection.send(f"Warning: Name {name} is not present in the phone number database.".encode('ascii'))
                    else:
                        self._logger.warning(f"Warning: Invalid method '{data_decoded}'.")
                        connection.send(f"Warning: Invalid method '{data_decoded}'.".encode('ascii'))
                connection.close()  # close the connection
            except socket.timeout:
                pass  # ignore timeouts
        self.sock.close()
        self._logger.info("Server down.")


class Client:
    """ The client """
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((const_cs.HOST, const_cs.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def call(self, msg_in="Hello, world"):
        """ Call server """
        self.sock.send(msg_in.encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        msg_out = data.decode('ascii')
        # print the result
        self.print_message(msg_out)
        self.sock.close()  # close the connection
        self.logger.info("Client down.")
        return msg_out

    def print_message(self, _message):
        """Prints the message received by the server."""
        self.logger.info("=================================================")
        if _message.startswith('GETALL|'):  # GETALL method return string format: "GETALL|name: number|name: number|..."
            name_number_pairs = _message[7:].split('|') # remove "GETALL|"
            for entry in name_number_pairs:
                self.logger.info(entry)
        else:
            if _message.startswith("Warning"):
                self.logger.warning(_message)  # warnings
            else:
                self.logger.info(_message)  # GET method
        self.logger.info("=================================================\n")


    def get(self, _name):
        """Attempts to call the server to get a phone number based on the parameter name."""
        self.logger.info(f"Attempting to use method \"GET/{_name}\"...")
        self.call(msg_in=f"get/{_name}")

    def get_all(self):
        """Attempts to call the server to get all existing phone numbers."""
        self.logger.info("Attempting to use method \"GETALL\"...")
        self.call(msg_in="get_all")

    def close(self):
        """ Close socket """
        self.sock.close()
