# Release Guide
A CI/CD pipeline should do this.

## check release notes
Check and fix docs/about/release-notes.md

## lint
```shell
hatch fmt --check
```

## test
* Test with all supported Python versions.
  ```shell
  hatch test --all
  ```
* Tests with coverage
  ```shell
  hatch test --all --cover
  ```

## versioning
See details: https://waylonwalker.com/hatch-version/
* print current version
  ```shell
  hatch version
  ```
* set version
  ```shell
  hatch version 1.2.3
  ```
(The version should be set in `src/jinja_file_renderer/__about__.py`.)

## build
* build python app
  ```shell
  hatch build
  ```
* build documentation for "readthedocs"
  ```shell
  hatch run mkdocs build
  ```

## publish
### to https://test.pypi.org
hatch publish -r test
### to https://pypi.org
todo: publish pypa
todo: publish readthedocs
