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
        self.assertTrue(client.ConnectToServer())

    def test_client_disconnection(self):
        client = Client
        self.assertTrue(client.DisconnectFromServer())

    def test_client_login(self):
        client = Client
        self.assertTrue(client.Login())

    def test_client_logout(self):
        client = Client
        self.assertTrue(client.Logout())

    def test_client_save_data_to_database(self):
        client = Client
        self.assertTrue(client.SaveData())


if __name__ == '__main__':
    unittest.main()
