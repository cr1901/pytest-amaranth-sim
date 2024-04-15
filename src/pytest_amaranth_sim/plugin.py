"""Main module for amaranth simulator pytest plugin."""

import pytest
from amaranth import Elaboratable
from amaranth.sim import Simulator


def pytest_addoption(parser):
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


def pytest_make_parametrize_id(config, val, argname):
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
    def __init__(self, mod, clks, req, cfg):
        self.mod = mod
        self.clks = clks

        if cfg.getini("long_vcd_filenames"):
            self.name = req.node.name + "-" + req.module.__name__
        else:
            self.name = req.node.name

        self.sim = Simulator(self.mod)
        self.vcds = cfg.getoption("vcds")

        clks = req.node.get_closest_marker("clks")
        # There might not be clocks, but if there are, specify them with
        # @pytest.mark.
        if self.clks:
            if isinstance(self.clks, float):
                self.sim.add_clock(self.clks)
            elif isinstance(self.clks, dict):
                raise NotImplementedError("simulation for domains besides sync is not yet supported")
                # for domain, clk in clks.iter():
                #     pass
            else:
                raise ValueError(f"clks should be a float or dict of floats, not {type(self.clks)}")

    def run(self, testbenches=[], processes=[]):
        for t in testbenches:
            self.sim.add_testbench(t)

        for p in processes:
            self.sim.add_process(p)

        if self.vcds:
            with self.sim.write_vcd(self.name + ".vcd", self.name + ".gtkw"):
                self.sim.run()
        else:
            self.sim.run()


@pytest.fixture
def mod():
    raise pytest.UsageError("User must override `mod` fixture in test- see: https://docs.pytest.org/en/stable/how-to/fixtures.html#override-a-fixture-with-direct-test-parametrization")


@pytest.fixture
def sim(mod, clks, request, pytestconfig):
    simfix = SimulatorFixture(mod, clks, request, pytestconfig)
    return simfix


@pytest.fixture()
def clks():
    return None
