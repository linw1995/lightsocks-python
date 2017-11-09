import argparse
import asyncio
import sys

from lightsocks.core.password import InvalidPasswordError, loadsPassword
from lightsocks.local import LsLocal
from lightsocks.utils.config import (Config, InvalidFileError, InvalidURLError,
                                     load, loadURL)
from lightsocks.utils import net


def run_server(config: Config):
    loop = asyncio.get_event_loop()

    listenAddr = net.Address(config.localAddr, config.localPort)
    remoteAddr = net.Address(config.serverAddr, config.localAddr)
    server = LsLocal(loop=loop,
                     password=config.password,
                     listenAddr=listenAddr,
                     remoteAddr=remoteAddr)
    asyncio.ensure_future(server.listen())
    loop.run_forever()


def main():
    parser = argparse.ArgumentParser(
        description='A light tunnel proxy that helps you bypass firewalls')
    parser.add_argument(
        '--version',
        action='store_true',
        default=False,
        help='show version information')

    proxy_options = parser.add_argument_group('Proxy options')

    proxy_options.add_argument(
        '-c', metavar='CONFIG', help='path to config file')
    proxy_options.add_argument(
        '-u',
        metavar='URL',
        help='url contains server address, port and password')
    proxy_options.add_argument(
        '-s', metavar='SERVER_ADDR', help='server address')
    proxy_options.add_argument(
        '-p',
        metavar='SERVER_PORT',
        type=int,
        help='server port, default: 8388')
    proxy_options.add_argument(
        '-b',
        metavar='LOCAL_ADDR',
        help='local binding address, default: 127.0.0.1')
    proxy_options.add_argument(
        '-l',
        metavar='LOCAL_PORT',
        type=int,
        help='local port, default: 1080')
    proxy_options.add_argument('-k', metavar='PASSWORD', help='password')

    args = parser.parse_args()

    if args.version:
        print('lightsocks 0.1.0')
        sys.exit(0)

    config = Config(None, None, None, None, None)
    if args.c:
        with open(args.c, encoding='utf-8') as f:
            try:
                file_config = load(f)
            except InvalidFileError:
                print(f'invalid config file {args.c!r}')
                sys.exit(1)
        config = config._replace(**file_config._asdict())

    if args.u:
        try:
            url_config = loadURL(args.u)
        except InvalidURLError:
            print(f'invalid config URL {args.u!r}')
            sys.exit(1)

        config = config._replace(**url_config._asdict())

    if args.s:
        serverAddr = args.s
        # TODO: 验证 serverAddr 有效性
        config = config._replace(serverAddr=serverAddr)

    if args.p:
        serverPort = args.p
        # TODO: 验证 serverPort 有效性
        config = config._replace(serverPort=serverPort)

    if args.b:
        localAddr = args.b
        # TODO: 验证 localPort 有效性
        config = config._replace(localAddr=localAddr)

    if args.l:
        localPort = args.l
        # TODO: 验证 localPort 有效性
        config = config._replace(localPort=localPort)

    if args.k:
        try:
            password = loadsPassword(args.k)
            config = config._replace(password=password)
        except InvalidPasswordError:
            print('invalid password')
            sys.exit(1)

    if config.localAddr is None:
        config = config._replace(localAddr='127.0.0.1')

    if config.localPort is None:
        config = config._replace(localPort=1080)

    if config.serverPort is None:
        config = config._replace(serverPort=8388)

    if config.password is None:
        print('need PASSWORD, please use [-k PASSWORD]')
        sys.exit(1)

    if config.serverAddr is None:
        print('need SERVER_ADDR, please use [-s SERVER_ADDR]')

    run_server(config)


if __name__ == '__main__':
    main()
