#!/usr/bin/python
# coding=utf8
"""
# Author: meetbill
# Created Time : 2019-09-18 10:36:51

# File Name: test_util.py
# Description:

"""
import w_lib.util


def test_parse_size():
    assert w_lib.util.parse_size("20K") == 20480
    assert w_lib.util.parse_size("20k") == 20480


def test_format_size():
    assert w_lib.util.format_size(20480) == "20.00K"
    assert w_lib.util.format_size("20480") == "20.00K"
