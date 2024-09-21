# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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


[Unreleased]: https://github.com/cr1901/pytest-amaranth-sim/compare/v0.1.0..HEAD
[0.1.0]: https://github.com/cr1901/pytest-amaranth-sim/releases/tag/v0.1.0
