import sys

from easy_python.task_master import registry, storage
from easy_python.task_master.config import Config, enable_cwd_imports, apply_post_parse_func, apply_post_task_func, \
    apply_pre_parse_func


def _fetch_task_name() -> str:
    return sys.argv[1] if len(sys.argv) > 1 or not sys.argv[1].startswith("--") else None


def run():
    # -- INITIAL CONFIGURATION --
    enable_cwd_imports()
    Config.update_if_needed()

    # -- PROGRAM LIFE-CYCLE STARTS --
    apply_pre_parse_func()

    task_name = _fetch_task_name()
    task = registry.select_task(task_name)

    storage.update_args(task.parse_args())

    apply_post_parse_func(storage.args())
    task.execute()
    apply_post_task_func(storage.args())
