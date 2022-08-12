from typing import Callable, Optional, Any

from easy_python.task_master.storage import args as term_args


def if_debug(func: Callable) -> Callable:
    def _if_debug(*args, **kwargs) -> Optional[Any]:
        if term_args().debug_mode:
            return func(*args, **kwargs)

    return _if_debug


def if_experimental(func: Callable) -> Callable:
    def _if_experimental(*args, **kwargs) -> Optional[Any]:
        if term_args().experimental_mode:
            return func(*args, **kwargs)

    return _if_experimental


def if_logging(func: Callable) -> Callable:
    def _if_logging(*args, **kwargs) -> Optional[Any]:
        if term_args().logging_mode:
            return func(*args, **kwargs)

    return _if_logging
