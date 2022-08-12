from typing import TypeVar

from easy_python.terminal import terminal_args, args_params


@terminal_args
class BaseArgs:
    task = args_params(type=str, main=True, help="Task to be executed")

    debug_mode = args_params(type=bool, default=False, help="Flag whether to enable debug mode")
    experimental_mode = args_params(type=bool, default=False, help="Flag whether to enable experimental mode")
    logging_mode = args_params(type=bool, default=False, help="Flag whether to enable logging mode")


AT = TypeVar("AT", bound=BaseArgs)
