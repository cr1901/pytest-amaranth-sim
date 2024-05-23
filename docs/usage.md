# Usage

## Command Line Options

## Configuration File Settings

The following {doc}`configuration options <pytest:reference/customize>`
are available:

* `long_vcd_filenames`: VCD and GTKW files generated have longer, but less
  ambiguous filenames (`bool`).
* `extend_vcd_time`: Work around [GTKWave behavior](https://github.com/gtkwave/gtkwave/issues/230#issuecomment-2065663811)
  to truncate VCD traces that end on a transition (`string`, femtoseconds to
  extend trace).
