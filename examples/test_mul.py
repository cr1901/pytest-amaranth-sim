"""Basic test of amaranth sim pytest plugin using a dummy multiplier."""

import pytest
from amaranth.sim import Tick
from amaranth import Elaboratable, Signal, Module


class Mul(Elaboratable):
    """Dummy Amaranth multiplier module."""

    def __init__(self, width=4, registered=True):
        self.width = width
        self.registered = registered
        self.a = Signal(width)
        self.b = Signal(width)
        self.o = Signal(2*width)

    def elaborate(self, plat):  # noqa: D102
        m = Module()

        if self.registered:
            m.d.sync += self.o.eq(self.a * self.b)
        else:
            m.d.comb += self.o.eq(self.a * self.b)

        return m


@pytest.fixture
def mul_tb(sim_mod):
    def testbench():
        _, m = sim_mod

        yield m.a.eq(1)
        yield m.b.eq(2)
        yield Tick()

        assert (yield m.o) == 2

    return testbench


@pytest.mark.module(Mul())
@pytest.mark.clks((1.0 / 12e6,))
def test_basic(sim_mod, mul_tb):
    sim, _ = sim_mod
    sim.run(testbenches=[mul_tb])
