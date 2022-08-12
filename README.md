## This repo tries to make your life easier! 

Currently, the biggest feature that this repo offers is a `task_master` module which primarily handles task management 
in the project. 

Additional features are `terminal_args` which makes command line arguments parsing much nicer and some `pandas` utils.

To take advantage of what we offer, you need to first install the `easy_python` package. We recommend doing it 
in a virtual environment.

```angular2html
git clone <REPO>
python install.py
```

After executing these 2 commands, our package will be already available in your environment.

You can use our features either by importing them from within your code and you can also use the terminal command.

For example, if you'd like to create a project structure skeleton, you can use `task_master-start`. Here, you can also 
provide a few additional options:
```angular2html
$ task_master-start -h
usage: task_master-start [-h] [--location LOCATION] [--with_config WITH_CONFIG] [--with_example WITH_EXAMPLE] [--with_git WITH_GIT]

optional arguments:
  -h, --help                    show this help message and exit
  --location LOCATION           Location where a new project should be created
  --with_config WITH_CONFIG     Flag whether to create a config file
  --with_example WITH_EXAMPLE   Flag whether to add example
  --with_git WITH_GIT           Flag whether to init git
```

That's being said, in the beginning we recommend to start off with `task_master-start --with_example True` to see how 
the tasks can be registered.

Then, the example task can be launched using `task_master hello_world`.

And, this `task_master` command can actually start any of your tasks. As a first argument after the command you have to 
specify a name of the task you registered in your project, and then you can follow it with any dashed (`--`) arguments 
necessary to execute your task.
