#!/usr/bin/env bash
#
# Copyright (c) 2019-2022 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

export LC_ALL=C.UTF-8
#export PACKAGE_MANAGER_INSTALL #default
#export MAKEJOBS #default
#export DANGER_RUN_CI_ON_HOST #default
#export TEST_RUNNER_PORT_MIN #default
#export CCACHE_SIZE #default
#export CCACHE_DIR #default

export CONTAINER_NAME=ci_native_nowallet_libBGLkernel
export CI_IMAGE_NAME_TAG="ubuntu:20.04"
# Use minimum supported python3.8 and clang-10, see doc/dependencies.md
export PACKAGES="python3-zmq clang-10 llvm-10 libc++abi-10-dev libc++-10-dev"
export DEP_OPTS="NO_WALLET=1 CC=clang-10 CXX='clang++-10 -stdlib=libc++'"
export GOAL="install"
export BGL_CONFIG="--enable-reduce-exports --enable-experimental-util-chainstate --with-experimental-kernel-lib --enable-shared"
