import unittest
from unittest.mock import Mock, patch
from wsserver import WSServer


class TestWSServer(unittest.TestCase):
    def setUp(self):        
        self.server = WSServer()

    def test__generate_accept_key(self):
        key = self.server._generate_accept_key("dGhlIHNhbXBsZSBub25jZQ==")
        assert key == "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="

    def tearDown(self):
        pass
