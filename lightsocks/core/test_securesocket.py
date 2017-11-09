import asyncio
import socket
import unittest

from lightsocks.core.cipher import Cipher
from lightsocks.core.password import randomPassword
from lightsocks.core.securesocket import SecureSocket
from lightsocks.utils import net


class TestSecuresocket(unittest.TestCase):
    def setUp(self):
        self.ls_local, self.ls_server = socket.socketpair()
        password = randomPassword()
        self.loop = asyncio.new_event_loop()
        self.cipher = Cipher.NewCipher(password)
        self.securesocket = SecureSocket(loop=self.loop, cipher=self.cipher)
        self.msg = bytearray(b'hello world')
        self.encripted_msg = self.msg.copy()
        self.cipher.encode(self.encripted_msg)

    def tearDown(self):
        self.loop.close()
        self.ls_local.close()
        self.ls_server.close()

    def test_dialRemote(self):
        remoteServer = socket.socket()
        remoteServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        address = net.Address('127.0.0.1', 11111)
        remoteServer.bind(address)
        remoteServer.listen(1)

        self.securesocket.remoteAddr = address

        localServer = self.securesocket.dialRemote()
        localServer.setblocking(True)
        localServer.send(self.msg)

        remoteConn, _ = remoteServer.accept()
        received_msg = remoteConn.recv(1024)

        self.assertEqual(received_msg, self.msg)

        with self.assertRaises(Exception):
            self.securesocket.remoteAddr = net.Address('127.0.0.1', 0)
            self.securesocket.dialRemote()

        localServer.close()
        remoteServer.close()

    def test_decodeRead(self):

        self.ls_local.send(self.encripted_msg)
        self.ls_server.setblocking(False)

        received_msg = self.loop.run_until_complete(
            self.securesocket.decodeRead(self.ls_server))

        self.assertEqual(received_msg, self.msg)

    def test_encodeWrite(self):

        self.ls_local.setblocking(False)
        self.loop.run_until_complete(
            self.securesocket.encodeWrite(self.ls_local, self.msg))

        received_msg = self.ls_server.recv(1024)

        self.assertEqual(bytearray(received_msg), self.encripted_msg)

    def test_decodeCopy(self):
        dstServer, ls_server_conn = socket.socketpair()
        ls_server_conn.setblocking(False)
        self.ls_server.setblocking(False)

        self.ls_local.sendall(self.encripted_msg * 10)
        self.ls_local.close()

        self.loop.run_until_complete(
            self.securesocket.decodeCopy(ls_server_conn, self.ls_server))
        received_msg = dstServer.recv(1024)

        self.assertEqual(bytearray(received_msg), self.msg * 10)

        dstServer.close()
        ls_server_conn.close()

    def test_encodeCopy(self):
        user_client, ls_local_conn = socket.socketpair()
        ls_local_conn.setblocking(False)
        self.ls_local.setblocking(False)

        user_client.sendall(self.msg * 10)
        user_client.close()

        self.loop.run_until_complete(
            self.securesocket.encodeCopy(self.ls_local, ls_local_conn))
        received_msg = self.ls_server.recv(1024)

        self.assertEqual(bytearray(received_msg), self.encripted_msg * 10)

        ls_local_conn.close()
