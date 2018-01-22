import asyncio
import socket
import unittest

from lightsocks.core.cipher import Cipher
from lightsocks.core.password import randomPassword
from lightsocks.server import LsServer
from lightsocks.utils import net


def getValidAddr():
    with socket.socket() as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', 0))
        rv = sock.getsockname()
    return rv


class TestLsServer(unittest.TestCase):
    def setUp(self):
        self.listenAddr = net.Address('127.0.0.1', getValidAddr()[1])

        password = randomPassword()
        self.cipher = Cipher.NewCipher(password)
        self.loop = asyncio.new_event_loop()
        self.server = LsServer(
            loop=self.loop, password=password, listenAddr=self.listenAddr)

    def tearDown(self):
        self.loop.close()

    def test_run_succeed_ipv4(self):
        def didListen(address):
            self.assertEqual(address[0], self.listenAddr.ip)
            self.assertEqual(address[1], self.listenAddr.port)

            async def call_later():
                localServer = socket.create_connection(self.listenAddr)
                localServer.setblocking(False)

                dstServer = socket.socket()
                dstAddress = getValidAddr()
                dstServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                dstServer.bind(dstAddress)
                dstServer.listen(socket.SOMAXCONN)
                dstServer.setblocking(False)

                msg = bytearray((0x05, ))
                self.cipher.encode(msg)
                await self.loop.sock_sendall(localServer, msg)

                received_msg = await self.loop.sock_recv(localServer, 1024)
                received_msg = bytearray(received_msg)
                self.cipher.decode(received_msg)

                self.assertEqual(received_msg, bytearray((0x05, 0x00)))

                msg = bytearray([0x05, 0x01, 0x01, 0x01])
                msg.extend(socket.inet_pton(socket.AF_INET, '127.0.0.1'))
                msg.extend(dstAddress[1].to_bytes(2, 'big'))
                self.cipher.encode(msg)
                await self.loop.sock_sendall(localServer, msg)

                received_msg = await self.loop.sock_recv(localServer, 1024)
                received_msg = bytearray(received_msg)
                self.cipher.decode(received_msg)

                self.assertEqual(received_msg,
                                 bytearray((0x05, 0x00, 0x00, 0x01, 0x00, 0x00,
                                            0x00, 0x00, 0x00, 0x00)))

                msg = bytearray(b'hello world')
                self.cipher.encode(msg)
                await self.loop.sock_sendall(localServer, msg)

                localServer.close()

                dstServer_conn, _ = await self.loop.sock_accept(dstServer)
                received_msg = await self.loop.sock_recv(dstServer_conn, 1024)

                self.assertEqual(received_msg, bytearray(b'hello world'))

                dstServer_conn.close()
                dstServer.close()

                await asyncio.sleep(0.001)
                await asyncio.sleep(0.001)

                self.loop.stop()

            asyncio.ensure_future(call_later(), loop=self.loop)

        with self.assertRaises(RuntimeError):
            self.loop.run_until_complete(self.server.listen(didListen))

    def test_run_succeed_domain(self):
        def didListen(address):
            self.assertEqual(address[0], self.listenAddr.ip)
            self.assertEqual(address[1], self.listenAddr.port)

            async def call_later():
                localServer = socket.create_connection(self.listenAddr)
                localServer.setblocking(False)

                dstServer = socket.socket()
                dstAddress = getValidAddr()
                dstServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                dstServer.bind(dstAddress)
                dstServer.listen(socket.SOMAXCONN)
                dstServer.setblocking(False)

                msg = bytearray([0x05])
                self.cipher.encode(msg)
                await self.loop.sock_sendall(localServer, msg)

                received_msg = await self.loop.sock_recv(localServer, 1024)
                received_msg = bytearray(received_msg)
                self.cipher.decode(received_msg)

                self.assertEqual(received_msg, bytearray([0x05, 0x00]))

                msg = bytearray((0x05, 0x01, 0x01, 0x03, 0x11))
                msg.extend(b'127.0.0.1')
                msg.extend(dstAddress[1].to_bytes(2, 'big'))
                self.cipher.encode(msg)
                await self.loop.sock_sendall(localServer, msg)

                received_msg = await self.loop.sock_recv(localServer, 1024)
                received_msg = bytearray(received_msg)
                self.cipher.decode(received_msg)

                self.assertEqual(received_msg,
                                 bytearray([
                                     0x05, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
                                     0x00, 0x00, 0x00
                                 ]))

                msg = bytearray(b'hello world')
                self.cipher.encode(msg)
                await self.loop.sock_sendall(localServer, msg)

                localServer.close()

                dstServer_conn, _ = await self.loop.sock_accept(dstServer)
                received_msg = await self.loop.sock_recv(dstServer_conn, 1024)

                self.assertEqual(received_msg, bytearray(b'hello world'))

                dstServer_conn.close()
                dstServer.close()

                await asyncio.sleep(0.001)
                await asyncio.sleep(0.001)

                self.loop.stop()

            asyncio.ensure_future(call_later(), loop=self.loop)

        with self.assertRaises(RuntimeError):
            self.loop.run_until_complete(self.server.listen(didListen))

    def test_run_succeed_ipv6(self):
        def didListen(address):

            self.assertEqual(address[0], self.listenAddr.ip)
            self.assertEqual(address[1], self.listenAddr.port)

            async def call_later():
                localServer = socket.create_connection(self.listenAddr)
                localServer.setblocking(False)

                dstServer = socket.socket(socket.AF_INET6)
                dstPort = getValidAddr()[1]
                dstServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                dstServer.bind(('', dstPort))
                dstServer.listen(socket.SOMAXCONN)
                dstServer.setblocking(False)

                msg = bytearray([0x05])
                self.cipher.encode(msg)
                await self.loop.sock_sendall(localServer, msg)

                received_msg = await self.loop.sock_recv(localServer, 1024)
                received_msg = bytearray(received_msg)
                self.cipher.decode(received_msg)

                self.assertEqual(received_msg, bytearray([0x05, 0x00]))

                msg = bytearray((0x05, 0x01, 0x01, 0x04))
                msg.extend(socket.inet_pton(socket.AF_INET6, '::1'))
                msg.extend(dstPort.to_bytes(2, 'big'))
                self.cipher.encode(msg)
                await self.loop.sock_sendall(localServer, msg)

                received_msg = await self.loop.sock_recv(localServer, 1024)
                received_msg = bytearray(received_msg)
                self.cipher.decode(received_msg)

                self.assertEqual(received_msg,
                                 bytearray([
                                     0x05, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
                                     0x00, 0x00, 0x00
                                 ]))

                msg = bytearray(b'hello world')
                self.cipher.encode(msg)
                await self.loop.sock_sendall(localServer, msg)

                localServer.close()

                dstServer_conn, _ = await self.loop.sock_accept(dstServer)
                dstServer_conn.setblocking(False)
                received_msg = await self.loop.sock_recv(dstServer_conn, 1024)

                self.assertEqual(received_msg, bytearray(b'hello world'))

                dstServer_conn.close()
                dstServer.close()

                await asyncio.sleep(0.001)
                await asyncio.sleep(0.001)

                self.loop.stop()

            asyncio.ensure_future(call_later(), loop=self.loop)

        with self.assertRaises(RuntimeError):
            self.loop.run_until_complete(self.server.listen(didListen))

    def test_run_fail(self):
        def didListen(address):

            self.assertEqual(address[0], self.listenAddr.ip)
            self.assertEqual(address[1], self.listenAddr.port)

            async def call_later():
                with self.subTest('只支持sock5'):
                    localServer = socket.create_connection(self.listenAddr)
                    localServer.setblocking(False)

                    msg = bytearray((0x04, ))
                    self.cipher.encode(msg)
                    await self.loop.sock_sendall(localServer, msg)

                    received_msg = await self.loop.sock_recv(localServer, 1024)
                    self.assertFalse(received_msg)

                    localServer.close()

                with self.subTest('包格式错误'):
                    localServer = socket.create_connection(self.listenAddr)
                    localServer.setblocking(False)

                    msg = bytearray((0x05, ))
                    self.cipher.encode(msg)
                    await self.loop.sock_sendall(localServer, msg)

                    received_msg = await self.loop.sock_recv(localServer, 1024)
                    received_msg = bytearray(received_msg)
                    self.cipher.decode(received_msg)

                    self.assertEqual(received_msg, bytearray((0x05, 0x00)))

                    msg = bytearray((0x05, 0x01, 0x01))
                    self.cipher.encode(msg)
                    await self.loop.sock_sendall(localServer, msg)

                    received_msg = await self.loop.sock_recv(localServer, 1024)
                    self.assertFalse(received_msg)

                    localServer.close()

                with self.subTest('错误的CMD类型'):
                    localServer = socket.create_connection(self.listenAddr)
                    localServer.setblocking(False)

                    msg = bytearray((0x05, ))
                    self.cipher.encode(msg)
                    await self.loop.sock_sendall(localServer, msg)

                    received_msg = await self.loop.sock_recv(localServer, 1024)
                    received_msg = bytearray(received_msg)
                    self.cipher.decode(received_msg)

                    self.assertEqual(received_msg, bytearray((0x05, 0x00)))

                    msg = bytearray((0x05, 0xff, 0x01, 0x02, 0xff, 0xff, 0xff))
                    self.cipher.encode(msg)
                    await self.loop.sock_sendall(localServer, msg)

                    received_msg = await self.loop.sock_recv(localServer, 1024)
                    self.assertFalse(received_msg)

                    localServer.close()

                with self.subTest('错误的ATYP类型'):
                    localServer = socket.create_connection(self.listenAddr)
                    localServer.setblocking(False)

                    msg = bytearray((0x05, ))
                    self.cipher.encode(msg)
                    await self.loop.sock_sendall(localServer, msg)

                    received_msg = await self.loop.sock_recv(localServer, 1024)
                    received_msg = bytearray(received_msg)
                    self.cipher.decode(received_msg)

                    self.assertEqual(received_msg, bytearray((0x05, 0x00)))

                    msg = bytearray((0x05, 0x01, 0x01, 0x02, 0xff, 0xff, 0xff))
                    self.cipher.encode(msg)
                    await self.loop.sock_sendall(localServer, msg)

                    received_msg = await self.loop.sock_recv(localServer, 1024)
                    self.assertFalse(received_msg)

                    localServer.close()

                await asyncio.sleep(0.1)
                self.loop.stop()

            asyncio.ensure_future(call_later(), loop=self.loop)

        with self.assertRaises(RuntimeError):
            self.loop.run_until_complete(self.server.listen(didListen))
