import pytest
from amaranth import ClockDomain, Elaboratable, Signal, Module, ClockSignal
from amaranth.sim import Passive
from dataclasses import dataclass
from contextlib import nullcontext as does_not_raise

from pytest_amaranth_sim._marker import Testbench


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


@pytest.fixture
def clk_drivers(mod):
    """Directly drive clocks for the clock multiplexer testbench."""  # noqa: D401
    def mk_driver(clk, period):
        async def driver(sim):
            s = sim
            m = mod

            curr_val = True
            i = 0

            # If this is truly background as intended, we won't break out of
            # the while before clk_tb or similar is done.
            # TODO: Use pytest timeout instead?
            while i < 1000:
                await s.delay(period / 2)
                # s.set(ClockSignal(clk), curr_val)
                s.set(getattr(m, clk), curr_val)

                curr_val = not curr_val
                i += 1

            pytest.fail("critical processes should have ended by now.")

        return driver

    return [
        Testbench(mk_driver("clk2", 1 / 12.0e6), background=True),
        Testbench(mk_driver("clk1", 1 / 12.5e6), background=True),
    ]


@pytest.mark.parametrize("mod", [Clocks(registered=False)])
@pytest.mark.parametrize("clks", [{
    "fast": 1 / 12.0e6,
    "slow": 1 / 12.5e6
}])
def test_clock_switcher_multi(sim, clk_tb):
    sim.run(testbenches=[clk_tb], processes=[])


@pytest.mark.parametrize("mod", [ClockSwitcher(registered=False)])
@pytest.mark.parametrize("clks", [None])
def test_clock_switcher_background(sim, clk_tb, clk_drivers):
    sim.run(testbenches=[clk_tb, *clk_drivers], processes=[])
