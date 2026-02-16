"""Main module for amaranth simulator pytest plugin."""

__doc__ = ""  # Hide from Sphinx docs while making pydocstyle happy... I
# don't think it looks nice in the docs.

import pytest
import in_place
from amaranth import Elaboratable
from amaranth.sim import Simulator

from ._marker import Testbench


def pytest_addoption(parser):  # noqa: D103
    group = parser.getgroup('amaranth-sim')
    group.addoption(
        "--vcds",
        action="store_true",
        help="generate Value Change Dump (vcds) from simulations",
    )
    parser.addini(
        "long_vcd_filenames",
        type="bool",
        default=False,
        help="if set, vcd files get longer, but less ambiguous, filenames"
    )
    parser.addini(
        "extend_vcd_time",
        type="string",
        default="0",
        help="extend simulation time in failing vcds by the supplied number "
             "of femtoseconds"
    )


def pytest_make_parametrize_id(config, val, argname):  # noqa: D103
    if argname in ("clks"):
        if isinstance(val, float):
            return f"{1 / val / 1000000:04.2f}"
        if isinstance(val, dict):
            # No need for sorted(val.items()) since 3.7.
            return "-".join([f"{k}@{1 / v / 1000000:04.2f}"
                             for (k, v) in val.items()])
        else:
            return "comb"
    elif isinstance(val, Elaboratable) and argname in ("mod"):
        return val.__class__.__name__.lower()
    else:
        return None


class SimulatorFixture:
    """Fixture class which drives Amaranth's :doc:`Python simulator <amaranth:simulator>`.

    ``SimulatorFixture's`` contructor is private; it's arguments are documented
    for completeness.

    Parameters
    ----------
    mod: Module
        The :fixture:`module <mod>` fixture.
    clks: None or float or dict of str: float
        The :fixture:`clock periods <clks>` fixture.
    req: ~_pytest.fixtures.FixtureRequest
        The :mod:`pytest` ``request`` fixture.
    cfg: ~_pytest.config.Config
        The :mod:`pytest` :func:`~_pytest.fixtures.pytestconfig` fixture.

    Raises
    ------
    :exception:`Valuerror`
        If clocks aren't ``None``, :class:`float`, or :class:`dict` of
        :class:`str`: :class:`float`.
    """  # noqa: E501

    def __init__(self, mod, clks, req, cfg):
        self.mod = mod
        self.clks = clks

        if cfg.getini("long_vcd_filenames"):
            self.name = req.node.name + "-" + req.module.__name__
        else:
            self.name = req.node.name

        self.extend = int(cfg.getini("extend_vcd_time"))

        self.sim = Simulator(self.mod)
        self.vcds = cfg.getoption("vcds")

        if self.clks:
            if isinstance(self.clks, float):
                self.sim.add_clock(self.clks)
            elif isinstance(self.clks, dict):
                for domain, per in self.clks.items():
                    self.sim.add_clock(per, domain=domain)
            else:
                raise ValueError("clks should be a float or dict of floats, "
                                 f"not {type(self.clks)}")

    def run(self, *, testbenches=[], processes=[]):
        r"""Run a simulation using Amaranth's :class:`amaranth.sim.Simulator`.

        :meth:`run` is expected to be called as the last statement in a test.
        The simulator tests a given ``mod`` by driving the given
        :meth:`testbenches <amaranth.sim.Simulator.add_testbench>` and
        :meth:`processes <amaranth.sim.Simulator.add_processes>`.

        Testbenches and can be prepared and parameterized in multiple ways.
        See :ref:`how_to_use_fixtures` for examples.

        Any exceptions raised within the testbenches and processes given to
        :meth:`run` will be propagated to the `pytest` test runner. Generally,
        testbenches and processes should raise :exc:`AssertionError` to
        indicate test failure of a given ``mod``.

        Parameters
        ----------
        testbenches: list of Callable[[SimulatorContext], Coroutine] or :class:`.Testbench`
            List of Amaranth
            :meth:`testbenches <amaranth.sim.Simulator.add_testbench>`
            to add *all at once* before running the simulator. The list can
            be callables, :class:`.Testbench`\es, or a mixture.

            Each "bare" callable will be passed to
            :meth:`~amaranth.sim.Simulator.add_testbench` unmodified; such
            testbenches are implicitly critical.
        processes: list of Callable[[SimulatorContext], Coroutine]
            List of Amaranth
            :meth:`processes <amaranth.sim.Simulator.add_process>`
            to add *all at once* before running the simulator.

        Raises
        ------
        :exception:`ValueError`
            If at least one list element of ``testbenches`` isn't a
            callable or :class:`.Testbench`.
        """  # noqa: DOC501, DOC502, E501
        for t in testbenches:
            if callable(t):
                self.sim.add_testbench(t)
            elif isinstance(t, Testbench):
                self.sim.add_testbench(t.constructor, background=t.background)
            else:
                raise ValueError("testbenches should be a list of callables "
                                 f"and/or Testbenches, not {type(t)}")

        for p in processes:
            self.sim.add_process(p)

        if self.vcds:
            try:
                with self.sim.write_vcd(self.name + ".vcd",
                                        self.name + ".gtkw"):
                    self.sim.run()
            except:
                self._patch_vcds()
                raise
        else:
            self.sim.run()

    def _patch_vcds(self):
        with in_place.InPlace(self.name + ".vcd") as fp:
            ts = 0
            for line in fp:
                if line[0] in "#":
                    ts = int(line[1:-1])
                fp.write(line)
            else:
                fp.write(f"#{ts + self.extend}\n")


