"""
Zencore daemon application start(zdas).
"""
import six
from io import open
import os
import errno
import atexit
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


def make_basic_daemon(workspace=None):
    """Make basic daemon.
    """
    workspace = workspace or os.getcwd()
    # first fork
    if os.fork():
        os._exit(0)
    # change env
    os.chdir(workspace)
    os.setsid()
    os.umask(0o22)
    # second fork
    if os.fork():
        os._exit(0)
    # reset stdin/stdout/stderr to /dev/null
    null = os.open('/dev/null', os.O_RDWR)
    try:
        for i in range(0, 3):
            try:
                os.dup2(null, i)
            except OSError as error:
                if error.errno != errno.EBADF:
                    raise
    finally:
        os.close(null)


def process_kill(pid, sig=None):
    """Send signal to process.
    """
    sig = sig or signal.SIGTERM
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
            fobj.write(six.u(str(pid)))
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
    if process and process.is_running() and process.status() != "zombie":
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
    logger.debug("start daemon application pidfile={pidfile} daemon={daemon} workspace={workspace}.".format(pidfile=pidfile, daemon=daemon, workspace=workspace))
    new_pid = os.getpid()
    workspace = workspace or os.getcwd()
    os.chdir(workspace)
    daemon_flag = False
    if pidfile and daemon:
        old_pid = load_pid(pidfile)
        if old_pid:
            logger.debug("pidfile {pidfile} already exists, pid={pid}.".format(pidfile=pidfile, pid=old_pid))
        # if old service is running, just exit.
        if old_pid and is_running(old_pid):
            error_message = "Service is running in process: {pid}.".format(pid=old_pid)
            logger.error(error_message)
            six.print_(error_message, file=os.sys.stderr)
            os.sys.exit(95)
        # clean old pid file.
        clean_pid_file(pidfile)
        # start as background mode if required and available.
        if daemon and os.name == "posix":
            make_basic_daemon()
            daemon_flag = True
    if daemon_flag:
        logger.info("Start application in DAEMON mode, pidfile={pidfile} pid={pid}".format(pidfile=pidfile, pid=new_pid))
    else:
        logger.info("Start application in FRONT mode, pid={pid}.".format(pid=new_pid))
    write_pidfile(pidfile)
    atexit.register(clean_pid_file, pidfile)
    main()
    return


def daemon_stop(pidfile, sig=None):
    """Stop application.
    """
    logger.debug("stop daemon application pidfile={pidfile}.".format(pidfile=pidfile))
    pid = load_pid(pidfile)
    logger.debug("load pid={pid}".format(pid=pid))
    if not pid:
        six.print_("Application is not running or crashed...", file=os.sys.stderr)
        os.sys.exit(195)
    process_kill(pid, sig)
    return pid
