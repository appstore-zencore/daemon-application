"""
Zencore daemon application start(zdas).
"""
import os
import signal
import logging
import psutil

__all__  = [
    "process_kill",
    "load_pid",
    "write_pidfile",
    "get_process",
    "is_running",
    "clean_pid_file",
    "daemon_start",
    "daemon_stop",
]


logger = logging.getLogger(__name__)


def process_kill(pid, sig=None):
    sig = sig or signal.SIGINT
    os.kill(pid, sig)


def load_pid(pidfile):
    """read pid from pidfile.
    """
    if pidfile and os.path.isfile(pidfile):
        with open(pidfile, "r", encoding="utf-8") as fobj:
            return int(fobj.readline().strip())
    return 0


def write_pidfile(pidfile):
    """write current pid to pidfile.
    """
    pid = os.getpid()
    if pidfile:
        with open(pidfile, "w", encoding="utf-8") as fobj:
            fobj.write(str(pid))
    return pid


def get_process(pid):
    """get process information from pid.
    """
    try:
        return psutil.Process(pid)
    except psutil.NoSuchProcess:
        return None


def is_running(pid):
    """check if the process with given pid still running
    """
    process = get_process(pid)
    if process:
        return True
    else:
        return False


def clean_pid_file(pidfile):
    """clean pid file.
    """
    if pidfile and os.path.exists(pidfile):
        os.unlink(pidfile)


def daemon_start(main, pidfile, daemon=True, workspace=None):
    """Start application in background mode if required and available. If not then in front mode.
    """
    logger.debug("start daemon application pidfile={} daemon={} workspace={}.".format(pidfile, daemon, workspace))
    new_pid = os.getpid()
    workspace = workspace or os.getcwd()
    os.chdir(workspace)
    if pidfile:
        old_pid = load_pid(pidfile)
        # if old service is running, just exit.
        if old_pid and is_running(old_pid):
            error_message = "Service is running in process: {}.".format(old_pid)
            logger.error(error_message)
            print(error_message, file=os.sys.stderr)
            os.sys.exit(95)
        # clean old pid file.
        clean_pid_file(pidfile)
        # start as background mode if required and available.
        if daemon and os.name == "posix":
            logger.debug("Start application in DAEMON mode, pidfile={} pid={}".format(pidfile, new_pid))
            import daemon # import daemon package only if it is required.
            with daemon.DaemonContext(working_directory=workspace, pidfile=pidfile) as context:
                main()
            return
    logger.debug("Start application in FRONT mode, pid={}.".format(new_pid))
    try:
        write_pidfile(pidfile)
        main()
    finally:
        clean_pid_file(pidfile)
    return


def daemon_stop(pidfile):
    """Stop application.
    """
    logger.debug("stop daemon application pidfile={}.".format(pidfile))
    pid = load_pid(pidfile)
    logger.debug("load pid={}".format(pid))
    if not pid:
        print("Application is not running or crashed...", file=os.sys.stderr)
        os.sys.exit(195)
    process_kill(pid)
    return pid
