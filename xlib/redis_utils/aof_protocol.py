#!/usr/bin/env python
# -*- coding: utf-8 -*-
DELIMITER = "\r\n"


def encode(*args):
    "Pack a series of arguments into a value Redis command"
    result = []
    result.append("*")
    result.append(str(len(args)))
    result.append(DELIMITER)
    for arg in args:
        result.append("$")
        result.append(str(len(arg)))
        result.append(DELIMITER)
        result.append(arg)
        result.append(DELIMITER)
    return "".join(result)


def decode(data):
    processed, index = 0, data.find(DELIMITER)
    if index == -1:
        index = len(data)
    term = data[processed]
    if term == "*":
        return parse_multi_chunked(data)
    elif term == "$":
        return parse_chunked(data)
    elif term == "+":
        return parse_status(data)
    elif term == "-":
        return parse_error(data)
    elif term == ":":
        return parse_integer(data)


def parse_stream(data):
    """
    Args:
        data: (Str) Aof str
    Returns:
        result: (List) Redis command list
    Example:
        *3\r\n
        $3\r\n
        SET\r\n
        $16\r\n
        key:000003946867\r\n
        $20\r\n
        xxxxxxxxxxxxxxxxxxxx\r\n
    """
    cursor = 0
    data_len = len(data)
    result = []
    while cursor < data_len:
        # 每解析完一个命令，则重新将 AOF 字符串截取下
        pdata = data[cursor:]
        # 获取字符串中 DELIMITER(\r\n) 的起始位置 index
        index = pdata.find(DELIMITER)
        # (*) 表示消息体总共有多少行，不包括当前行，*后面是具体的行数。
        count = int(pdata[1:index])
        cmd = ''
        start = index + len(DELIMITER)
        for i in range(count):
            chunk, length = parse_chunked(pdata, start)
            start = length + len(DELIMITER)
            cmd += " " + chunk
        cursor += start
        result.append(cmd.strip())
    return result


def parse_multi_chunked(data):
    index = data.find(DELIMITER)
    count = int(data[1:index])
    result = []
    start = index + len(DELIMITER)
    for i in range(count):
        chunk, length = parse_chunked(data, start)
        start = length + len(DELIMITER)
        result.append(chunk)
    return result


def parse_chunked(data, start=0):
    """
    Args:
        data: (Str) Aof str
        start: (Int) 字符串开始查找偏移量
    Returns:
        result: (List) [chunk,stop_index]
    """
    index = data.find(DELIMITER, start)
    # 不存在字符串
    if index == -1:
        index = start
    # list[start_index: stop_index]
    # 下面的 start 加1 是 $ 的偏移量，即 length 表示下一行数据长度，不包括换行符长度 \r\n,$ 后面则是对应的长度的数据。
    length = int(data[start + 1:index])
    if length == -1:
        if index + len(DELIMITER) == len(data):
            return None
        else:
            return None, index
    else:
        result = data[index + len(DELIMITER):index + len(DELIMITER) + length]
        return result if start == 0 else [result, index + len(DELIMITER) + length]


def parse_status(data):
    return [True, data[1:]]


def parse_error(data):
    return [False, data[1:]]


def parse_integer(data):
    return [int(data[1:])]


if __name__ == '__main__':
    print '---------------------------------------decode(encode("ping"))'
    print(decode(encode("ping")))

    print '---------------------------------------encode("set some value")'
    print(encode("set some value"))

    print '---------------------------------------encode("foobar")'
    print(encode("foobar"))

    print '---------------------------------------parse_stream(data)'
    data = '*3\r\n$3\r\nSET\r\n$15\r\nmemtier-8232902\r\n$2\r\nxx\r\n*3\r\n$3\r\nSET\r\n$15\r\nmemtier-8232902\r\n$2\r\nxx\r\n*3\r\n$3\r\nSET\r\n$15\r\nmemtier-7630684\r\n$3\r\nAAA\r\n'
    print(parse_stream(data))

    #print '---------------------------------------parse_stream(data)'
    #with open('./appendonly.aof') as f:
    #    aof_str = f.read()
    #    print(parse_stream(aof_str))
