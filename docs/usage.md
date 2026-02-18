# Usage

## Why Make A Sim Wrapper At All?

As alluded to in the {doc}`quickstart <quickstart>`, `pytest-amaranth-sim`
doesn't do that much on its own. However, I've found `pytest` {doc}`fixtures <pytest:reference/fixtures>`
to be extremely effective in deduplicating test setup code and to create more 
test cases. So I went ahead and created this plugin based on my own experiences
repeatedly implementing small fixtures, so that all my shared code is in one
place.

## Fixtures

`pytest-amaranth-sim` provides the following fixtures and class (`SimulatorFixture`)
for controlling Amaranth simulations:

```{eval-rst}
.. automodule:: pytest_amaranth_sim.plugin
   :exclude-members: pytest_addoption, pytest_make_parametrize_id
```

## Miscellaneous

`pytest_amaranth_sim` also provides the following classes, functions, etc
for working with its fixtures. _Since these are not fixtures, and do not use
`pytest` hooks, you must import them before use._

```{eval-rst}
.. automodule:: pytest_amaranth_sim
```

(how_to_use_fixtures)=
### How To Use These Fixtures

(basic_test)=
A basic test using this plugin looks something like this:

```python
import pytest
from amaranth import Elaboratable, Module


class MyMod(Elaboratable):
    def __init__(self, width=4, registered=True):
        ...

    def elaborate(self, plat):
        m = Module()

        ...

        return m


@pytest.fixture
def tb(mod, request):
    async def inner(sim):
        s = sim
        m = mod

        ...

        # Use s object to drive simulation forward.
        await s.tick()

        # Assert statements to test m.
        assert ...

    return inner


@pytest.mark.parametrize("mod,clks", [(MyMod(), 1.0 / 12e6)])
def test_tb(sim, tb):
    sim.run(testbenches=[tb])
```

```{todo} Work on the prose of this section. Bullet points are a shortcut.
```

Of note: 

* Tests are expected to end with `sim.run()`, where most of the actual test
  is executed.
* Tests must be parameterized _at least_ in terms of `mod`, and probably `clks`
  as well (unless testing combinational code).
* From the simulator's POV, testbenches and processes are expected to be a
  function of a single argument (async) or no argument (generator).

Due to the simulator expecting functions of a single or no argument,
testbenches and processes generally are defined as [inner functions](https://docs.python.org/3.9/reference/compound_stmts.html#function-definitions), returned from an outer function (or passed
directly to `sim.run()`). In the above snippet, the inner function is `inner`
and the outer function is `tb`.

By using inner functions, testbenches and processes can be customized from
multiple sources:

* The [`request` fixture](https://docs.pytest.org/en/stable/reference/reference.html#std-fixture-request).
  This is useful when paired with [`pytest.mark.parametrize`](https://docs.pytest.org/en/stable/how-to/parametrize.html#pytest-mark-parametrize-parametrizing-test-functions) or [indirect parameterization](https://docs.pytest.org/en/stable/example/parametrize.html#indirect-parametrization):

  ```python
  @pytest.fixture(params=[False, True], ids=["once", "twice"])
  def params_from_fixture_tb(mod, request):
      tick_twice = request.param

      async def inner(sim):
          s = sim
          m = mod

          ...

          # Use s object to drive simulation forward.
          await s.tick()

          # Supplying arguments from the request fixture customizes TB behavior.
          if tick_twice:
              await s.tick()

          # Assert statements to test m.
          assert ...

      return inner


  @pytest.mark.parametrize("mod,clks", [(MyMod(), 1.0 / 12e6)])
  def test_params_from_fixture_tb(sim, mod, params_from_fixture_tb):
      sim.run(testbenches=[params_from_fixture_tb])
  ```

* From other fixtures when parameterizing tests [directly](https://docs.pytest.org/en/stable/how-to/fixtures.html#override-a-fixture-with-direct-test-parametrization):

  ```python
  @pytest.fixture
  def tick_twice_fixture():
    return False


  @pytest.fixture
  def params_from_other_fixture_tb(mod, tick_twice_fixture):
      async def inner(sim):
          s = sim
          m = mod

          ...

          # Use s object to drive simulation forward.
          await s.tick()

          # Supplying arguments from an external fixture customizes TB behavior.
          if tick_twice:
              await s.tick()

          # Assert statements to test m.
          assert ...

      return inner


  @pytest.mark.parametrize("mod,clks", [(MyMod(), 1.0 / 12e6)])
  @pytest.mark.parametrize("tick_twice_fixture", [True, False])
  def test_params_from_other_fixture_tb(sim, mod, params_from_other_fixture_tb):
      sim.run(testbenches=[params_from_other_fixture_tb])
  ```

* Direct input arguments to the outer function. This is useful when the outer
  function isn't a fixture, _and is very similar to the direct test
  parameterization above_. The outer function would be invoked inside a test
  body (`direct_arg_tb` in the below snippet) and return your testbenches and
  processes to be passed to `sim.run()`:

  ```python
  def direct_arg_tb(mod, tick_twice=False):
      async def inner(sim):
          s = sim
          m = mod

          ...

          # Use s object to drive simulation forward.
          await s.tick()

          # Supplying arguments to the TB generator customizes TB behavior.
          if tick_twice:
              await s.tick()

          # Assert statements to test m.
          assert ...

      return inner


  @pytest.mark.parametrize("mod,clks", [(MyMod(), 1.0 / 12e6)])
  @pytest.mark.parametrize("tick_twice", [True, False])
  def test_direct_arg_tb(sim, mod, tick_twice):
      tb = direct_arg_tb(mod, tick_twice)

      sim.run(testbenches=[tb])
  ```

(inline_test)=
* If your given test body has enough fixtures and parameterization, the test
  itself can be the outer function, and testbenches and processes can be
  defined in-line in the test body!


  ```python
  @pytest.mark.parametrize("mod,clks", [(MyMod(), 1.0 / 12e6)])
  @pytest.mark.parametrize("tick_twice", [True, False])
  def test_inline_tb(sim, mod, tick_twice):
      async def inner(sim):
          s = sim
          m = mod

          ...

          # Use s object to drive simulation forward.
          await s.tick()

          # Supplying bound variables to the inner function customizes TB behavior.
          if tick_twice:
              await s.tick()

          # Assert statements to test m.
          assert ...

      sim.run(testbenches=[inner])
  ```

  **Note the similarities of each inner function, from the [basic](basic_test) example
  to the [inline](inline_test) example**. How to customize your testbenches is
  at least partially a matter of preference. I would start with whatever seems
  quickest to implement and adapt as you flesh out your test suite.

## Command Line Options

* `--vcds`: Generate [Value Change Dump](https://en.wikipedia.org/wiki/Value_change_dump) files
  from simulations. These can be viewed in a VCD viewer like [GTKWave](https://gtkwave.sourceforge.net/)
  or [Surfer](https://gitlab.com/surfer-project/surfer). The filenames of the
  VCD files will be derived from the names of tests run in the current session.

## Configuration File Settings

The following {doc}`configuration options <pytest:reference/customize>`
are available:

* `long_vcd_filenames`: VCD and GTKW files generated have longer, but less
  ambiguous filenames (`bool`).
* `extend_vcd_time`: Work around [GTKWave behavior](https://github.com/gtkwave/gtkwave/issues/230)
  to truncate VCD traces that end on a transition (`string`, femtoseconds to
  extend trace).
