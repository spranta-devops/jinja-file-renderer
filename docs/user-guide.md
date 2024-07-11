# User-Guide

## Install
```shell
pipx install jinja-file-renderer
```

## Upgrade
```shell
pipx upgrade jinja-file-renderer
```

## Usage
The `jinja-file-renderer` can print the usage information: 
```shell
jinja-file-renderer --help
```

The implementation is based on [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) and 
[python-dotenv](https://github.com/theskumar/python-dotenv).

See:
* [dotenv file format](https://github.com/theskumar/python-dotenv?tab=readme-ov-file#file-format)
* [Jinja Template Designer Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/)
  The Template variables are the key-value variables collected from the OS environment variables and dotenv files. 

### Command examples
* Minimal with defaults:
  ```shell
  mkdir /tmp/my-test-output
  jinja-file-renderer --source-dir tests/source-dirs/yaml-files --target-dir /tmp/my-test-output 
  ```
* os.environ should overwrite .env:
  
  By default .env values are overwriting os.environ values.

  "os.env" is a reserved filename for the OS environment variables.

  ```shell
  mkdir /tmp/testJinjaFileRenderer
  # Default is --dotenv os.env .env
  jinja-file-renderer --dotenv .env os.env --source-dir tests/source-dirs/yaml-files --target-dir /tmp/testJinjaFileRenderer 
  ```
* No environment variables, only from some dotenv files:
  
  "os.env" is a reserved filename for the OS environment variables. 
  ```shell
  mkdir /tmp/testJinjaFileRenderer
  # Variables form stage.env are overwriting variables from default.env, if the files exists
  jinja-file-renderer --dotenv default.env stage.env --source-dir tests/source-dirs/yaml-files --target-dir /tmp/testJinjaFileRenderer 
  ```
