import logging
import socket
import asyncio

from .cipher import Cipher
from lightsocks.utils import net

BUFFER_SIZE = 1024
Connection = socket.socket
logger = logging.getLogger(__name__)


class SecureSocket:
    def __init__(self,
                 loop: asyncio.AbstractEventLoop,
                 cipher: Cipher,
                 listenAddr: net.Address=None,
                 remoteAddr: net.Address=None):
        self.loop = loop or asyncio.get_event_loop()
        self.cipher = cipher
        self.listenAddr = listenAddr
        self.remoteAddr = remoteAddr

    async def decodeRead(self, conn: Connection):
        data = await self.loop.sock_recv(conn, BUFFER_SIZE)

        logger.debug('decodeRead %r', data)

        bs = bytearray(data)
        self.cipher.decode(bs)
        return bs

    async def encodeWrite(self, conn: Connection, bs: bytearray):
        logger.debug('encodeWrite %r', bs)
        bs = bs.copy()

        self.cipher.encode(bs)
        await self.loop.sock_sendall(conn, bs)

    async def encodeCopy(self, dst: Connection, src: Connection):
        logger.debug('encodeCopy')
        while True:
            data = await self.loop.sock_recv(src, BUFFER_SIZE)
            if not data:
                break
            logger.debug('encodeCopy receive %r', data)
            await self.encodeWrite(dst, bytearray(data))

    async def decodeCopy(self, dst: Connection, src: Connection):
        logger.debug('decodeCopy')
        while True:
            bs = await self.decodeRead(src)
            if not bs:
                break
            logger.debug('encodeCopy receive %r', bs)
            await self.loop.sock_sendall(dst, bs)

    def dialRemote(self):
        try:
            remoteConn = socket.create_connection(self.remoteAddr)
            remoteConn.setblocking(False)
        except Exception as err:
            raise Exception('链接到远程服务器 %s:%d 失败: %r' % (*self.remoteAddr, err))
        return remoteConn
