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
                 remoteAddr: net.Address):
        super().__init__(
            loop=loop,
            cipher=Cipher.NewCipher(password),
            listenAddr=listenAddr,
            remoteAddr=remoteAddr)

    async def listen(self, didListen: typing.Callable=None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(self.listenAddr)
            listener.listen(10)
            listener.setblocking(False)

            if didListen:
                didListen(listener.getsockname())

            while True:
                connection, address = await self.loop.sock_accept(listener)
                logger.info('Receive %s:%d', *address)
                await self.handleConn(connection)

    async def handleConn(self, connection: Connection):
        remoteServer = self.dialRemote()

        def cleanUp(task):
            remoteServer.close()
            connection.close()

        local2remote = asyncio.ensure_future(
            self.decodeCopy(connection, remoteServer))
        remote2local = asyncio.ensure_future(
            self.encodeCopy(remoteServer, connection))
        task = asyncio.ensure_future(
            asyncio.gather(local2remote, remote2local, return_exceptions=True))
        task.add_done_callback(cleanUp)
