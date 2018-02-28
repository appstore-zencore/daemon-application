import os
import time
import threading
from multiprocessing import Process
import unittest
from .base import *

def example_process():
    time.sleep(30)

class TestZdas(unittest.TestCase):

    def test01(self):
        p = Process(target=example_process)
        p.start()

        assert is_running(p.pid)

        p2 = get_process(p.pid)
        assert p2.pid == p.pid

        process_kill(p.pid)
        time.sleep(1)
        assert not p.is_alive()
        assert not is_running(p.pid)

    def test02(self):
        pidfile = "a.pid"
        write_pidfile(pidfile)
        assert load_pid(pidfile) == os.getpid()

        clean_pid_file(pidfile)
        assert load_pid(pidfile) == 0

    def test03(self):
        pidfile = "b.pid"

        def test03main():
            daemon_start(example_process, pidfile, False)
        t = threading.Thread(target=test03main)
        t.setDaemon(True)
        t.start()

        pid = load_pid(pidfile)
        assert is_running(pid)

