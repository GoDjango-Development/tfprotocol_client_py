from threading import Lock, Thread
from typing import Any, Callable, Iterable, Mapping
from tfprotocol_client.models.exceptions import TfException


class TfThread(Thread):
    """Represents a thread control, for multithreaded tasks"""

    HANDLED_THREAD = None

    def __init__(
        self,
        target: Callable[..., Any],
        quite_errors: bool = False,
        lock: Lock = None,
        name: str = ...,
        args: Iterable[Any] = ...,
        kwargs: Mapping[str, Any] = ...,
        *,
        daemon: bool = ...,
    ) -> None:
        """Preparation for the thread execution.

        Args:
            `target` (Callable[..., Any]): The method who is going to be used asynchronous.
            `quite_errors` (bool, optional): Raise silently exceptions.
            `lock` (Lock, optional): The mutex that is going to be informed when the method
                execution reach its end. Defaults to None.
            `name` (str, optional): Thread name. Defaults to ....
            `args` (Iterable[Any], optional): Postitional arguments to be passed to method
                call, must be set at the exactly order required by the method.
            `kwargs` (Mapping[str, Any], optional): Keyword arguments to be passed to method
                call.
            `daemon` (bool, optional): Demonize the thread.
        """
        super().__init__(name=name, args=args, kwargs=kwargs, daemon=daemon)
        self.lock = lock if lock else Lock()
        self._quite_errors = quite_errors
        self._method = target

    def setup_args(self, args: Iterable[Any] = ..., kwargs: Mapping[str, Any] = ...):
        """Set up arguments for the method.

        Args:
            args (Iterable[Any], optional): Postitional arguments to be passed to method
                call, must be set at the exactly order required by the method.
            kwargs (Mapping[str, Any], optional): Keyword arguments to be passed to method
                call.
        """
        self._args = args
        self._kwargs = kwargs

    def run(self) -> None:
        """Method representing the thread's activity.

        Raises:
            `TfException`: _description_
        """
        try:
            self._method(*self._args, **self._kwargs)
        except Exception as e:  # pylint: disable=broad-except
            if not self._quite_errors:
                raise TfException(
                    exception=e,
                    message=f'{self.getName()}:\n {self._method.__name__}()',
                )
        finally:
            self._stop()
    
    def interrupt(self):
        self._quite_errors = True
        self._stop()
    
    def set_handled_t(self):
        self.__class__.HANDLED_THREAD = self
