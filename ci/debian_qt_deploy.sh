#!/usr/bin/env bash

export LC_ALL=C.UTF-8

set -o errexit; source ./ci/test/00_setup_env.sh

echo "INSTALL"

apt-get update

apt-get install --no-install-recommends --no-upgrade -y build-essential devscripts debhelper g++-8 libssl-dev wget pkg-config libevent-dev fakeroot

echo "INSTALL DONE"

export ARTIFACT_NAME="bitgesell-qt-amd64.deb"
export RELEASE_ARTIFACT_NAME="bitgesell-qt_${CIRRUS_TAG}_amd64.deb"

mv ./debian.qt ./debian
chmod +x ./debian/build-in-docker.sh
set -o errexit; source ./debian/build-in-docker.sh
set -o errexit; source ./ci/test/07_script.sh
