import os
from pathlib import Path
from typing import Dict, Union, Optional

from easy_python.terminal import terminal_args, args_params

FilesContent = Dict[str, Optional[str]]


def _example_content():
    return """from easy_python.task_master import register


@register
def hello_world():
    print("Hello World!")
"""


def _example_config_content():
    return """from easy_python.task_master import AT


def post_parse_example_func(args: AT):
    print(f"This is an example config function run after parsing.\\nCurrent args = {args}")
    
    
def post_task_example_func(args: AT):
    print(f"This is an example config function run after the task execution has finished.\\nCurrent args = {args}")
"""


def _example_yaml_config_content():
    return """post_parse_func: config.functions.post_parse_example_func
post_task_func: config.functions.post_task_example_func"""


def _how_to_run_content():
    return """# To run the example task, just type the following in the command line:
task_master hello_world
"""


@terminal_args
class StartArgs:
    location = args_params(type=str, help="Location where a new project should be created")

    with_config = args_params(type=bool, default=True, help="Flag whether to create a config file")
    with_example = args_params(type=bool, default=False, help="Flag whether to add example")
    with_git = args_params(type=bool, default=True, help="Flag whether to init git")


class ProjectStructure:

    def __init__(self):
        self._args = StartArgs()
        self._root_dir = self._args.location or Path().absolute()

    def create(self) -> None:
        os.makedirs(self._root_dir, exist_ok=True)
        os.chdir(self._root_dir)

        if self._args.with_git:
            os.system("git init")
            self._create_file(self._root_dir, ".gitignore")

        tasks_dir = self._create_python_dir(self._root_dir, "tasks")

        yaml_config_name = None
        if self._args.with_config:
            yaml_config_name = self._create_file(self._root_dir, "task_master.config.yaml")

        args_data = {}

        self._create_python_dir(self._root_dir, "args", args_data)
        config_dir = self._create_python_dir(self._root_dir, "config", args_data)

        if self._args.with_example:
            self._create_python_dir(tasks_dir, "example", {"hello.py": _example_content()})
            self._create_file(config_dir, "functions.py", _example_config_content())
            self._create_file(self._root_dir, "HOW_TO_RUN.txt", _how_to_run_content())

            if self._args.with_config:
                self._append_to_file(yaml_config_name, _example_yaml_config_content())

    def _create_python_dir(self, root_path: Union[str, Path], name: str, files_content: FilesContent = None) -> str:
        if files_content is None:
            files_content = {}

        dir_path = os.path.join(root_path, name)
        os.makedirs(dir_path, exist_ok=True)

        self._create_file(dir_path, "__init__.py")

        for file_name, content in files_content.items():
            if content is None:
                content = ""

            self._create_file(dir_path, file_name, content)

        return dir_path

    @staticmethod
    def _create_file(dir_path: Union[str, Path], name: str, content=""):
        dir_init_path = os.path.join(dir_path, name)
        if not os.path.exists(dir_init_path):
            with open(dir_init_path, "w") as file:
                file.write(content)

        return dir_init_path

    @staticmethod
    def _append_to_file(file_path: str, content: str):
        with open(file_path, "a") as file:
            file.write(content)


def create_project_structure():
    structure = ProjectStructure()
    structure.create()
