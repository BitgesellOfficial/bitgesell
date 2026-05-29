FROM debian:bookworm-slim AS builder

WORKDIR /src

RUN apt-get update && apt-get install --no-install-recommends -y \
    git ca-certificates \
    make automake libtool pkg-config \
    gcc g++ libc6-dev \
    libboost-system-dev libboost-filesystem-dev libboost-chrono-dev \
    libboost-thread-dev libboost-test-dev \
    libevent-dev libssl-dev \
    libminiupnpc-dev libnatpmp-dev \
    libzmq3-dev \
    python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN ./autogen.sh && ./configure --with-incompatible-bdb --without-gui \
    --disable-tests --disable-bench --enable-reduce-exports \
    --enable-util-cli --enable-util-tx \
    CFLAGS="-O2" CXXFLAGS="-O2" \
    && make -j$(nproc) \
    && make install DESTDIR=/install

FROM debian:bookworm-slim

RUN apt-get update && apt-get install --no-install-recommends -y \
    libboost-system1.74 libboost-filesystem1.74 libboost-chrono1.74 \
    libboost-thread1.74 libevent-2.1 libevent-pthreads-2.1 \
    libssl3 libminiupnpc libnatpmp \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install/usr/local /usr/local

RUN mkdir -p /root/.bitgesell /data

EXPOSE 8332 8333 18332 18333

VOLUME ["/root/.bitgesell"]

ENTRYPOINT ["/usr/local/bin/BGLd"]

CMD ["-printtoconsole", "-datadir=/root/.bitgesell"]
