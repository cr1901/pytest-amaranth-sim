"""amaranth-sim tests module."""

from itertools import zip_longest
from vcd.reader import tokenize, TokenKind


def test_inject_sim_args(pytester, file_exists):
    """Test various ways to inject a testbench with arguments."""
    pytester.copy_example("test_inject.py")

    # run pytest with the following cmd args
    result = pytester.runpytest("-v")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_inject_*[[]*[]] PASSED*',
        '*::test_inject_*[[]*[]] PASSED*',
        '*::test_inject_*[[]*[]] SKIPPED*',
        '*::test_inject_*[[]*[]] PASSED*',
        '*::test_inject_*[[]*[]] PASSED*',
        '*::test_inject_*[[]*[]] PASSED*',
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0

    assert not file_exists("*.vcd")
    assert not file_exists("*.gtkw")


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


def test_multiple_clocks(pytester, file_exists):
    """Test that the simulator fixture can accept multiple clocks."""
    pytester.copy_example("test_multiclk.py")

    # run pytest with the following cmd args
    result = pytester.runpytest("-v", "-k", "switcher_multi", "--vcds")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_clock_switcher_multi[[]fast@12.0*slow@12.5*clocks*[]] PASSED*',  # noqa: E501
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0

    assert file_exists("test_clock_switcher_multi"
                       "[[]fast@12.0*slow@12.5*clocks*[]].vcd")
    assert file_exists("test_clock_switcher_multi"
                       "[[]fast@12.0*slow@12.5*clocks*[]].gtkw")


def test_background_testbench(pytester, file_exists):
    """Test that the simulator fixture can accept background testbenches."""
    pytester.copy_example("test_multiclk.py")

    # run pytest with the following cmd args
    result = pytester.runpytest("-v", "-k", "switcher_background", "--vcds")

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0

    assert file_exists("test_clock_switcher_background[[]comb*clocks*[]].vcd")
    assert file_exists("test_clock_switcher_background[[]comb*clocks*[]].gtkw")


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


def test_collect(pytester, file_exists):
    """Test how pytest names tests with our hook and id functions."""
    pytester.copy_example("test_mul.py")

    pytester.makepyfile(
        """
        # amaranth: UnusedElaboratable=no
        import pytest
        from test_mul import Mul

        class MyMul(Mul):
            pass

        @pytest.fixture(params=[0,1,2])
        def my_mul_tb(request):
            pass

        @pytest.mark.parametrize("mod,clks", [pytest.param(MyMul(), 1.0 / 13.33e6)])
        def test_naming(sim, my_mul_tb):
            sim.run(testbenches=[my_mul_tb])

        @pytest.mark.parametrize("mod,clks,my_mul_tb", [pytest.param(MyMul(), 1.0 / 13.33e6, 3)])
        def test_naming_extra(sim, my_mul_tb):
            sim.run(testbenches=[my_mul_tb])
    """  # noqa: E501
    )

    result = pytester.runpytest("-v", "--co")

    assert result.ret == 0
    result.stdout.fnmatch_lines([
        "*test_naming[[]0-mymul-13.33[]]*",
        "*test_naming[[]1-mymul-13.33[]]*",
        "*test_naming[[]2-mymul-13.33[]]*",
        "*test_naming_extra[[]mymul-13.33-3[]]*",
        "*test_basic[[]1-2-mul-12.00[]]*",
        "*test_alternate_inputs[[]alt-mul[]]*",
        "*test_alternate_width[[]1-2-mul-12.00-fail[]]*",
        "*test_alternate_width[[]1-2-mul-12.00-pass[]]*",
        "*test_alternate_width_and_inputs[[]mul-12.00-1-1[]]*",
        "*test_alternate_width_and_inputs[[]mul-12.00-16-16[]]*",
        "*test_comb_tb[[]1-2-comb-reg-mul[]]*",
        "*test_comb_tb[[]1-2-comb-mul-pass[]]*",
    ])

    assert not file_exists("*.vcd")
    assert not file_exists("*.gtkw")


