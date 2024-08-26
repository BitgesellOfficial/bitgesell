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

#docker cp ./debian/updateunattended.sh $container:/root/
#docker exec $container /root/updateunattended.sh
docker exec $container apt-get update
docker exec $container apt-get -y install apt-utils devscripts sudo #dpkg-dev
docker exec $container apt-get -y install libqrencode-dev qttools5-dev qttools5-dev-tools libsqlite3-dev
docker exec $container mkdir -p /root/repo
docker exec $container useradd user
docker exec $container mkdir /home/user
docker exec $container chown user.user /home/user
docker exec $container sudo -u user mkdir /home/user/build
docker cp ../bitgesell-qt_0.1.13.dsc $container:/root/repo/
docker cp ../bitgesell-qt_0.1.13.tar.xz $container:/root/repo/
# docker exec -w /root/repo $container sh -c "dpkg-scanpackages . /dev/null | gzip -9c > Packages.gz"

docker exec -w /root/repo $container sh -c "apt-ftparchive sources . > Sources"
docker exec $container sh -c "echo deb-src [trusted=yes] file:/root/repo ./ >> /etc/apt/sources.list"
docker exec $container apt-get -y -o APT::Sandbox::User=root update
docker exec $container apt-get -y build-dep bitgesell-qt
docker exec $container chmod a+rX /root
docker exec $container chmod -R a+rX /root/repo
docker exec -w /home/user/build $container sudo -u user apt-get -y source bitgesell-qt
docker exec -w /home/user/build/bitgesell-qt-0.1.13 $container sudo -u user debuild -b
docker cp $container:/home/user/build/bitgesell-qt_0.1.13_amd64.deb bitgesell-qt_0.1.13_amd64.deb
docker cp $container:/home/user/build/bitgesell-qt-dbg_0.1.13_amd64.deb bitgesell-qt-dbg_0.1.13_amd64.deb
