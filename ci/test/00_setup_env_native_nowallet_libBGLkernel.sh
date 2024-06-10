#!/usr/bin/env bash
#
# Copyright (c) 2019-present The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

export LC_ALL=C.UTF-8

export CONTAINER_NAME=ci_native_nowallet_libBGLkernel
export CI_IMAGE_NAME_TAG="docker.io/ubuntu:22.04"
# Use minimum supported python3.9 (or best-effort 3.10) and clang-14, see doc/dependencies.md
export PACKAGES="python3-zmq clang-14 llvm-14 libc++abi-14-dev libc++-14-dev"
export DEP_OPTS="NO_WALLET=1 CC=clang-14 CXX='clang++-14 -stdlib=libc++'"
export GOAL="install"
export BGL_CONFIG="--enable-reduce-exports --enable-experimental-util-chainstate --with-experimental-kernel-lib --enable-shared"
