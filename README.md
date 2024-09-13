# pytest-amaranth-sim

[![Documentation Status](https://readthedocs.org/projects/pytest-amaranth-sim/badge/?version=latest)](https://pytest-amaranth-sim.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://img.shields.io/pypi/v/pytest-amaranth-sim.svg)](https://pypi.org/project/pytest-amaranth-sim)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-amaranth-sim.svg)](https://pypi.org/project/pytest-amaranth-sim)
[![See Build Status on GitHub Actions](https://github.com/cr1901/pytest-amaranth-sim/actions/workflows/main.yml/badge.svg)](https://github.com/cr1901/pytest-amaranth-sim/actions/workflows/main.yml)

Fixture to automate running Amaranth simulations.

This [pytest] plugin was generated with [Cookiecutter] along with [@hackebrot]'s [cookiecutter-pytest-plugin] template.

## Features

- Automatically set up an Amaranth [pysim](https://github.com/amaranth-lang/amaranth/blob/main/amaranth/sim/pysim.py)
  simulator object fixture `sim`, ready to run testbenches, via `clks` and
  `mod` fixtures.
- Generate [VCDs](https://en.wikipedia.org/wiki/Value_change_dump) for simulations.
  Includes optional workarounds for pytest/GTKWave behavior that I've found
  useful.

## Requirements

- At least Amaranth version `0.5.0` or more recent is required.
- Pytest, of course, is also required, at least version `6.2.0`.

## Installation

`pytest-amaranth-sim` is available on [PyPI]:

```
$ pip install pytest-amaranth-sim
```

If using this plugin as part [PDM], you can install using `pdm add`:

```
$ pdm add -G dev pytest-amaranth-sim
```

To follow development, use the [git repo](https://github.com/cr1901/pytest-amaranth-sim):

```
$ pip install [-e] git+https://github.com/cr1901/pytest-amaranth-sim
```

```
$ pdm add -G dev git+https://github.com/cr1901/pytest-amaranth-sim
```

## Usage

```python
import pytest
from amaranth import Elaboratable, Signal, Module


class Adder(Elaboratable):
    def __init__(self, width=4):
        self.width = width
        self.a = Signal(width)
        self.b = Signal(width)
        self.o = Signal(width + 1)

    def elaborate(self, plat):  # noqa: D102
        m = Module()

        m.d.sync += self.o.eq(self.a + self.b)

        return m


@pytest.fixture
def testbench(mod, a, b, o):
    if (a,b,o,mod.width) == (127, 127, 254, 4):
        return pytest.skip(reason="inputs too wide")

    async def testbench(sim):
        await sim.tick()

        sim.set(mod.a, a)
        await sim.tick()
        assert sim.get(mod.o) == a
        sim.set(mod.b, b)
        await sim.tick()
        assert sim.get(mod.o) == o

    return testbench


@pytest.mark.parametrize("a,b,o", [(0, 0, 0), (1, 1, 2), (127, 127, 254)])
@pytest.mark.parametrize("mod", [Adder(4), Adder(8)])
@pytest.mark.parametrize("clks", [1.0 / 12e6])
def test_inject_direct(sim, testbench):
    sim.run(testbenches=[testbench], processes=[])
```

Save inside your test directory to a file that matches the glob `test_*.py`
(see [pytest docs](https://docs.pytest.org/en/stable/explanation/goodpractices.html#conventions-for-python-test-discovery)
for more info). Run with:

```sh
pytest [--vcds]
```

## Contributing

Contributions are very welcome. Tests can be run with [pytest] (`pdm test`),
please ensure the coverage at least stays the same before you submit a pull
request.

## License

Distributed under the terms of the [BSD-2] license, "pytest-amaranth-sim" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[@hackebrot]: https://github.com/hackebrot
[apache software license 2.0]: https://www.apache.org/licenses/LICENSE-2.0
[bsd-3]: https://opensource.org/licenses/BSD-2-Clause
[cookiecutter]: https://github.com/audreyr/cookiecutter
[cookiecutter-pytest-plugin]: https://github.com/pytest-dev/cookiecutter-pytest-plugin
[file an issue]: https://github.com/cr1901/pytest-amaranth-sim/issues
[gnu gpl v3.0]: https://www.gnu.org/licenses/gpl-3.0.txt
[mit]: https://opensource.org/licenses/MIT
[pip]: https://pypi.org/project/pip/
[pypi]: https://pypi.org/project
[pytest]: https://github.com/pytest-dev/pytest
[tox]: https://tox.readthedocs.io/en/latest/
[pdm]: https://pdm-project.org/en/latest/
