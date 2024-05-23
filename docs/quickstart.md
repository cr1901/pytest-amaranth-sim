# Quick Start

## Features

- Automatically set up an Amaranth [pysim](https://github.com/amaranth-lang/amaranth/blob/main/amaranth/sim/pysim.py)
  simulator object fixture `sim`, ready to run testbenches.
  - Top-level [`Elaboratable`s](https://amaranth-lang.org/docs/amaranth/latest/guide.html#elaboration)
    are passed to the `sim` fixture by [overrding](https://docs.pytest.org/en/stable/how-to/fixtures.html#override-a-fixture-with-direct-test-parametrization) the `mod` and `clks`
    fixtures at a test function or class.
- Command-line option to generate [VCDs](https://en.wikipedia.org/wiki/Value_change_dump)
  for run simulations (`--vcds`)
  - VCDs filename verbosity is configurable (`long_vcd_filenames`).
  - When a testbench fails, optionally extend the output VCD trace so that the
    failing state is more visible at lower zooms (`extend_vcd_time`). See
    [this issue](https://github.com/gtkwave/gtkwave/issues/230#issuecomment-2065663811)
    for an example of why this workaround exists).

## Requirements

- At least Amaranth commit `89eae72` or more recent is required.
  - The first release version that will be supported is 0.5.
- Pytest, of course, is also required, at least version 6.2.0.
  - Development tracks whatever version of `pytest` is in the PDM
    [lock file](https://pdm-project.org/latest/usage/lockfile/). This is not
    an elaborate plugin; it is unlikely to take advantage of recent Pytest
    functionality.

## Installation

You can install "pytest-amaranth-sim" via [pip] from the [git repo](https://github.com/cr1901/pytest-amaranth-sim):

```
$ pip install [-e] git+https://github.com/cr1901/pytest-amaranth-sim
```

A [PyPI] release is pending the release of Amaranth 0.5.

## Basic Example

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

The {doc}`Usage <usage>` section elaborates on how to effectively set up
testbenches and VCD waveforms using this plugin.

[pip]: https://pypi.org/project/pip/
[pypi]: https://pypi.org/project
