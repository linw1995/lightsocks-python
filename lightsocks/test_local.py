import asyncio
import socket
import unittest

from lightsocks.core.cipher import Cipher
from lightsocks.core.password import randomPassword
from lightsocks.local import LsLocal
from lightsocks.utils import net


class TestLsLocal(unittest.TestCase):
    def setUp(self):
        self.listenAddr = net.Address('127.0.0.1', 11111)
        self.remoteAddr = net.Address('127.0.0.1', 22222)
        self.remoteServer = socket.socket()
        self.remoteServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.remoteServer.bind(self.remoteAddr)
        self.remoteServer.listen(1)

        password = randomPassword()
        self.cipher = Cipher.NewCipher(password)
        self.loop = asyncio.new_event_loop()
        self.local = LsLocal(
            loop=self.loop,
            password=password,
            listenAddr=self.listenAddr,
            remoteAddr=self.remoteAddr)

        self.msg = bytearray(b'hello world')
        self.encrypted_msg = self.msg.copy()
        self.cipher.encode(self.encrypted_msg)

    def tearDown(self):
        self.remoteServer.close()
        self.loop.close()

    def test_run(self):
        def didListen(address):

            self.assertEqual(address[0], self.listenAddr.ip)
            self.assertEqual(address[1], self.listenAddr.port)

            user_client = socket.create_connection(self.listenAddr)
            user_client.send(b'hello world')
            user_client.close()

            async def call_later():
                conn, _ = await self.loop.sock_accept(self.remoteServer)
                received_msg = await self.loop.sock_recv(conn, 1024)
                conn.close()

                self.assertEqual(received_msg, self.encrypted_msg)

                await asyncio.sleep(0.1)
                self.loop.stop()

            asyncio.ensure_future(call_later(), loop=self.loop)

        with self.assertRaises(RuntimeError):
            self.loop.run_until_complete(self.local.listen(didListen))
