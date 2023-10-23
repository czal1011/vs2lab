# pylint: disable=protected-access
"""
Simple client server unit test
"""

import logging
import threading
import unittest

import clientserver
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

unittest.TestLoader.sortTestMethodsUsing = None

class TestEchoService(unittest.TestCase):
    """The test"""
    _server = clientserver.Server()  # create single server in class variable
    _server_thread = threading.Thread(target=_server.serve)  # define thread for running server

    @classmethod
    def setUpClass(cls):
        cls._server_thread.start()  # start server loop in a thread (called only once)

    def setUp(self):
        super().setUp()
        self.client = clientserver.Client()  # create new client for each test

    x = """
    # TODO write more tests & modify this one below
    def test_srv_get(self):  # each test_* function is a test
        \"""Test simple call\"""
        msg = self.client.call("Hello VS2Lab")
        self.assertEqual(msg, 'Hello VS2Lab*')
    """

    def test_1_get_rufus_should_return_name_and_number_string(self):
        """Test the GET method with a name that already exists in the phone number database
        (as defined by the constructor)."""
        msg = self.client.get("Rufus")
        self.assertEqual(msg, 'Rufus: 1234567890')

    def test_2_get_nonexistent_name_should_return_name_not_present_warning(self):
        """Test the GET method with a name that doesn't exist in the phone number database."""
        msg = self.client.get("Carlos")
        self.assertEqual(msg, 'Warning: Name Carlos is not present in the phone number database.')

    def test_3_get_all_should_return_long_string_with_all_entries_as_name_and_number_duo(self):
        """Test the GETALL method."""
        msg = self.client.get_all()
        self.assertEqual(msg, 'GETALL|Rufus: 1234567890|Karl-Heinz-Dietrich: 987654321|Peter: 89555521|Peter 2: 2222222223|Sonic the Hedgehog: 9876567811')

    def test_4_add_phone_number_should_add_it_to_the_database_and_enlarge_it(self):
        """Test the "add_phone_number" server method."""
        self._server.add_phone_number("Martin", 5064234)
        msg = self.client.get("Martin")
        self.assertEqual(msg, "Martin: 5064234")
        self.assertEqual(len(self._server._phone_database), 6)

    def test_5_get_empty_string_should_return_invalid_parameter_for_get_string(self):
        """Test the GET method with an empty string as parameter,
        which should return a warning string."""
        msg = self.client.get("")
        self.assertEqual(msg, "Warning: Invalid parameter '' for method 'GET'.")

    def test_6_method_call_with_invalid_parameter_should_return_invaild_method_warning(self):
        """Test the call client method with a custom message parameter,
        which should go against the client-server-protocol and return a warning."""
        msg = self.client.call("gaming")
        self.assertEqual(msg, "Warning: Invalid method 'gaming'.")

    def test_7_method_call_with_get_parameter_should_return_name_and_number_string(self):
        """Test the call client method with a valid message parameter,
        which should work exactly like calling the method itself."""
        msg = self.client.call("GET/Rufus")
        self.assertEqual(msg, 'Rufus: 1234567890')

    def tearDown(self):
        self.client.close()  # terminate client after each test

    @classmethod
    def tearDownClass(cls):
        cls._server._serving = False  # break out of server loop. pylint: disable=protected-access
        cls._server_thread.join()  # wait for server thread to terminate


if __name__ == '__main__':
    unittest.main()
