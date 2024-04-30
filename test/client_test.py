import unittest

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.client import Client


class TestClient(unittest.TestCase):

    def test_client_creation(self):
        client = Client
        self.assertIsInstance(client, Client)

    def test_client_connection(self):
        client = Client
        self.assertTrue(client.connect())


if __name__ == '__main__':
    unittest.main()
