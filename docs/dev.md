# Development Guidelines

```{todo} This whole section needs to be written. The general gist is:

* We use PDM at the package manager/virtual env for isolation.
  * `pdm test` for Pytest, `pdm doc` for Sphinx, etc.
* We also use PDM's build backend as the build system, but this can be
  interfaced to via `pip`.
* We use `pytest`'s `Pytester` plugin to test our plugin.
  * See `[tool.pytest.ini_options]` for `pytest` config required for tests
    to function properly (including `doctest`s).
  * Doctests that are _not_ intended to be invoked via `pytest` are nominally
    run through `pytest-sphinx`.
    * `pdm doc-test`, which calls `sphinx-build -b doctest`, is provided as a
      fallback in case `pytest-sphinx` [misses](https://github.com/twmr/pytest-sphinx/issues/65)
      a doctest.
  * AFAICT, it is not possible to invoke `Pytester` through doctest, so
    all Python code in docs _and_ intended to be _invoked via pytest_ is
    duplicated in `test_inject.py`, and run as part of the main `pytest` suite
    (`test_inject_sim_args`).
* Linting is done with a combination of `ruff`, `pydoclint`, and transitively,
  `flake8`.
  * `flake8` usage is minimized to `pydoclint` and lints that are unstable
    in `ruff`. See `.flake8` file (`flake8` doesn't support `pyproject.toml`).
  * Eventually, this should go down to only `ruff`, when the `pydoclint`
    functionality and extra `flake8` lints are stabilized. See `[tool.ruff]`
    section in `pyproject.toml` and compare to `.flake8`; lint rule overlap
    should be minimized.
* Docs are written in Markdown using `myst` when possible.

```
