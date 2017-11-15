import typing
import socket
import asyncio
import logging

from lightsocks.utils import net
from lightsocks.core.cipher import Cipher
from lightsocks.core.securesocket import SecureSocket

Connection = socket.socket
logger = logging.getLogger(__name__)


class LsLocal(SecureSocket):
    def __init__(self,
                 loop: asyncio.AbstractEventLoop,
                 password: bytearray,
                 listenAddr: net.Address,
                 remoteAddr: net.Address) -> None:
        super().__init__(loop=loop, cipher=Cipher.NewCipher(password))
        self.listenAddr = listenAddr
        self.remoteAddr = remoteAddr

    async def listen(self, didListen: typing.Callable=None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(self.listenAddr)
            listener.listen(socket.SOMAXCONN)
            listener.setblocking(False)

            logger.info('Listen to %s:%d' % self.listenAddr)
            if didListen:
                didListen(listener.getsockname())

            while True:
                connection, address = await self.loop.sock_accept(listener)
                logger.info('Receive %s:%d', *address)
                asyncio.ensure_future(self.handleConn(connection))

    async def handleConn(self, connection: Connection):
        remoteServer = await self.dialRemote()

        def cleanUp(task):
            """
            Close the socket when they succeeded or had an exception.
            """
            remoteServer.close()
            connection.close()

        local2remote = asyncio.ensure_future(
            self.decodeCopy(connection, remoteServer))
        remote2local = asyncio.ensure_future(
            self.encodeCopy(remoteServer, connection))
        task = asyncio.ensure_future(
            asyncio.gather(
                local2remote,
                remote2local,
                loop=self.loop,
                return_exceptions=True))
        task.add_done_callback(cleanUp)

    async def dialRemote(self):
        """
        Create a socket that connects to the Remote Server.
        """
        try:
            remoteConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remoteConn.setblocking(False)
            await self.loop.sock_connect(remoteConn, self.remoteAddr)
        except Exception as err:
            raise ConnectionError('链接到远程服务器 %s:%d 失败:\n%r' % (*self.remoteAddr,
                                                              err))
        return remoteConn
