# Developer Guide
The source code is hosted on [GitHub](https://github.com/spranta-devops/jinja-file-renderer/), you can "git clone" the
repository from there.

This project was developed under linux. The following guidelines and hints are tested on linux only.

## tl/tr
run without building, while developing
```shell
mkdir out
hatch run jinja-file-renderer \
  --log-level DEBUG \
  --delete-target-dir-content \
  --source-dir tests/source-dirs/yaml-files \
  --target-dir out
```

## Developing Environment
The development environment is based on the guide of pytest: https://docs.pytest.org/en/8.2.x/explanation/goodpractices.html

### direnv
[direnv](https://direnv.net/) is prepared to automatically create a venv for developing with an IDE.
This is optional.

## Hatch basics
[Hatch](https://hatch.pypa.io/latest/) is used as a lint, test and build system.
Hatch manages multiple venv environments with different Python versions and dependencies. For each environment multiple 
scripts can be prepared, making the usage of development tools quite easy.

* show environments, also internal
  Get an overview of all prepared environments and scripts (last column). 
  ```shell
  hatch env show
  hatch env show -i
  ```
* create an env from "hatch env show -i" output, so that an IDE can use it
  ```shell
  hatch env create hatch-test.py3.12
  hatch env find hatch-test.py3.12
  ## Use the output (path) to point your IDE Python venv to it.
  ## (The direnv does the same.)
  ```
* execute built-in commands
  The internal environments are used for the built-in commands:
  ```shell
  hatch fmt --help
  ```
  ```shell
  hatch test --help
  ```
* execute scripts from column "scripts", some examples
  ```shell
  hatch run mkdocs:serve
  ```
  ```shell
  hatch run mkdocs:build
  ```
