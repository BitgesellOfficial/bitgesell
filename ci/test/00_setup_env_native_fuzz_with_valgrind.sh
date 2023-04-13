#!/usr/bin/env bash
#
# Copyright (c) 2019-2022 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

export LC_ALL=C.UTF-8

export CI_IMAGE_NAME_TAG="debian:bookworm"
export CONTAINER_NAME=ci_native_fuzz_valgrind
export PACKAGES="clang llvm libclang-rt-dev python3 libevent-dev bsdmainutils libboost-dev libsqlite3-dev valgrind"
export NO_DEPENDS=1
export RUN_UNIT_TESTS=false
export RUN_FUNCTIONAL_TESTS=false
export RUN_FUZZ_TESTS=true
export FUZZ_TESTS_CONFIG="--valgrind"
export GOAL="install"
<<<<<<< HEAD
# Temporarily pin dwarf 4, until valgrind can understand clang's dwarf 5
export BGL_CONFIG="--enable-fuzz --with-sanitizers=fuzzer CC=clang CXX=clang++ CFLAGS='-gdwarf-4' CXXFLAGS='-gdwarf-4'"
=======
# Temporarily pin dwarf 4, until using Valgrind 3.20 or later
export BITCOIN_CONFIG="--enable-fuzz --with-sanitizers=fuzzer CC=clang CXX=clang++ CFLAGS='-gdwarf-4' CXXFLAGS='-gdwarf-4'"
>>>>>>> ba29143d98... ci: use Debian Bookworm and Valgrind 3.19 in Valgrind jobs
export CCACHE_SIZE=200M
