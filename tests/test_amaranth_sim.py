"""amaranth-sim tests module."""


def test_sim_mod_fixture(pytester, file_exists):
    """Make sure that pytest accepts our fixture."""
    pytester.copy_example("test_mul.py")

    # run pytest with the following cmd args
    result = pytester.runpytest("-v", "-k", "test_basic")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_basic[[]*[]] PASSED*',
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0

    assert not file_exists("*.vcd")
    assert not file_exists("*.gtkw")


def test_help_message(pytester):
    """Test that help message looks correct."""
    result = pytester.runpytest(
        "--help",
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "amaranth-sim:",
        "*--vcds*generate Value Change Dump (vcds) from simulations",
        "*long_vcd_filenames (bool):",
        "*if set, vcd files get longer, but less ambiguous,",
        "*filenames"
    ])


def test_vcd_generation(pytester, file_exists):
    """Make sure that VCD files get generated."""
    pytester.copy_example("test_mul.py")

    # run pytest with the following cmd args
    result = pytester.runpytest("-v", "-k", "test_basic", "--vcds")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_basic[[]*[]] PASSED*',
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0

    assert file_exists("test_basic[[]*[]].vcd")
    assert file_exists("test_basic[[]*[]].gtkw")


def test_long_vcd_generation(pytester, file_exists):
    """Make sure that VCD files with extended filenames get generated."""
    pytester.makeini("""
        [pytest]
        long_vcd_filenames = true
    """)
    pytester.copy_example("test_mul.py")

    # run pytest with the following cmd args
    result = pytester.runpytest("-v", "-k", "test_basic", "--vcds")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_basic[[]*[]] PASSED*',
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0

    assert file_exists("test_basic[[]*[]]-test_mul.vcd")
    assert file_exists("test_basic[[]*[]]-test_mul.gtkw")


def test_parameterized_testbench(pytester, file_exists):
    """Ensure that parameterizing testbenches/processes work."""
    pytester.copy_example("test_mul.py")

    # run pytest with the following cmd args
    result = pytester.runpytest("-v", "-k", "test_alternate_inputs")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_alternate_inputs[[]*[]] PASSED*',
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0

    assert not file_exists("*.vcd")
    assert not file_exists("*.gtkw")


def test_parameterized_module(pytester, file_exists):
    """Make sure that parameterizing an Elaboratable succeeds."""
    pytester.copy_example("test_mul.py")

    # run pytest with the following cmd args
    result = pytester.runpytest("-v", "-k", "test_alternate_width")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_alternate_width[[]*[]] PASSED*',
        '*::test_alternate_width[[]*[]] PASSED*',
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0

    assert not file_exists("*.vcd")
    assert not file_exists("*.gtkw")


def test_parameterized_testbench_and_module(pytester, file_exists):
    """Test parameterizing testbench/process and Elaboratable simultaneously."""  # noqa: E501
    pytester.copy_example("test_mul.py")

    # run pytest with the following cmd args
    result = pytester.runpytest("-v", "-k", "test_alternate_width_and_inputs")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_alternate_width_and_inputs[[]*[]] PASSED*',
        '*::test_alternate_width_and_inputs[[]*[]] PASSED*',
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0

    assert not file_exists("*.vcd")
    assert not file_exists("*.gtkw")


def test_comb_testbench(pytester, file_exists):
    """Test combinational and sync testbenches without clks decorator."""
    pytester.copy_example("test_mul.py")

    # run pytest with the following cmd args
    result = pytester.runpytest("-v", "-k", "comb", "--vcds")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_comb_tb[[]*[]] PASSED*',
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0

    assert file_exists("test_comb_tb[[]*[]].vcd")
    assert file_exists("test_comb_tb[[]*[]].gtkw")


# This one's special... we _want_ this one to fail!
def test_comb_testbench_fail(pytester, file_exists):
    """Test combinational testbench with clks decorator."""
    pytester.copy_example("test_mul.py")

    pytester.makepyfile(
        """
        import pytest
        from test_mul import Mul

        # This should raise an exception when creating the sim fixture.
        @pytest.mark.parametrize("mod,clks", [(Mul(registered=False), 1.0 / 12e6)])
        def test_comb_tb_with_clock(sim, mul_tb):
            sim.run(testbenches=[mul_tb])
    """
    )

    result = pytester.runpytest("-v", "-k", "test_comb_tb_with_clock")

    assert result.ret == 1
    result.stdout.fnmatch_lines([
        "*ValueError: Domain * is not present in simulation",
        "ERROR*::test_comb_tb_with_clock*"
    ])

    assert not file_exists("test_comb_tb_with_clock.vcd")
    assert not file_exists("test_comb_tb_with_clock.gtkw")
