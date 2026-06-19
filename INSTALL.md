# Installation

Bitgesell Core can be built from source on Linux, macOS, Windows, and BSD systems. The platform-specific build guides in [`doc/`](doc) contain the required dependencies and detailed instructions.

## Platform build guides

- [Unix/Linux](doc/build-unix.md)
- [macOS](doc/build-osx.md)
- [Windows](doc/build-windows.md)
- [FreeBSD](doc/build-freebsd.md)
- [OpenBSD](doc/build-openbsd.md)
- [NetBSD](doc/build-netbsd.md)

## Quick source build

On supported Unix-like systems, the usual autotools flow is:

```sh
./autogen.sh
./configure
make
make check
sudo make install
```

Run `./configure --help` to review optional build flags before compiling.

For deterministic release builds and platform-specific dependency notes, use the relevant guide linked above.
