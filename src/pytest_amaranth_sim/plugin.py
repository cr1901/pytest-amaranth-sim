"""Main module for amaranth simulator pytest plugin."""

import pytest
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


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line(
        "markers",
        "clks(freq): clock frequency of \"sync\" domain to register "
        "for simulator."
    )
    config.addinivalue_line(
        "markers",
        "module(name): top-level module to simulate."
    )


class SimulatorFixture:
    def __init__(self, req, cfg):
        mod = req.node.get_closest_marker("module").args[0]

        # If sim_mod fixture was called indirect, assume that we were passed
        # a class, e.g. @pytest.mark.module.with_args(MyElaboratable). Extract
        # constructor args from the @pytest.mark.parameterize call.
        # This allows parameterizing a single Elaboratable within the framework
        # of pytest.
        if hasattr(req, "param"):
            args, kwargs = req.param
            self.mod = mod(*args, **kwargs)
        # Otherwise, assume we have an instance of Elaboratable, and pass that
        # directly to pysim. E.g. @pytest.mark.module(MyElaboratable())
        else:
            self.mod = mod

        if cfg.getini("long_vcd_filenames"):
            self.name = req.node.name + "-" + req.module.__name__
        else:
            self.name = req.node.name

        self.sim = Simulator(self.mod)
        self.vcds = cfg.getoption("vcds")

        clks = req.node.get_closest_marker("clks")
        # There might not be clocks, but if there are, specify them with
        # @pytest.mark.
        if clks:
            for clk in clks.args[0]:
                self.sim.add_clock(clk)

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
def sim_mod(request, pytestconfig):
    simfix = SimulatorFixture(request, pytestconfig)
    return (simfix, simfix.mod)
