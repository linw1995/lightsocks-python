[![license](https://img.shields.io/github/license/linw1995/lightsocks-python.svg)](https://github.com/linw1995/lightsocks-python/blob/master/LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/linw1995/lightsocks-python.svg)](https://github.com/linw1995/lightsocks-python)
[![Build Status](https://travis-ci.org/linw1995/lightsocks-python.svg?branch=master)](https://travis-ci.org/linw1995/lightsocks-python)
[![Coverage Status](https://coveralls.io/repos/github/linw1995/lightsocks-python/badge.svg)](https://coveralls.io/github/linw1995/lightsocks-python)

# [Lightsocks-Python](https://github.com/linw1995/lightsocks-python)

一个轻量级网络混淆代理，基于 SOCKS5 协议，可用来代替 Shadowsocks。

- 只专注于混淆，用最简单高效的混淆算法达到目的；
- Py3.6 asyncio实现；

> 本项目为 [你也能写个 Shadowsocks](https://github.com/gwuhaolin/blog/issues/12) 的 Python 实现
> 作者实现了 GO 版本 **[Lightsocks](https://github.com/gwuhaolin/lightsocks)**

## 安装

python版本为最新的3.6

```bash
git clone https://github.com/linw1995/lightsocks-python
cd lightsocks-python
pip install -r requirements.txt
```

## 使用

### lsserver

用于运行在代理服务器的客户端，会还原混淆数据

```bash
$ python lsserver.py -h
usage: lsserver.py [-h] [--version] [--save CONFIG] [-c CONFIG]
                   [-s SERVER_ADDR] [-p SERVER_PORT] [-k PASSWORD] [--random]

A light tunnel proxy that helps you bypass firewalls

optional arguments:
  -h, --help      show this help message and exit
  --version       show version information

Proxy options:
  --save CONFIG   path to dump config
  -c CONFIG       path to config file
  -s SERVER_ADDR  server address, default: 0.0.0.0
  -p SERVER_PORT  server port, default: 8388
  -k PASSWORD     password
  --random        generate a random password to use
```

```bash
$ python lsserver.py --random --save config.json
generate random password
dump config file into 'config.json'
Listen to 0.0.0.0:8388

Please use:

lslocal -u "http://hostname:port/#vJjC3tW5l4nG7C3dHZ7hc77cIYrE2q0ikrWQw2MsRa9rqVlDU9vFTF5Hu6PX367kV6qRPU_z-Y_0sio4DAVV-1bmFrfoYoEHmmWkH9L1UDLZqOv8oYvPbe-miAg5Ow58aheFPitEeTX2bmhYC8nQFf1kA5lxpyc0Ljc2W2Du7TESlFIB8aJ7kz-DnczTXcsUv1oYlhpR-AbKf_DI8jMN_tRNdF-szgIJEQrqZ7alvfrNhCCVQNZ-EIIpSOOfXI7nnMC42B48h3egGzBsSpvpaXCNRhME4mEmePd2HFSrD0ty0SUAhjpvTv9BweUZgHrHKLG6Qi-zjLC0JEngI3VmfQ=="

to config lslocal
```

### lslocal

用于运行在本地电脑的客户端，用于桥接本地浏览器和远程代理服务，传输前会混淆数据

```bash
$ python lslocal.py -h
usage: lslocal.py [-h] [--version] [--save CONFIG] [-c CONFIG] [-u URL]
                  [-s SERVER_ADDR] [-p SERVER_PORT] [-b LOCAL_ADDR]
                  [-l LOCAL_PORT] [-k PASSWORD]

A light tunnel proxy that helps you bypass firewalls

optional arguments:
  -h, --help      show this help message and exit
  --version       show version information

Proxy options:
  --save CONFIG   path to dump config
  -c CONFIG       path to config file
  -u URL          url contains server address, port and password
  -s SERVER_ADDR  server address
  -p SERVER_PORT  server port, default: 8388
  -b LOCAL_ADDR   local binding address, default: 127.0.0.1
  -l LOCAL_PORT   local port, default: 1080
  -k PASSWORD     password
```

```bash
$ python lslocal.py -u "http://remoteAddr:remotePort/#password" --save config.json
dump config file into 'config.json'
Listen to 127.0.0.1:1080
```
