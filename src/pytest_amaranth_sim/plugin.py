"""Main module for amaranth simulator pytest plugin."""

import pytest
import in_place
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
    parser.addini(
        "extend_vcd_time",
        type="string",
        default="0",
        help="extend simulation time in failing vcds by the supplied number of femtoseconds"
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

        self.extend = int(cfg.getini("extend_vcd_time"))

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

        try:
            if self.vcds:
                try:
                    with self.sim.write_vcd(self.name + ".vcd", self.name + ".gtkw"):
                        self.sim.run()
                except AssertionError as e:
                    self._patch_vcds()
                    raise
            else:
                self.sim.run()
        except TypeError as e:
            raise TypeError("simulation returned TypeError; did you mix async-await with yield in your testbenches?") from e

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
    raise pytest.UsageError("User must override `mod` fixture in test- see: https://docs.pytest.org/en/stable/how-to/fixtures.html#override-a-fixture-with-direct-test-parametrization")


@pytest.fixture
def sim(mod, clks, request, pytestconfig):
    simfix = SimulatorFixture(mod, clks, request, pytestconfig)
    return simfix


@pytest.fixture()
def clks():
    return None
