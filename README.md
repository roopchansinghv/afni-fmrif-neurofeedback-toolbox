
# afni-fmrif-neurofeedback-toolbox

## Python scripts and modules to enable communication with AFNI's real-time data interface to facilitate neuro-feedback experiments

This project contains both code to communicate with AFNI's real-time interface via network, and example code to do simple
processing and stimulus generation, based on the received data.

The communication is handled by the `afniInterfaceRT` module, and the shipping demonstration experiment is implemented using
[PsychoPy](http://www.psychopy.org).

As of September 25, 2018 - this repository has been merged into [AFNI's](https://github.com/afni/afni) master branch, via
[this](https://github.com/afni/afni/pull/84) pull request. All future changes/enhancements will be done in and committed to
that repository.

