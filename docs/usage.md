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

(how_to_use_fixtures)=
### How To Use These Fixtures

```{todo} To be written. General outline:

* Pytests tests are expected to end with a `sim.run(testbenches=[], processes=[])` line.

* From the simulator's POV, testbenches and processes are expected to be a
  function of a single argument (async) or no argument (generator).

* To create a testbench that takes parameters, you will generally wrap the
  testbench function `tb` inside another function `outer` which takes arguments,
  and then returns `tb`. While `tb` takes a single argument (async) or no argument
  (generator), it can access the parameters/local variables of `outer` after
  `outer` returns.

  See: Programmer's note under https://docs.python.org/3.9/reference/compound_stmts.html#function-definitions

* There are at least four ways to inject an inner function `tb` with variables:
  * Create `outer` as a fixture that expects its arguments via request fixture,
    and pass arguments to fixture via pytest.mark.parameterize. If you return
    the inner testbench `tb`, the `outer` fixture will return a testbench
    immediately ready to be passed to `sim.run`.
  * Like above, but create `outer` as a fixture that expects its arguments via
    other fixtures (either direct, or otherwise).
  * Create fixtures that supply arguments to a `make_testbench(args)` function,
    where `make_testbench()` is invoked in the `test_*` function body.
  * Create the `tb` functions in-line in the `test_*` functions.
```

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
* `extend_vcd_time`: Work around [GTKWave behavior](https://github.com/gtkwave/gtkwave/issues/230#issuecomment-2065663811)
  to truncate VCD traces that end on a transition (`string`, femtoseconds to
  extend trace).
