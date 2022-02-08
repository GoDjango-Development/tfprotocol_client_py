from functools import wraps
from typing import Any, Callable, Dict, Union
from tfprotocol_client.models.exceptions import ErrorCode, TfException
from tfprotocol_client.models.status_info import StatusInfo

ExceptionHandler = Callable[[Exception], Any]


def raise_from(excp: Exception):
    """Raise TfException from regular exceptions.

    Args:
        excp (Exception): Regular exceptions raised to feed TfExceptions.

    Raises:
        TfException: Custom exception
    """
    raise TfException(exception=excp)


def get_raise_exceptions_handler(
    message: str = None,
    code: Union[int, ErrorCode, None] = None,
    status_info: StatusInfo = None,
):
    """Retrieves a exception handler.

    Args:
        message (str, optional): Exception message. Defaults to None.
        code (Union[int, ErrorCode, None], optional): Error code. Defaults to None.
        status_info (StatusInfo, optional): Status info. Defaults to None.
    """

    def _raise_from(excp: Exception):
        raise TfException(
            exception=excp, message=message, code=code, status_info=status_info,
        )

    return _raise_from


def on_except(
    dflt_handler: ExceptionHandler = None, **handlers: Dict[str, ExceptionHandler]
):
    """Handle exceptions or wraps exceptions and re-raise.

    Args:
        `dflt_handler` (ExceptionHandler): Default handler for exceptions.
        `**handlers` (Dict[str, ExceptionHandler]): Handlers dictionary exception name
        to handler function.
    """

    def _on_except(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as excp:
                handler = handlers.get(excp.__class__.__name__, dflt_handler)
                if handler is None:
                    raise excp
                return handler(excp)

        return _wrapper

    return _on_except


def exception_raise_guard(func):
    @wraps(func)
    def _exception_raise_guard(*args, **kwargs):
        self = args[0]
        if self.socket is None or not self.is_connect():
            raise TfException(
                message="Socket is closed or not connected",
                code=ErrorCode.ON_WRITE_OR_RECEIVE_TO_SOCKET,
            )
        return func(*args, **kwargs)

