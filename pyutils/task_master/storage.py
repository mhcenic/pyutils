from easy_python.task_master.args import AT

_args: AT = None


def update_args(new_args: AT):
    global _args
    _args = new_args


def args() -> AT:
    return _args
