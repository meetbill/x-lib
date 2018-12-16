#!/usr/bin/python
# coding=utf8
"""
# Author: meetbill
# Created Time : 2018-12-06 00:33:20

# File Name: demo.py
# Description:

"""
import sys
import os
root_path = os.path.split(os.path.realpath(__file__))[0]
os.chdir(root_path)
sys.path.insert(0, os.path.join(root_path, 'w_lib'))

import color
import blog
import ttable
import schema
import easyrun


def table():
    """
    str_info: string
    """
    x = ttable.Ttable("Special entries", 3)
    x.defattr("l", "r", "r")
    x.header("entry", "effect", "extra column")
    x.append("-- ", "--", "")
    x.append("--- ", "---", "")
    x.append("('--','',2)", ('--', '', 2))
    x.append("('','',2)", ('', '', 2))
    x.append("('---','',2)", ('---', '', 2))
    x.append("('red','1')", ('red', '1'), '')
    x.append("('orange','2')", ('orange', '2'), '')
    x.append("('yellow','3')", ('yellow', '3'), '')
    x.append("('green','4')", ('green', '4'), '')
    x.append("('cyan','5')", ('cyan', '5'), '')
    x.append("('blue','6')", ('blue', '6'), '')
    x.append("('magenta','7')", ('magenta', '7'), '')
    x.append("('gray','8')", ('gray', '8'), '')
    x.append(('---', '', 3))
    x.append("('left','l',2)", ('left', 'l', 2))
    x.append("('right','r',2)", ('right', 'r', 2))
    x.append("('center','c',2)", ('center', 'c', 2))
    print x


def hello(str_info):
    """
    str_info: string
    """
    color.print_error("this is an error message!")
    color.print_warning("this is a warning message!")
    color.print_info("this ia a info message!")
    color.print_log('this is a log message!')
    color.print_debug('this is a debug message!')
    print str_info


def log():
    debug = True
    logpath = "./log/test.log"
    logger = blog.Log(
        logpath,
        level="debug",
        logid="meetbill",
        is_console=debug,
        mbs=5,
        count=5)

    logstr = "helloworld"
    logger.error(logstr)
    logger.warn(logstr)
    logger.info(logstr)
    logger.debug(logstr)


def test_schema():

    # 检查数字
    print '----------------------int'
    print schema.Schema(int).validate(123)
    print schema.Schema(int).is_valid(123)

    # 检查字符串
    print '----------------------str'
    # Regex 没有 is_valid 方法
    print schema.Regex(r'^foo').validate('foobar')
    print schema.Schema(lambda n: "foo" in n).is_valid('foobar')
    print 'False:%s ' % schema.Schema(lambda n: "foo" in n).is_valid('fobar')

    # 检查字典
    print '----------------------dict'
    rules = {
        'name': schema.And(str, len),
        'age': schema.And(schema.Use(int), lambda n: 18 <= n <= 99),
        schema.Optional('gender'): schema.And(str, schema.Use(str.lower), lambda s: s in ('squid', 'kid'))}

    data = {'name': 'Sue', 'age': '28', 'gender': 'Squid'}

    print schema.Schema(rules).validate(data)
    print schema.Schema(rules).is_valid(data)

    print '----------------------list-dict'
    rules = [{
        'name': schema.And(str, len),
        'age': schema.And(schema.Use(int), lambda n: 18 <= n <= 99),
        schema.Optional('gender'): schema.And(str, schema.Use(str.lower), lambda s: s in ('squid', 'kid'))}]

    data = [{'name': 'Sue', 'age': '28', 'gender': 'Squid'},
            {'name': 'Sam', 'age': '42'},
            {'name': 'Sacha', 'age': '20', 'gender': 'KID'}]

    print schema.Schema(rules).validate(data)
    print schema.Schema(rules).is_valid(data)


def test_easyrun():
    exe_result = easyrun.run_capture('ls')
    if exe_result.success:
        print exe_result.output


if __name__ == '__main__':
    import sys
    import inspect
    import time
    import os
    root_path = os.path.split(os.path.realpath(__file__))[0]
    os.chdir(root_path)
    if len(sys.argv) < 2:
        print "Usage:"
        for k, v in sorted(globals().items(), key=lambda item: item[0]):
            if inspect.isfunction(v) and k[0] != "_":
                args, __, __, defaults = inspect.getargspec(v)
                if defaults:
                    print sys.argv[0], k, str(args[:-len(defaults)])[1:-1].replace(",", ""), \
                        str(["%s=%s" % (a, b) for a, b in zip(
                            args[-len(defaults):], defaults)])[1:-1].replace(",", "")
                else:
                    print sys.argv[0], k, str(v.func_code.co_varnames[:v.func_code.co_argcount])[
                        1:-1].replace(",", "")
        sys.exit(-1)
    else:
        try:
            func = eval(sys.argv[1])
        except NameError:
            print "Usage:"
            for k, v in sorted(globals().items(), key=lambda item: item[0]):
                if inspect.isfunction(v) and k[0] != "_":
                    args, __, __, defaults = inspect.getargspec(v)
                    if defaults:
                        print sys.argv[0], k, str(args[:-len(defaults)])[1:-1].replace(",", ""), \
                            str(["%s=%s" % (a, b) for a, b in zip(
                                args[-len(defaults):], defaults)])[1:-1].replace(",", "")
                    else:
                        print sys.argv[0], k, str(v.func_code.co_varnames[:v.func_code.co_argcount])[
                            1:-1].replace(",", "")
            sys.exit(-1)
        args = sys.argv[2:]
        now_start = int(time.time())
        timeArray = time.localtime(now_start)
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        print "\x1B[;36m[start time]\x1B[0m:%s" % timeStr
        try:
            r = func(*args)
        except Exception as e:
            print "Usage:"
            print "\t", "python %s" % sys.argv[1], str(
                func.func_code.co_varnames[:func.func_code.co_argcount])[1:-1].replace(",", "")
            if func.func_doc:
                print "\n".join(["\t\t" + line.strip()
                                 for line in func.func_doc.strip().split("\n")])
            print e
            r = -1
            import traceback
            traceback.print_exc()
        now_end = int(time.time())
        timeArray = time.localtime(now_end)
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        print "\x1B[;36m[end time]\x1B[0m :%s" % timeStr
        time_consum = now_end - now_start
        time_consum_minute = time_consum / 60
        time_consum_second = time_consum % 60
        print "\x1B[;36m[consum time]\x1B[0m %s m:%s s" % (
            time_consum_minute, time_consum_second)
        if isinstance(r, int):
            sys.exit(r)