@pytest.fixture
def mod():
    """Fixture representing an Amaranth :ref:`Module <amaranth:lang-modules>`.

    If the :fixture:`sim` fixture is used in a test, either directly or
    indirectly, this fixture must be :ref:`overridden <override fixtures>`
    by the user. The overridden fixture should return an Amaranth Module.

    Raises
    ------
    :exception:`pytest.UsageError`
        If ``mod`` fixture was not overridden when the ``sim`` fixture is used
        in a test, directly or indirectly.
    """  # noqa: DOC501, DOC502
    raise pytest.UsageError("User must override `mod` fixture in test- see: https://docs.pytest.org/en/stable/how-to/fixtures.html#overriding-fixtures-on-various-levels")


@pytest.fixture
def sim(mod, clks, request, pytestconfig):
    """Fixture representing an Amaranth :class:`pysim <amaranth.sim.Simulator>` context.

    Parameters
    ----------
    mod: Module
        The :fixture:`module <mod>` fixture.
    clks: float or dict of str: float
        The :fixture:`clock periods <clks>` fixture.
    request: ~_pytest.fixtures.FixtureRequest
        The :mod:`pytest` ``request`` fixture.
    pytestconfig: ~_pytest.config.Config
        The :mod:`pytest` :fixture:`~_pytest.fixtures.pytestconfig` fixture.

    Returns
    -------
    :class:`SimulatorFixture`
    """  # noqa: E501
    simfix = SimulatorFixture(mod, clks, request, pytestconfig)
    return simfix


@pytest.fixture()
def clks():
    """Fixture representing the clocks used by the :fixture:`mod` fixture.

    The ``clks`` fixture should return either:

    * ``None``, indicating a purely combinational module.
    * A :class:`float` representing the clock period of the ``sync`` domain in
      seconds.
    * A :class:`dict` with :class:`str` keys and :class:`float` values. The
      keys name each clock domain used by the :fixture:`mod` fixture (and thus
      available to :fixture:`sim`). Each value is the clock period of the named
      clock in seconds.

    This fixture is expected to be :ref:`overridden <override fixtures>` by
    the user if the :fixture:`mod` fixture is clocked.

    Returns
    -------
    None or float or dict
    """
    return None