# Below this line, we _want_ these tests to fail!
def test_comb_testbench_fail(pytester, file_exists):
    """Test combinational and sync testbenches without clks decorator."""
    pytester.copy_example("test_mul.py")

    # Trying to add a clock via parameterization to a comb-only module, will
    # trigger an Amaranth error at pytest setup time; test_mul.py by itself
    # cannot catch this. Since test_mul is meant to be an example, create a
    # new file to test this case.
    #
    # TODO: when https://github.com/amaranth-lang/amaranth/issues/442 is
    # solved, we can move test_comb_tb[*reg-mul*] to this file too.
    pytester.makepyfile(
        """
        # amaranth: UnusedElaboratable=no
        import pytest
        from contextlib import nullcontext as does_not_raise
        from test_mul import Mul, mul_tb

        @pytest.mark.parametrize(
        "mod,clks,expectation", [
            (Mul(registered=False), 1.0 / 12.0e6, does_not_raise())
        ], ids=["comb-mul-with-clock-setup-error"])
        def test_comb_tb(sim, mul_tb, expectation):
            with expectation:
                sim.run(testbenches=[mul_tb])
        """
    )

    # run pytest with the following cmd args
    result = pytester.runpytest("-v", "-k", "comb", "--vcds")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        "*::test_comb_tb[[]*clock-setup-error[]] ERROR*",
        "*::test_comb_tb[[]*reg-mul[]] SKIPPED*",
        "*::test_comb_tb[[]*mul-pass[]] PASSED*",
    ])

    # make sure that we get a '1' exit code for the testsuite
    assert result.ret == 1

    assert file_exists("test_comb_tb[[]*[]].vcd")
    assert file_exists("test_comb_tb[[]*[]].gtkw")


def test_user_forgot_override_mod(pytester, file_exists):
    """Test combinational testbench with clks decorator."""
    pytester.copy_example("test_mul.py")

    pytester.makepyfile(
        """
        import pytest

        # This should raise an exception when creating the sim fixture.
        @pytest.mark.parametrize("clks", [1.0 / 12e6])
        def test_missing_mod(sim, mul_tb):
            sim.run(testbenches=[mul_tb])
    """
    )

    result = pytester.runpytest("-v", "-k", "test_missing_mod")

    assert result.ret == 1
    result.stdout.fnmatch_lines([
        "*UsageError: User must override `mod` fixture in test*",
        "ERROR*::test_missing_mod*"
    ])

    assert not file_exists("*.vcd")
    assert not file_exists("*.gtkw")


def test_vcd_not_truncated(pytester, file_exists, monkeypatch):
    """Test that VCD files are not truncated on assertion failure."""
    pytester.makeini("""
        [pytest]
        extend_vcd_time = 1000
    """)
    pytester.makepyfile(
        """
        # amaranth: UnusedElaboratable=no
        import pytest
        from amaranth import Module, Signal
        from amaranth.sim import Tick

        m = Module()
        a = Signal(4)
        b = Signal()

        m.d.comb += b.eq(a == 15)
        m.d.sync += a.eq(a + 1)

        @pytest.fixture(params=[pytest.param(False, id="good"), pytest.param(True, id="bad")])
        def my_tb(request):
            def testbench():
                fail_it = request.param
                for _ in range(16):
                    yield Tick()

                if fail_it:
                    assert False

            return testbench

        @pytest.mark.parametrize("mod,clks", [pytest.param(m, 1.0 / 12e6, id="sync")])
        def test_vcd_truncation(sim, my_tb):
            sim.run(testbenches=[my_tb])
    """  # noqa: E501
    )

    result = pytester.runpytest("-v", "--vcds", "-s")

    assert result.ret == 1

    assert file_exists("test_vcd_truncation[[]good-sync[]].vcd")
    assert file_exists("test_vcd_truncation[[]good-sync[]].gtkw")
    assert file_exists("test_vcd_truncation[[]bad-sync[]].vcd")
    assert file_exists("test_vcd_truncation[[]bad-sync[]].gtkw")

    with open("test_vcd_truncation[good-sync].vcd", "rb") as gfp, \
         open("test_vcd_truncation[bad-sync].vcd", "rb") as bfp:
        good_tokens = tokenize(gfp)
        bad_tokens = tokenize(bfp)

        must_be_last = False
        last_bt_ts = 0
        for gt, bt in zip_longest(good_tokens, bad_tokens):
            assert not must_be_last

            # Doubt the VCDs will be generated at the exact same time down
            # to the microsecond...
            if gt.kind == TokenKind.DATE:
                assert gt.kind == bt.kind
                continue

            # Otherwise, VCDs must match exactly until the last entry.
            if gt != bt:
                must_be_last = True
                continue

            if bt.kind == TokenKind.CHANGE_TIME:
                last_bt_ts = bt.time_change

        assert gt.kind == bt.kind
        assert bt.kind == TokenKind.CHANGE_TIME
        assert bt.time_change == last_bt_ts + 1000
