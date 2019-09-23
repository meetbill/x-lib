#!/usr/bin/python
# coding=utf8
"""
# Author: meetbill
# Created Time : 2019-09-18 10:36:51

# File Name: test_util.py
# Description:

"""
import xlib.util


def test_parse_size():
    assert xlib.util.parse_size("20K") == 20480
    assert xlib.util.parse_size("20k") == 20480


def test_format_size():
    assert xlib.util.format_size(20480) == "20.00K"
    assert xlib.util.format_size("20480") == "20.00K"
