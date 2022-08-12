import os
from importlib import import_module
from pathlib import Path
from typing import Callable, Any, Union

import yaml

from easy_python.task_master.args import AT

NoArgsFunc = Callable[[], None]
ArgsFunc = Callable[[AT], None]

_CONFIG_FILE_NAME = "task_master.config.yaml"


def _build_config_func(func_name: str) -> Union[NoArgsFunc, ArgsFunc]:
    module_name, func_name = func_name.rsplit(".", 1)
    module = import_module(module_name)
    return getattr(module, func_name)


class Config:
    tasks_module: str = "tasks"
    pre_parse_func: NoArgsFunc = None
    post_parse_func: ArgsFunc = None
    post_task_func: ArgsFunc = None

    @classmethod
    def update_if_needed(cls) -> None:
        with open(os.path.join(Path().absolute(), _CONFIG_FILE_NAME), "r") as yaml_file:
            config_ = yaml.safe_load(yaml_file) or {}

        for name, val in config_.items():
            cls._update(name, val)

    @classmethod
    def show_default(cls) -> None:
        raise NotImplementedError()

    @classmethod
    def _update(cls, name: str, val: Any):
        if name in ["pre_parse_func", "post_parse_func", "post_task_func"]:
            val = _build_config_func(val)

        setattr(cls, name, val)


def enable_cwd_imports():
    import sys
    sys.path.insert(0, str(Path().absolute()))


def apply_pre_parse_func() -> None:
    if Config.pre_parse_func is None:
        return

    Config.pre_parse_func()


def apply_post_parse_func(args: AT) -> None:
    if Config.post_parse_func is None:
        return

    Config.post_parse_func(args)


def apply_post_task_func(args: AT) -> None:
    if Config.post_task_func is None:
        return

    Config.post_task_func(args)
