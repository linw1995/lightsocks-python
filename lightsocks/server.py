import logging
import typing
import socket
import asyncio

from lightsocks.utils import net
from lightsocks.core.cipher import Cipher
from lightsocks.core.securesocket import SecureSocket

Connection = socket.socket
logger = logging.getLogger(__name__)


class LsServer(SecureSocket):
    def __init__(self,
                 loop: asyncio.AbstractEventLoop,
                 password: bytearray,
                 listenAddr: net.Address) -> None:
        super().__init__(loop=loop, cipher=Cipher.NewCipher(password))
        self.listenAddr = listenAddr

    async def listen(self, didListen: typing.Callable=None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.setblocking(False)
            listener.bind(self.listenAddr)
            listener.listen(socket.SOMAXCONN)

            logger.info('Listen to %s:%d' % self.listenAddr)
            if didListen:
                didListen(listener.getsockname())

            while True:
                connection, address = await self.loop.sock_accept(listener)
                logger.info('Receive %s:%d', *address)
                asyncio.ensure_future(self.handleConn(connection))

    async def handleConn(self, connection: Connection):
        buf = await self.decodeRead(connection)
        if not buf or buf[0] != 0x05:
            connection.close()
            return

        await self.encodeWrite(connection, bytearray((0x05, 0x00)))

        buf = await self.decodeRead(connection)
        if len(buf) < 7:
            connection.close()
            return

        if buf[1] != 0x01:
            connection.close()
            return

        dstIP = None

        dstPort = buf[-2:]
        dstPort = int(dstPort.hex(), 16)

        dstFamily = None

        if buf[3] == 0x01:
            # ipv4
            dstIP = socket.inet_ntop(socket.AF_INET, buf[4:4 + 4])
            dstAddress = net.Address(ip=dstIP, port=dstPort)
            dstFamily = socket.AF_INET
        elif buf[3] == 0x03:
            # domain
            dstIP = buf[4:-2].decode()
            dstAddress = net.Address(ip=dstIP, port=dstPort)
        elif buf[3] == 0x04:
            # ipv6
            dstIP = socket.inet_ntop(socket.AF_INET6, buf[4:4 + 16])
            dstAddress = (dstIP, dstPort, 0, 0)
            dstFamily = socket.AF_INET6
        else:
            connection.close()
            return

        if dstFamily:
            dstServer = socket.socket(
                family=dstFamily, type=socket.SOCK_STREAM)
            dstServer.connect(dstAddress)
        else:
            dstServer = socket.create_connection(dstAddress)
        dstServer.setblocking(False)

        await self.encodeWrite(connection,
                               bytearray((0x05, 0x00, 0x00, 0x01, 0x00, 0x00,
                                          0x00, 0x00, 0x00, 0x00)))

        def cleanUp(task):
            dstServer.close()
            connection.close()

        conn2dst = asyncio.ensure_future(
            self.decodeCopy(dstServer, connection))
        dst2conn = asyncio.ensure_future(
            self.encodeCopy(connection, dstServer))
        task = asyncio.ensure_future(
            asyncio.gather(
                conn2dst, dst2conn, loop=self.loop, return_exceptions=True))
        task.add_done_callback(cleanUp)
