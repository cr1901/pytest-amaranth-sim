# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-02-17

### Added
- Add support for multiple clock domains in the `clks` fixture, including
  [incorporating](https://docs.pytest.org/en/stable/reference/reference.html#pytest.hookspec.pytest_make_parametrize_id)
  each clock into the generated test name.
- Add support for [background testbenches] via the `Testbench` dataclass.
- CI now tests publishing each commit to [TestPyPI](https://test.pypi.org/).
  - Package is published to [PyPI](https://pypi.org/) only if commit is tagged
    _and_ the TestPyPI step succeeds.
- CI now tests Python versions `3.13`, `3.14`, and PyPy versions
  `3.8` through `3.11`.

### Changed
- The package version is rewritten during build step of CI to conform to PyPI
  rules of disallowing [local versions](https://packaging.python.org/en/latest/specifications/version-specifiers/#local-version-identifiers).
  - Version-rewriting should have no effect on tags/releases because PDM's
    [default version formatter] is used directly in those cases.
- Use Sybil in place of `pytest-sphinx` for checking doctests.
  - `testcode` directives are replaced with the `doctest` directive.

### Fixed
- The `test_comb_testbench_fail` test and its failure modes now more thoroughly
  tested/described.
- "How To Use These Fixtures" documentation is improved, with code examples!
  - There is still room to improve those docs' prose.
- Use [`sphinx-autofixture`](https://github.com/sphinx-toolbox/sphinx-autofixture)
  to explicitly mark Pytest fixtures provided by this plugin.

### Removed
- Remove `flake8` and use `ruff` `v0.14.1`'s [preview](https://docs.astral.sh/ruff/settings/#preview)
  mode for the implemented [pydoclint subset](https://docs.astral.sh/ruff/rules/#pydoclint-doc)
  instead.
  - `.flake8` settings were transferred to `tool.ruff` table of
    `pyproject.toml` on a best-effort basis.


## [0.1.0] - 2024-09-21

Initial release.

### Added
- Add pytest plugin for running simulations of digital logic using [Amaranth's](https://amaranth-lang.org/)
  Python simulator. The plugin does the following:

  - Add fixtures for interacting with the Amaranth simulator. As this targets
    Amaranth 0.5, both the deprecated generator-based and `async`-based
    testbenches are supported.

  - Add pytest [configuration options](https://docs.pytest.org/en/stable/reference/customize.html#configuration)
    to work around a GTKWave [quirk](https://github.com/gtkwave/gtkwave/issues/230),
    create [VCD](https://en.wikipedia.org/wiki/Value_change_dump) files, and
    configure how VCD files are named.

- All plugin functionality is documented, and tested against Python versions
  `3.8` through `3.12`.

[background testbenches]: https://amaranth-lang.org/docs/amaranth/v0.5.8/simulator.html#amaranth.sim.Simulator.add_testbench
[default version formatter]: https://github.com/pdm-project/pdm-backend/blob/263a598db674fcc0ee03fcd2414bea454a28b6a3/src/pdm/backend/hooks/version/scm.py#L326-L341

[Unreleased]: https://github.com/cr1901/pytest-amaranth-sim/compare/v0.1.1..HEAD
[0.1.1]: https://github.com/cr1901/pytest-amaranth-sim/compare/v0.1.0..v0.1.1
[0.1.0]: https://github.com/cr1901/pytest-amaranth-sim/releases/tag/v0.1.0
