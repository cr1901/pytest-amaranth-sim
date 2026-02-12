"""Useful marker classes that aren't part of pytest hooks."""

from dataclasses import dataclass
from amaranth.sim import SimulatorContext
from typing import Callable, Coroutine


@dataclass
class Testbench:
    """Annotate an Amaranth testbench with arguments.

    This class is a wrapper, similar to how :func:`pytest.param` annotates
    fixture parameters. Wrap your testbench constructor with this class so
    that :func:`sim fixture <sim>` can pass additional arguments to
    :meth:`~amaranth.sim.Simulator.add_testbench` along with your testbench
    constructor.

    ..
       The sequence of >>> and ... is tragically correct for this example.
       For the reasoning, see: https://stackoverflow.com/a/41081780

    .. doctest::

       >>> from pytest_amaranth_sim import Testbench

       >>> async def my_tb(ctx):
       ...    ...

       >>> tb = Testbench(my_tb, background=True)
    """

    __test__ = False

    #: Testbench constructor- i.e. the first argument to
    #: :meth:`~amaranth.sim.Simulator.add_testbench`.
    constructor: Callable[[SimulatorContext], Coroutine]
    #: If ``True``, mark :attr:`constructor` as background when passed to
    #: :meth:`~amaranth.sim.Simulator.add_testbench`.
    background: bool = False
