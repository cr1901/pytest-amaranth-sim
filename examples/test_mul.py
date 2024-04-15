"""Basic test of amaranth sim pytest plugin using a dummy multiplier."""

import pytest
from amaranth.sim import Tick, Delay
from amaranth import Elaboratable, Signal, Module
from dataclasses import dataclass
from contextlib import nullcontext as does_not_raise


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


@pytest.mark.module(Mul())
@pytest.mark.clks((1.0 / 12e6,))
@pytest.mark.parametrize(
    "mul_tb", [pytest.param(MulTbArgs(a_in=2, o_out=4), id="alt")],
    indirect=True
)
def test_alternate_inputs(sim_mod, mul_tb):
    sim, _ = sim_mod
    sim.run(testbenches=[mul_tb])


@pytest.mark.module.with_args(Mul)
@pytest.mark.clks((1.0 / 12e6,))
@pytest.mark.parametrize(
    "sim_mod,expectation", [
        (((), dict(width=1)), pytest.raises(AssertionError)),
        (((), dict(width=6)), does_not_raise())
    ], indirect=["sim_mod"]
)
def test_alternate_width(sim_mod, mul_tb, expectation):
    sim, _ = sim_mod
    with expectation:
        sim.run(testbenches=[mul_tb])


@pytest.mark.module.with_args(Mul)
@pytest.mark.clks((1.0 / 12e6,))
@pytest.mark.parametrize(
    "sim_mod,mul_tb", [
        (((), dict(width=1)), MulTbArgs(b_in=1, o_out=1)),
        (((), dict(width=6)), MulTbArgs(a_in=16, b_in=16, o_out=256))
    ], indirect=True
)
def test_alternate_width_and_inputs(sim_mod, mul_tb):
    sim, _ = sim_mod
    sim.run(testbenches=[mul_tb])


@pytest.mark.module.with_args(Mul)
@pytest.mark.parametrize(
    "sim_mod,expectation", [
        pytest.param(((), dict(registered=True)), does_not_raise(),
                     marks=pytest.mark.skip(reason="infinitely loops")),
        (((), dict(registered=False)), does_not_raise())
    ], indirect=["sim_mod"]
)
def test_comb_tb(sim_mod, mul_tb, expectation):
    sim, _ = sim_mod
    with expectation:
        sim.run(testbenches=[mul_tb])
