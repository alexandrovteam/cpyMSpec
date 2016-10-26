## cpyMSpec [![Documentation Status](https://readthedocs.org/projects/cpymspec/badge/?version=latest)](http://cpymspec.readthedocs.org/en/latest/?badge=latest) [![Build Status](https://travis-ci.org/alexandrovteam/cpyMSpec.svg?branch=master)](https://travis-ci.org/alexandrovteam/cpyMSpec)

Routines for computing theoretical isotope patterns of small molecules.

## Installation

Binary builds are provided for convenience, use `pip install cpyMSpec`.
(You might have to run `pip install --upgrade pip` first, its version should be at least `8.1.1`.)

If it didn't work for you or you have security concerns, here's how to install the package from source:
- Install `cmake` and a recent version of `g++`, preferably 5.3 or later
  - OS X: `brew install gcc5`
  - Ubuntu: install `gcc-5` package from `ubuntu-toolchain-r` PPA
  - Windows: install MSYS2 and the build toolchain (see `wheel_builders/README.md`)
- Call the appropriate script from `wheel_builders` folder with arguments 'ims-cpp ms_cffi'.


## License

This project is licensed under Apache 2.0 license.
