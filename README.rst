daemon-application
==================

.. image:: https://travis-ci.org/appstore-zencore/daemon-application.svg?branch=master
    :target: https://travis-ci.org/appstore-zencore/daemon-application

Daemon application help functions.

Install
-------

::

    pip install daemon-application


Usage
-----

::

    import time
    import threading
    import signal
    from daemon_application import daemon_start

    stopflag = False

    def main():
        def on_exit(*args, **kwargs):
            with open("backgroud.log", "a", encoding="utf-8") as fobj:
                print("process got exit signal...", file=fobj)
                print(args, file=fobj)
                print(kwargs, file=fobj)
            global stopflag
            stopflag = True
        signal.signal(signal.SIGTERM, on_exit)
        signal.signal(signal.SIGINT, on_exit)
        while not stopflag:
            time.sleep(1)
            print(time.time())

    if __name__ == "__main__":
        print("start background application...")
        daemon_start(main, "background.pid", True)
