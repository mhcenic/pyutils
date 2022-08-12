__all__ = [
    'args_params',
    'terminal_args',
    'Config',
]

from argparse import ArgumentParser
from types import ModuleType
from typing import List, Any, Union, Dict, Tuple, Callable

# ---------------------------------------------------------------------------------------------------------------------
# CUSTOM TYPES
# ---------------------------------------------------------------------------------------------------------------------
Config = Union[ModuleType, type]
Attrs = List[str]
AttrsDict = Dict[str, Any]
ParserParams = List[Tuple[str, tuple, dict]]
ArgGetter = Callable[[str], Any]

# ---------------------------------------------------------------------------------------------------------------------
# PRIVATE
# ---------------------------------------------------------------------------------------------------------------------
_DEFAULT_ARGUMENTPARSER_ARGS = ["name_or_flags", "action", "nargs", "const", "default", "type", "choices", "required",
                                "help", "metavar", "dest"]

__INITIAL_FIELDS = {}
__READ_ONLY_FIELDS = {}

_NEW_TAB_LINE = "\n\t"


def _get_initial_fields(cls: type):
    return __INITIAL_FIELDS.get(cls.__name__, [])


def _set_initial_fields(cls: type, params: ParserParams):
    __INITIAL_FIELDS[cls.__name__] = params


def _set_read_only_fields(cls: type, params: ParserParams, cls_read_only: bool):
    read_only_fields = set()

    for param in params:
        is_read_only = param[2].get("read_only")
        if ((is_read_only is None and not cls_read_only
             and not any([_is_field_read_only(parent_cls, param[0]) for parent_cls in cls.__mro__]))
                or is_read_only is False):
            continue

        read_only_fields.add(param[0])

    __READ_ONLY_FIELDS[cls.__name__] = read_only_fields


def _is_field_read_only(cls: type, name: str) -> bool:
    return name in __READ_ONLY_FIELDS.get(cls.__name__, {})


def _read_attrs(cls: type) -> List[str]:
    return [key for key in cls.__dict__ if not key.startswith("__")]


def _fetch_base_attrs(cls: type):
    base_attrs = set()
    for _cls in cls.__mro__:
        for data in _get_initial_fields(_cls):
            base_attrs.add(data[0])
    return list(base_attrs)


def _fetch_base_parsing_params(cls: type):
    params = []

    for base_cls in cls.__mro__:
        params += _get_initial_fields(base_cls)

    return params


def _is_default_eligible(config: Config, dict_: AttrsDict):
    return config is not None and not dict_.get("required", False)


def _handle_default(cls: type, attrs: Attrs, config: Config, with_base_defaults: bool) -> ParserParams:
    def read_default(name: str):
        return getattr(config, name, None)

    parsing_params = []

    for attr in attrs:
        if _is_default_eligible(config, cls.__dict__[attr][1]):
            cls.__dict__[attr][1]["default"] = read_default(attr)

        parsing_params.append((attr, cls.__dict__[attr][0], cls.__dict__[attr][1]))

    for params in _fetch_base_parsing_params(cls):
        if not with_base_defaults:
            params = list(params)
            params[2] = params[2].copy()
            params[2]["default"] = read_default(params[0]) if _is_default_eligible(config, params[2]) else None
            params = tuple(params)
        parsing_params.append(params)

    return parsing_params


def _update_config(config: Config, attrs: Attrs, getter: ArgGetter):
    for attr in attrs:
        setattr(config, attr, getter(attr))


def _parse_arguments(params: ParserParams):
    def _remove_extra_arg_params(arg_param_dict: Dict[str, Any]):
        for arg_prop in list(arg_param_dict):
            if arg_prop in _DEFAULT_ARGUMENTPARSER_ARGS:
                continue

            arg_param_dict.pop(arg_prop, None)

    def _convert_type_if_needed(arg_param_dict: Dict[str, Any]):
        type_ = arg_param_dict["type"]

        if type_ is bool:
            arg_param_dict["type"] = _to_bool
        elif type_ is list:
            arg_param_dict["type"] = _to_list
        # TODO: think if any other types need conversion

    parser = ArgumentParser()

    for arg_name, param_tuple, param_dict in params:
        if not param_dict.get("main", False):
            arg_name = f"--{arg_name}"

        _remove_extra_arg_params(param_dict)
        _convert_type_if_needed(param_dict)

        param_args = [arg_name] + [f"-{abbrev}" for i, abbrev in enumerate(param_tuple) if i == 0]
        parser.add_argument(*param_args, **param_dict)

    return parser.parse_args()


def _repr_format(s: Any):
    if isinstance(s, str):
        return f"'{s}'"

    return s


# TODO: maybe these converters could be placed in another file or class?
def _to_list(s: str, delimiter=",") -> List[str]:
    return s.split(delimiter)


def _to_bool(s: str) -> bool:
    return s.lower() in ["true", "t", "1", "yes", "y"]


# ---------------------------------------------------------------------------------------------------------------------
# PUBLIC
# ---------------------------------------------------------------------------------------------------------------------
def args_params(*vargs, **kwargs):
    return vargs, kwargs


def terminal_args(cls: type = None, config: Config = None, with_base_defaults=True, read_only=False):
    def _args(_cls: type):
        attrs = _read_attrs(_cls)
        base_attrs = _fetch_base_attrs(_cls)
        all_attrs = attrs + base_attrs

        parsing_params = _handle_default(_cls, attrs, config, with_base_defaults)
        _set_initial_fields(_cls, parsing_params)
        _set_read_only_fields(_cls, parsing_params, read_only)

        parsed_args = None

        def _get_arg(name: str):
            return getattr(parsed_args, name, None)

        def _set_arg(name: str, value: Any):
            setattr(parsed_args, name, value)

        class _Args:
            __slots__ = tuple(all_attrs)

            def __init__(self):
                nonlocal parsed_args
                parsed_args = _parse_arguments(_get_initial_fields(_cls))

                if config is not None:
                    _update_config(config, all_attrs, _get_arg)

                if "__post_parse__" in _cls.__dict__:
                    _cls.__post_parse__(self)

            def __getattr__(self, name: str):
                if name not in _Args.__slots__:
                    raise AttributeError(f"{_cls.__name__} has no attribute '{name}'.")

                return _get_arg(name)

            def __setattr__(self, name: str, value: Any):
                if _is_field_read_only(_cls, name):
                    raise AttributeError(f"The `{name}` attribute of {_cls.__name__} is read only.")

                _set_arg(name, value)

            def __repr__(self):
                values_strings = [f"{attr}={_repr_format(_get_arg(attr))}" for attr in all_attrs]
                return (f"<{_cls.__name__}{_NEW_TAB_LINE if len(values_strings) > 1 else ' '}"
                        f"{_NEW_TAB_LINE.join(values_strings)}" + ("\n" if len(values_strings) > 1 else "") + ">")

        _Args.__name__ = _cls.__name__
        _Args.__qualname__ = _cls.__qualname__

        return _Args

    return _args if cls is None else _args(cls)
