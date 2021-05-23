#!/usr/bin/env bash
#
# Copyright (c) 2019-2020 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

export LC_ALL=C.UTF-8

export HOST=x86_64-apple-darwin18
export PIP_PACKAGES="zmq"
export GOAL="install"
export BGL_CONFIG="--with-gui --enable-reduce-exports --enable-external-signer"
export CI_OS_NAME="macos"
export NO_DEPENDS=1
export OSX_SDK=""
export CCACHE_SIZE=300M

#export TEST_RUNNER_EXTRA #no relevant
export RUN_UNIT_TESTS="false"
export RUN_FUNCTIONAL_TESTS="false"
export EVENT_LIBS="/usr/local/Cellar/libevent/2.1.12/lib/libevent.a /usr/local/Cellar/libevent/2.1.12/lib/libevent_pthreads.a"

export ARTIFACT_NAME="BGL-Qt.dmg"
export RELEASE_ARTIFACT_NAME="BGL-Qt-${CIRRUS_TAG}.dmg"
