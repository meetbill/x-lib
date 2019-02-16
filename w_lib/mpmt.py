#!/usr/bin/env python3
# coding=utf-8
from __future__ import absolute_import, division, unicode_literals

import multiprocessing
import os
import threading
import blog
import Queue

debug = False
logpath = "./log/mpmt.log"
_logger = blog.Log(
    logpath,
    level="debug",
    logid="mpmt",
    is_console=debug,
    mbs=5,
    count=5)

try:
    from typing import Any, Union
except BaseException:
    pass

VERSION = (2, 0, 0, 5)
VERSION_STR = "{}.{}.{}.{}".format(*VERSION)


def _worker_container(mpmt_flag, task_q, result_q, func):
    """
    Args:
        result_q (Queue|None)
    """
    _th_name = threading.current_thread().name

    _logger.debug(
        '[mpmt_flag]:%s [W++] mpmt worker %s starting' %
        (mpmt_flag, _th_name))

    while True:
        taskid, args, kwargs = task_q.get()
        # _logger.debug("mpmt worker %s got taskid:%s", _th_name, taskid)

        if taskid is StopIteration:
            _logger.debug(
                "[mpmt_flag]:%s [W++] mpmt worker %s got stop signal" %
                (mpmt_flag, _th_name))
            break
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            _logger.error(
                "[mpmt_flag]:%s [W++] Unhandled error %s in worker thread, taskid: %s" %
                (mpmt_flag, e, taskid))
            if result_q is not None:
                result_q.put_nowait((taskid, e))
        else:
            # _logger.debug("done %s", taskid)
            if result_q is not None:
                result_q.put_nowait((taskid, result))


def _slaver(mpmt_flag, task_q, result_q, threads, func):
    """
    接收与多进程任务并分发给子线程

    Args:
        task_q (Queue)
        result_q (Queue|None)
        threads (int)
        func (Callable)
    """
    _process_name = "{}(PID:{})".format(
        multiprocessing.current_process().name,
        multiprocessing.current_process().pid,
    )
    _logger.debug(
        "[mpmt_flag]:%s [W] mpmt subprocess %s start. threads:%s" %
        (mpmt_flag, _process_name, threads))

    pool = []
    for i in range(threads):
        th = threading.Thread(target=_worker_container,
                              args=(mpmt_flag, task_q, result_q, func),
                              name="{}#{}".format(_process_name, i + 1)
                              )
        th.daemon = True
        pool.append(th)
    for th in pool:
        th.start()

    for th in pool:
        th.join()

    _logger.debug(
        "[mpmt_flag]:%s [W] mpmt subprocess %s exiting" %
        (mpmt_flag, _process_name))


def get_cpu_count():
    try:
        if hasattr(os, "cpu_count"):
            return os.cpu_count()
        else:
            return multiprocessing.cpu_count()
    except BaseException:
        return 0


