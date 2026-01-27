"""Main module for amaranth simulator pytest plugin."""

__doc__ = ""  # Hide from Sphinx docs while making pydocstyle happy... I
# don't think it looks nice in the docs.

import pytest
import in_place
from amaranth import Elaboratable
from amaranth.sim import Simulator
from typing import Coroutine

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
            return f"{1/val/1000000:04.2f}"
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
        The :func:`module <mod>` fixture.
    clks: None or float or dict of str: float
        The :func:`clock periods <clks>` fixture.
    req: ~_pytest.fixtures.FixtureRequest
        The :mod:`pytest` ``request`` fixture.
    cfg: ~_pytest.config.Config
        The :mod:`pytest` :func:`~_pytest.fixtures.pytestconfig` fixture.

    Raises
    ------
    :exception:`NotImplementedError`
        If multiple clock domains are provided.
    :exception:`ValueError`
        If clocks aren't ``None``, :class:`float`, or :class:`dict` of
        :class:`str`: :class:`float`.
    """  #  noqa: E501

    def __init__(self, mod, clks, req, cfg):  # noqa: DOC503 # https://github.com/jsh9/pydoclint/issues/165
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

    def run(self, *, testbenches=[], processes=[]):  # noqa: DOC501
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
        testbenches: list of Coroutine or :class:`Testbench`
            List of Amaranth
            :meth:`testbenches <amaranth.sim.Simulator.add_testbench>`
            to add *all at once* before running the simulator.

            The list can be Coroutines, :class:`Testbench`\es, or a mixture.
            Each "bare" Coroutine will become a
            :meth:`critical <amaranth.sim.Simulator.add_testbench>` testbench.
        processes: list of callables
            List of Amaranth
            :meth:`processes <amaranth.sim.Simulator.add_processes>`
            to add *all at once* before running the simulator.

        Raises
        ------
        :exception:`ValueError`
            If at least one list element of ``testbenches`` isn't a
            Coroutine or :class:`Testbench`.
        """
        for t in testbenches:
            if isinstance(t, Coroutine):
                self.sim.add_testbench(t)
            elif isinstance(t, Testbench):
                self.sim.add_testbench(t.constructor, background=t.background)
            else:
                raise ValueError("clks should be a list of Coroutines and/or"
                                 f" Testbenches, not {type(self.clks)}")

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
def mod():  # noqa: DOC503  # https://github.com/jsh9/pydoclint/issues/165
    """Fixture representing an Amaranth :ref:`Module <amaranth:lang-modules>`.
    
    If the :func:`sim` fixture is used in a test, either directly or
    indirectly, this fixture must be :ref:`overridden <override fixtures>`
    by the user.

    Raises
    ------
    :exception:`pytest.UsageError`
        If ``mod`` fixture was not overridden when the ``sim`` fixture is used
        in a test, directly or indirectly.
    """
    raise pytest.UsageError("User must override `mod` fixture in test- see: https://docs.pytest.org/en/stable/how-to/fixtures.html#overriding-fixtures-on-various-levels")


@pytest.fixture
def sim(mod, clks, request, pytestconfig):
    """Fixture representing an Amaranth `pysim` context.
    
    Parameters
    ----------
    mod: Module
        The :func:`module <mod>` fixture.
    clks: float or dict of str: float
        The :func:`clock periods <clks>` fixture.
    request: ~_pytest.fixtures.FixtureRequest
        The :mod:`pytest` ``request`` fixture.
    pytestconfig: ~_pytest.config.Config
        The :mod:`pytest` :func:`~_pytest.fixtures.pytestconfig` fixture.

    Returns
    -------
    :class:`SimulatorFixture`
    """
    simfix = SimulatorFixture(mod, clks, request, pytestconfig)
    return simfix


@pytest.fixture()
def clks():
    """Fixture representing the clocks used by the :func:`mod` fixture.
    
    The ``clks`` fixture should return either:
     
    * ``None``, indicating a purely combinational module.
    * A :class:`float` representing the clock period of the ``sync`` domain in
      seconds.
    * A :class:`dict` with :class:`str` keys and :class:`float` values. The
      keys name each clock domain used by the :func:`mod` fixture (and thus
      available to :func:`sim`). Each value is the clock period of the named
      clock in seconds.

    This fixture is expected to be :ref:`overridden <override fixtures>` by
    the user if the :func:`mod` fixture is clocked.

    Returns
    -------
    None or float or dict
    """
    return None
