from setuptools import setup

setup(
    name="pyutils",
    version="0.0.1",
    description="Useful module making Python easier",
    author="Kuba Jazdzyk",
    author_email="jazdzyk.kuba@gmail.com",
    packages=["pyutils", "pyutils.task_master", "pyutils.task_master.extras"],
    entry_points={
        "console_scripts": [
            "task_master=pyutils.task_master.master:run",
            "task_master-start=pyutils.task_master.start:create_project_structure"
        ],
    }
)
