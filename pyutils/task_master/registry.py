import inspect
import os
from importlib import import_module
from pathlib import Path
from typing import Dict, Type, Callable, Any

from easy_python.task_master.args import AT, BaseArgs
from easy_python.terminal import args_params, terminal_args

TaskFunc = Callable[..., None]


def _does_task_exist(task_name: str, extension=".py") -> bool:
    from easy_python.task_master.config import Config

    tasks_path = os.path.join(Path().absolute(), Config.tasks_module)
    for module_path, dir_names, script_names in os.walk(tasks_path):
        for script_name in script_names:
            if script_name.startswith("__") or not script_name.endswith(extension):
                continue

            parent_modules = module_path[len(tasks_path):]
            if parent_modules:
                parent_modules = f"{parent_modules.replace(os.sep, '.')[1:]}."

            script_module_name = f"{Config.tasks_module}.{parent_modules}{script_name[:-len(extension)]}"
            import_module(script_module_name)

            if task_name in _REGISTRY:
                return True

    return False


def _attribute_generator(parameter):
    is_param_required = parameter.default is parameter.empty
    required_or_default_text = (f"required." if is_param_required else
                                f"optional and has the default value {parameter.default}.")
    return args_params(type=parameter.annotation,
                       required=is_param_required,
                       default=None if is_param_required else parameter.default,
                       help=f"Automatically generated hint for "
                            f"{parameter.name}. "
                            f"Type should be {parameter.annotation}. "
                            f"This parameter is {required_or_default_text}")


class Task:
    __slots__ = ("_name", "_args_cls", "_func", "_uses_func_params")

    def __init__(self, name: str, args_cls: Type[AT], func: TaskFunc, uses_func_params: bool):
        self._name = name
        self._args_cls = args_cls
        self._func = func
        self._uses_func_params = uses_func_params

    @property
    def name(self):
        return self._name

    def parse_args(self) -> AT:
        return self._args_cls()

    def execute(self) -> None:
        if self._uses_func_params:
            from easy_python.task_master.storage import args
            func_kwargs = {attr: getattr(args(), attr) for attr in set(args().__slots__) - set(BaseArgs.__slots__)}
            self._func(**func_kwargs)
        else:
            self._func()


_REGISTRY: Dict[str, Task] = {}


class IncorrectTask(Exception):
    def __init__(self, task_name: str):
        global _REGISTRY
        super(IncorrectTask, self).__init__(f"Wrong `task` argument given: '{task_name}' isn't registered.\n"
                                            f"Currently registered tasks: {', '.join(list(_REGISTRY.keys()))}")


class DynamicArgumentException(Exception):
    def __init__(self, dynamic_argument_error: str):
        super(DynamicArgumentException, self).__init__(dynamic_argument_error)


def register(func: TaskFunc = None, name: str = None, args_cls: Type[AT] = None):
    def _register(_func: TaskFunc):
        nonlocal name
        if name is None:
            name = _func.__name__

        dynamic_args_cls = None
        func_params = inspect.signature(_func).parameters.values()
        if len(func_params) > 0:
            if args_cls is not None:
                raise DynamicArgumentException("You can't register a function "
                                               "with parameters and an args class at the same time!")

            dynamic_class_attributes = {}
            problematic_parameters = []
            for parameter in func_params:
                if parameter.annotation is parameter.empty:
                    raise DynamicArgumentException("You can't register a function "
                                                   "with parameters that don't have type annotations!")

                if parameter.name in set(BaseArgs.__slots__):
                    problematic_parameters.append(parameter.name)

                dynamic_class_attributes[parameter.name] = _attribute_generator(parameter)

            if problematic_parameters:
                raise DynamicArgumentException("You can't register a function "
                                               "where parameter name can be found in BaseArgs! "
                                               f"Problematic parameters name: {problematic_parameters}")

            dynamic_args_cls = terminal_args(type(f"DynamicArgs_{name}", (BaseArgs,), dynamic_class_attributes))

        _REGISTRY[name] = Task(name, dynamic_args_cls or args_cls or BaseArgs, _func, dynamic_args_cls is not None)

        return _func

    return _register if func is None else _register(func)


def select_task(task_name: str) -> Task:
    if not _does_task_exist(task_name):
        raise IncorrectTask(task_name)
    # TODO: think what errors can occur and make their exceptions more explanatory

    return _REGISTRY[task_name]
