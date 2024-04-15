"""Basic test of amaranth sim pytest plugin using a dummy multiplier."""

import pytest
from amaranth.sim import Tick, Delay
from amaranth import Elaboratable, Signal, Module
from dataclasses import dataclass


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


@dataclass
class MulTbArgs:
    a_in: int = 1
    b_in: int = 2
    o_out: int = 2


@pytest.fixture(params=[pytest.param(MulTbArgs(), id="default")],)
def mul_tb(sim_mod, request):
    def testbench():
        _, m = sim_mod

        if m.registered:
            yield Tick()
        else:
            yield Delay(0.1)

        yield m.a.eq(request.param.a_in)
        yield m.b.eq(request.param.b_in)

        if m.registered:
            yield Tick()
        else:
            yield Delay(0.1)

        assert (yield m.o) == request.param.o_out

    return testbench


@pytest.mark.module(Mul())
@pytest.mark.clks((1.0 / 12e6,))
def test_basic(sim_mod, mul_tb):
    sim, _ = sim_mod
    sim.run(testbenches=[mul_tb])
