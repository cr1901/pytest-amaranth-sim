import pytest
from amaranth import Elaboratable, Signal, Module


class Adder(Elaboratable):
    def __init__(self, width=4):
        self.width = width
        self.a = Signal(width)
        self.b = Signal(width)
        self.o = Signal(width + 1)

    def elaborate(self, plat):  # noqa: D102
        m = Module()

        m.d.sync += self.o.eq(self.a + self.b)

        return m


@pytest.fixture
def testbench(mod, a, b, o):
    if (a,b,o,mod.width) == (127, 127, 254, 4):
        return pytest.skip(reason="inputs too wide")

    async def testbench(sim):
        await sim.tick()

        sim.set(mod.a, a)
        await sim.tick()
        assert sim.get(mod.o) == a
        sim.set(mod.b, b)
        await sim.tick()
        assert sim.get(mod.o) == o

    return testbench


@pytest.mark.parametrize("a,b,o", [(0, 0, 0), (1, 1, 2), (127, 127, 254)])
@pytest.mark.parametrize("mod", [Adder(4), Adder(8)])
@pytest.mark.parametrize("clks", [1.0 / 12e6])
def test_inject_direct(sim, testbench):
    sim.run(testbenches=[testbench], processes=[])
