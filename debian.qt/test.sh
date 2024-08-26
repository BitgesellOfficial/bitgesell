#!/bin/bash

finish() {
    docker stop $container >/dev/null
    docker container rm $container >/dev/null
}

docker pull ubuntu:22.04
container=`docker run -dit -e TZ='Etc/UTC' -e DEBIAN_FRONTEND='noninteractive' ubuntu:22.04`
trap finish EXIT

docker exec $container apt-get -y update
docker exec $container apt-get -y install apt-utils #dpkg-dev
docker exec $container mkdir /root/repo
docker cp ./bitgesell-qt_0.1.13_amd64.deb $container:/root/repo
# docker exec -w /root/repo $container sh -c "dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz"
docker exec -w /root/repo $container sh -c "apt-ftparchive packages . > Packages"
docker exec $container sh -c "echo deb [trusted=yes] file:/root/repo ./ >> /etc/apt/sources.list"
# docker exec $container rm -rf /var/lib/apt/lists/ # Why is this needed?
# docker exec $container apt-get -y clean
docker exec $container apt-get -y -o APT::Sandbox::User=root update
docker exec $container apt-get -y install bitgesell-qt
docker exec $container sh -c \
    "if { BGL-cli --help && BGLd --help && BGL-tx --help; } > /dev/null; then \
        echo 'Test passed.'; \
    else
        echo 'Test failed.'; \
    fi"