class MPMT(object):
    """
    简易的多进程-多线程任务队列
    Args:
        worker (Callable): 工作函数
        processes (int): 进程数, 若不指定则为CPU核心数
        threads (int): 每个进程下多少个线程
        total_count (int): 总任务数
        finish_count (int): 已完成的任务数
    """

    def __init__(
            self,
            worker,
            processes=None,
            threads=2,
            task_queue_maxsize=-1,
            mpmt_flag="mpmt"
    ):
        self.worker = worker
        self.collector = True
        self.mpmt_flag = mpmt_flag

        self.processes_count = processes or get_cpu_count() or 1
        if self.processes_count == 1:
            self.multi = False
        else:
            self.multi = True

        self.threads_count = threads

        self.total_count = 0  # 总任务数
        self.finish_count = 0  # 已完成的任务数

        self.processes_pool = []
        self.task_queue_maxsize = task_queue_maxsize
        self.task_queue_closed = False

        self.taskid = None

        if self.multi:
            self.task_q = multiprocessing.Queue(maxsize=task_queue_maxsize)
        else:
            self.task_q = Queue.Queue(maxsize=task_queue_maxsize)

        if self.collector:
            if self.multi:
                self.result_q = multiprocessing.Queue()
            else:
                self.result_q = Queue.Queue()
        else:
            self.result_q = None
        self.collector_thread = None
        self.worker_processes_pool = []
        self.running_tasks = {}
        self.result = []
        _logger.debug(
            "[mpmt_flag]:%s [version]:%s" %
            (self.mpmt_flag, VERSION_STR))

    def start(self):
        if self.worker_processes_pool:
            raise RuntimeError('You can only start ONCE!')

        if self.multi:
            _logger.debug(
                "[mpmt_flag]:%s [start] [worker-multi] mpmt starting worker subprocess" % (self.mpmt_flag))
            for i in range(self.processes_count):
                p = multiprocessing.Process(
                    target=_slaver,
                    args=(
                        self.mpmt_flag,
                        self.task_q,
                        self.result_q,
                        self.threads_count,
                        self.worker),
                    name="mpmt-{}".format(i + 1)
                )
                p.daemon = True
                p.start()
                self.worker_processes_pool.append(p)
        else:
            _logger.debug(
                "[mpmt_flag]:%s [start] [worker-nil] mpmt starting worker subprocess" % (self.mpmt_flag))
        if self.collector is not None:
            _logger.debug(
                "[mpmt_flag]:%s [start] mpmt starting collector thread" %
                (self.mpmt_flag))
            self.collector_thread = threading.Thread(
                target=self._collector_container, name='mpmt-collector')
            self.collector_thread.daemon = True
            self.collector_thread.start()
        else:
            _logger.debug(
                "[mpmt_flag]:%s [start] mpmt no collector given, skip collector thread" % (self.mpmt_flag))

    def put(self, *args, **kwargs):
        """
        put task params into working queue

        """
        if self.multi:
            if not self.worker_processes_pool:
                raise RuntimeError('you must call .start() before put')
        if self.task_queue_closed:
            raise RuntimeError('you cannot put after task_queue closed')

        taskid = self._gen_taskid()
        task_tuple = (taskid, args, kwargs)
        if self.collector:
            self.running_tasks[taskid] = task_tuple

        self.task_q.put(task_tuple)
        self.total_count += 1

    def join(self, close=True):
        """
        Wait until the works and handlers terminates.

        """
        if close and not self.task_queue_closed:  # 注意: 如果此处不close, 则一定需要在其他地方close, 否则无法结束
            self.close()

        # 等待所有工作进程结束
        if self.multi:
            for p in self.worker_processes_pool:  # type: multiprocessing.Process
                p.join()
                _logger.debug(
                    "[mpmt_flag]:%s [join] [work-multi] mpmt subprocess %s %s closed" %
                    (self.mpmt_flag, p.name, p.pid))
        else:
            _slaver(
                self.mpmt_flag,
                self.task_q,
                self.result_q,
                self.threads_count,
                self.worker)
            _logger.debug(
                "[mpmt_flag]:%s [join] [work-nil] mpmt closed" %
                (self.mpmt_flag))
        _logger.debug(
            "[mpmt_flag]:%s [join] mpmt all worker completed" %
            (self.mpmt_flag))

        if self.collector:
            self.result_q.put_nowait((StopIteration, None))  # 在结果队列中加入退出指示信号
            self.collector_thread.join()  # 等待处理线程结束

        _logger.debug(
            "[mpmt_flag]:%s [join] mpmt join completed" %
            (self.mpmt_flag))

    def _gen_taskid(self):
        return "mpmt{}".format(self.total_count)

    def _collector_container(self):
        """
        接受子进程传入的结果,并把它发送到master_product_handler()中

        """
        _logger.debug(
            "[mpmt_flag]:%s [C] mpmt collector start" %
            (self.mpmt_flag))

        while True:
            taskid, result = self.result_q.get()

            if taskid is StopIteration:
                _logger.debug(
                    "[mpmt_flag]:%s [C] mpmt collector got stop signal" %
                    (self.mpmt_flag))
                break
            self.running_tasks.pop(taskid)
            self.taskid = taskid
            self.finish_count += 1
            _logger.debug(
                "[mpmt_flag]:%s [C] collector finish [%d/%d]" %
                (self.mpmt_flag, self.finish_count, self.total_count))
            try:
                self.result.append(result)
            except BaseException:
                # 为了继续运行, 不抛错
                _logger.error(
                    "[mpmt_flag]:%s [C] an error occurs in collector, task: %s" % (self.mpmt_flag, taskid))

    def close(self):
        """
        Close task queue
        """

        # 在任务队列尾部加入结束信号来关闭任务队列
        for i in range(self.processes_count * self.threads_count):
            self.task_q.put((StopIteration, (), {}))
        self.task_queue_closed = True

    def get_result(self):
        return self.result
