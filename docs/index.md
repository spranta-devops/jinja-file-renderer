# jinja-file-renderer
A tool for copying a directory, during which *.jinja files are rendered via Jinja2.

It helps in the development of applications following the [12-factor](https://12factor.net/) principles.

## Motivation
As a DevOps engineer in the Kubernetes environment, I would like to be able to dynamically design and create files 
using templating in the as-code approach (GitOps, CI/CD pipelines). Pipeline variables from the CI/CD products 
(environment variables) should be able to be used in the template files. Jinja is a very good template rendering 
engine that is also well known in the DevOps community.

Usually there is a directory with mixed files. Some files should be used as-is and some should be used as templates. 
IDEs should support the template files with linting and code-completion. 
Luckily some IDEs are supporting "*.html.jinja" or "*.yaml.jinja" files, or can be extended to do so.  

## How does it work?
* The target-directory will not be created. The tool aborts when it does not exist.
* The content of a source-directory will be scanned traversal.
* By default, the environment variables will be read and can be used in the template-files.
  The [python-dotenv](https://pypi.org/project/python-dotenv/) lib is used to add and overwrite environment variables 
  from a ".env" file if exists.
  * See [dotenv file format](https://github.com/theskumar/python-dotenv?tab=readme-ov-file#file-format)
  * You can change the collection of environment variables with the "--dotenv" argument. The order and files to search 
    for.
* A non-"*.jinja"-file will be copied to the target-directory (same sub-dir) as-is.
* A "*.jinja"-file will be rendered via Jinja2 and written renamed (without ".jinja" suffix) to the target-directory 
  (same sub-dir).
