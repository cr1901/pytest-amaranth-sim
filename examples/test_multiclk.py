import pytest
from amaranth import ClockDomain, Elaboratable, Signal, Module, ClockSignal
from amaranth.sim import Passive
from dataclasses import dataclass
from contextlib import nullcontext as does_not_raise


class ClockSwitcher(Elaboratable):
    """Dummy Amaranth clock multiplexer module."""

    def __init__(self, registered=True):
        self.registered = registered
        self.clk1 = Signal()
        self.clk2 = Signal()
        self.out = Signal()
        self.sel = Signal(1)

    def elaborate(self, plat):
        m = Module()

        if self.registered:
            pass
        else:
            with m.If(self.sel):
                m.d.comb += self.out.eq(self.clk2)
            with m.Else():
                m.d.comb += self.out.eq(self.clk1)

        return m


class Clocks(Elaboratable):
    """Define some clock domains for testing."""

    def __init__(self, registered=True):
        self.registered = registered
        self.sel = Signal()

    def elaborate(self, plat):
        m = Module()

        sw = ClockSwitcher(self.registered)
        m.submodules += sw
        # Without this line, clk3 is "multiply-driven"
        m.domains += ClockDomain("out")

        m.d.comb += [
            sw.clk1.eq(ClockSignal("slow")),
            sw.clk2.eq(ClockSignal("fast")),
            ClockSignal("out").eq(sw.out)
        ]

        m.d.comb += sw.sel.eq(self.sel)

        return m


@pytest.fixture
def clk_tb(mod):
    """Basic clock multiplexer testbench."""  # noqa: D401
    async def testbench(sim):
        s = sim
        m = mod

        await s.delay(18e-6)
        s.set(m.sel, 1)
        await s.delay(20e-6)

    return testbench


@pytest.mark.parametrize("mod", [Clocks(registered=False)])
@pytest.mark.parametrize("clks", [{
    "fast": 1 / 12.0e6,
    "slow": 1 / 12.5e6
}])
def test_clock_switcher_multi(sim, clk_tb):
    sim.run(testbenches=[clk_tb], processes=[])  # , background=[sel_driver])
