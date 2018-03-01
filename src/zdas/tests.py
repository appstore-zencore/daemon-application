import os
import time
import signal
import threading
from multiprocessing import Process
from multiprocessing import Manager
import unittest
from .base import *

def example_process():
    global stopflag
    stopflag = False

    def log(msg):
        with open("zdas.log", "a", encoding="utf-8") as fobj:
            print(msg, file=fobj)

    def on_exit(sig, frame):
        log(time.time())
        log("got term signal...")
        log(sig)
        log(frame)
        global stopflag
        stopflag = True
    signal.signal(signal.SIGTERM, on_exit)
    signal.signal(signal.SIGINT, on_exit)

    log("example_process start pid={}.".format(os.getpid()))
    while not stopflag:
        log(time.time())
        time.sleep(1)
    log("example_process end.")

def main03():
    daemon_start(example_process, "test03.pid", False)

def main04():
    daemon_start(example_process, "test04.pid", True)

class TestZdas(unittest.TestCase):

    def test01(self):
        p = Process(target=example_process)
        p.start()

        assert is_running(p.pid)

        p2 = get_process(p.pid)
        assert p2.pid == p.pid

        process_kill(p.pid)
        time.sleep(2)
        assert not p.is_alive()
        assert not is_running(p.pid)

    def test02(self):
        pidfile = "test02.pid"

        write_pidfile(pidfile)
        assert load_pid(pidfile) == os.getpid()

        clean_pid_file(pidfile)
        assert load_pid(pidfile) == 0

    def test03(self):
        pidfile = "test03.pid"

        p = Process(target=main03, daemon=True)
        p.start()

        time.sleep(1) # child process may not start yet
        pid = load_pid(pidfile)
        assert pid == p.pid
        assert is_running(pid)
        assert pid != os.getpid()

        print("killing pid={}".format(pid))
        daemon_stop(pidfile)
        time.sleep(2)
        p = get_process(pid)
        if p:
            print(p)
            print(p.status())
        assert not is_running(pid)

    def test04(self):
        pidfile = "test04.pid"

        p = Process(target=main04, daemon=True)
        p.start()

        time.sleep(1) # child process may not start yet
        pid = load_pid(pidfile)
        assert pid != p.pid
        assert pid != os.getpid()
        assert is_running(pid)

        print("killing pid={}".format(pid))
        daemon_stop(pidfile)
        time.sleep(2)
        p = get_process(pid)
        if p:
            print(p)
            print(p.status())
        assert not is_running(pid)
