# coded by lagcleaner
# email: lagcleaner@gmail.com

from threading import Thread


class TimeLimitExpired(Exception):
    """This exception is raised when the operation is timed out."""


def timelimit(timeout, func, *args, **kwargs):
    """ Run func with the given timeout. If func didn't finish running
        within the timeout, raise TimeLimitExpired
    """

    class FuncThread(Thread):
        """Class to run a function with a timeout."""

        def __init__(self):
            Thread.__init__(self)
            self.result = None

        def run(self):
            self.result = func(*args, **kwargs)

        def stop(self):
            if self.is_alive():
                self._stop()

    it = FuncThread()
    it.start()
    it.join(timeout)
    if it.is_alive():
        it.stop()
        raise TimeLimitExpired()
    else:
        return it.result
