#!/bin/bash

set -e

debuild -S

finish() {
    docker stop $container >/dev/null
    docker container rm $container >/dev/null
}

docker pull ubuntu:22.04
container=`docker run -dit -e TZ='Etc/UTC' -e DEBIAN_FRONTEND='noninteractive' ubuntu:22.04 `
trap finish EXIT

docker exec $container apt-get -y update
docker exec $container apt-get -y install apt-utils devscripts sudo #dpkg-dev
docker exec $container mkdir -p /root/repo
docker exec $container useradd user
docker exec $container mkdir /home/user
docker exec $container chown user.user /home/user
docker exec $container sudo -u user mkdir /home/user/build
docker cp ../bitgesell_0.1.12.dsc $container:/root/repo/
docker cp ../bitgesell_0.1.12.tar.xz $container:/root/repo/
# docker exec -w /root/repo $container sh -c "dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz"
docker exec -w /root/repo $container sh -c "apt-ftparchive sources . > Sources"
docker exec $container sh -c "echo deb-src [trusted=yes] file:/root/repo ./ >> /etc/apt/sources.list"
docker exec $container apt-get -y -o APT::Sandbox::User=root update
docker exec $container apt-get -y build-dep bitgesell
docker exec $container chmod a+rX /root
docker exec $container chmod -R a+rX /root/repo
docker exec -w /home/user/build $container sudo -u user apt-get -y source bitgesell
docker exec -w /home/user/build/bitgesell-0.1.12 $container sudo -u user debuild -b
docker cp $container:/home/user/build/bitgesell_0.1.12_amd64.deb bitgesell_0.1.12_amd64.deb
