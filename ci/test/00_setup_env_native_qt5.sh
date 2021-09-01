#!/usr/bin/env bash
#
# Copyright (c) 2019-2020 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

export LC_ALL=C.UTF-8
#export PACKAGE_MANAGER_INSTALL #default
#export MAKEJOBS #default
#export DANGER_RUN_CI_ON_HOST #default
#export TEST_RUNNER_PORT_MIN #default
#export CCACHE_SIZE #default
#export CCACHE_DIR #default


#export HOST #default
export CONTAINER_NAME=ci_native_qt5
export DOCKER_NAME_TAG=ubuntu:18.04  # Check that bionic gcc-7 can compile our c++17 and run our functional tests in python3, see doc/dependencies.md


#export NO_DEPENDS #default
#export DEP_OPTS #no relevant
export GOAL="install"
export PREVIOUS_RELEASES_TO_DOWNLOAD="v0.15.2 v0.16.3 v0.17.2 v0.18.1 v0.19.1 v0.20.1"
export BGL_CONFIG="--enable-zmq --with-libs=no --with-gui=qt5 --enable-reduce-exports
--enable-debug --disable-fuzz-binary  CFLAGS=\"-g0 -O2 -funsigned-char\" CXXFLAGS=\"-g0 -O2 -funsigned-char\""
