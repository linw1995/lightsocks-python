import typing
import json
from collections import namedtuple
from urllib.parse import urlparse

from lightsocks.core.password import (InvalidPasswordError, dumpsPassword,
                                      loadsPassword)

Config = namedtuple('Config',
                    'serverAddr serverPort localAddr localPort password')


class InvalidURLError(Exception):
    """无效的config URL"""


class InvalidFileError(Exception):
    """无效的配置文件"""


def loadURL(url: str) -> Config:
    url = urlparse(url)
    serverAddr = url.hostname
    serverPort = url.port
    password = url.fragment

    try:
        # 验证 密码 有效性
        password = loadsPassword(password)
    except InvalidPasswordError:
        raise InvalidURLError

    # TODO: 验证 Addr 有效性

    # TODO: 验证 Port 有效性
    return Config(
        serverAddr=serverAddr,
        serverPort=serverPort,
        localAddr='127.0.0.1',
        localPort=1080,
        password=password)


def dumpURL(config: Config) -> str:
    config = config._replace(password=dumpsPassword(config.password))

    url_temp = 'http://{serverAddr}:{serverPort}/#{password}'

    url = url_temp.format_map(config._asdict())

    return url


def dumps(config: Config) -> str:
    config = config._replace(password=dumpsPassword(config.password))
    return json.dumps(config._asdict(), indent=2)


def loads(string: str) -> Config:
    try:
        data = json.loads(string)
        config = Config(**data)

        config = config._replace(password=loadsPassword(config.password))

        # TODO: 验证 Addr 有效性

        # TODO: 验证 Port 有效性
    except Exception:
        raise InvalidFileError

    return config


def dump(f: typing.TextIO, config: Config) -> None:
    config = config._replace(password=dumpsPassword(config.password))

    json.dump(config._asdict(), f, indent=2)


def load(f: typing.TextIO) -> Config:
    try:
        data = json.load(f)
        config = Config(**data)

        config = config._replace(password=loadsPassword(config.password))

        # TODO: 验证 Addr 有效性

        # TODO: 验证 Port 有效性
    except Exception:
        raise InvalidFileError

    return config
