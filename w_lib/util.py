#!/usr/bin/python
# coding=utf8
"""
# Author: meetbill
# Created Time : 2019-09-18 10:32:15

# File Name: util.py
# Description:

"""
import re


def parse_size(input):
    K = 1024
    M = K * K
    G = M * K
    T = G * K
    sizestr = re.search(r'(\d*)', input).group(1)
    size = int(sizestr)
    if input.find("k") > 0 or input.find("K") > 0:
        size = size * K
    if input.find("m") > 0 or input.find("M") > 0:
        size = size * M
    if input.find("g") > 0 or input.find("G") > 0:
        size = size * G
    if input.find("t") > 0 or input.find("T") > 0:
        size = size * T
    return size


def format_size(input):
    input = int(input)
    K = 1024.
    M = K * K
    G = M * K
    T = G * K
    if input >= T:
        return '%.2fT' % (input / T)
    if input >= G:
        return '%.2fG' % (input / G)
    if input >= M:
        return '%.2fM' % (input / M)
    if input >= K:
        return '%.2fK' % (input / K)
    return '%d' % input
