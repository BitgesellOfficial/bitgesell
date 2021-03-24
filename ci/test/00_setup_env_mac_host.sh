#!/usr/bin/env bash
#
# Copyright (c) 2019-2020 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

export LC_ALL=C.UTF-8
export PACKAGE_MANAGER_INSTALL="echo"
#export MAKEJOBS #default
export DANGER_RUN_CI_ON_HOST="true"
#export TEST_RUNNER_PORT_MIN #default
export CCACHE_SIZE=300M
#export CCACHE_DIR #default


export HOST=x86_64-apple-darwin16
#export CONTAINER_NAME #no relevant
#export DOCKER_NAME_TAG #no relevant


#eexport NO_DEPENDS default
#export DEP_OPTS #no relevant
export GOAL="deploy"
export BGL_CONFIG="--with-gui=qt5 --disable-wallet --disable-bench"
#export PACKAGES  #no relevant
export PIP_PACKAGES="zmq ds_store mac_alias"


#export TEST_RUNNER_EXTRA #no relevant
export RUN_UNIT_TESTS="false"
export RUN_FUNCTIONAL_TESTS="false"
export EVENT_LIBS="/usr/local/Cellar/libevent/2.1.12/lib/libevent.a /usr/local/Cellar/libevent/2.1.12/lib/libevent_pthreads.a"

export ARTIFACT_NAME="BGL-Qt.dmg"
export RELEASE_ARTIFACT_NAME="BGL-Qt-${CIRRUS_TAG}.dmg"