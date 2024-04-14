"""amaranth-sim tests module."""


def test_sim_mod_fixture(pytester):
    """Make sure that pytest accepts our fixture."""
    pytester.copy_example("test_mul.py")

    # run pytest with the following cmd args
    result = pytester.runpytest("-v", "-k", "test_basic")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_basic PASSED*',
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0

    assert not (pytester.path / "test_basic.vcd").exists()
    assert not (pytester.path / "test_basic.gtkw").exists()


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


def test_vcd_generation(pytester):
    """Make sure that VCD files get generated."""
    pytester.copy_example("test_mul.py")

    # run pytest with the following cmd args
    result = pytester.runpytest("-v", "-k", "test_basic", "--vcds")

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_basic PASSED*',
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0

    assert (pytester.path / "test_basic.vcd").exists()
    assert (pytester.path / "test_basic.gtkw").exists()


def test_long_vcd_generation(pytester):
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
        '*::test_basic PASSED*',
    ])

    # make sure that we get a '0' exit code for the testsuite
    assert result.ret == 0

    assert (pytester.path / "test_basic-test_mul.vcd").exists()
    assert (pytester.path / "test_basic-test_mul.gtkw").exists()
