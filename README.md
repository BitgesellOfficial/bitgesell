<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/BitgesellOfficial/bitgesell">
    <img src="https://github.com/BitgesellOfficial/bitgesell/blob/master/share/pixmaps/BGL64.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Bitgesell (BGL)</h3>

  <p align="center">
    Bitgesell (BGL) is a digital currency
    <br />
    <a href="https://bitgesell.ca/"><strong>Explore more about project »</strong></a>
    <br />
    <br />
    <a href="#">English</a>
    ·
    <a href="https://github.com/BitgesellOfficial/bitgesell/blob/master/README-zh.md">Chinese</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <!-- <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul> -->
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Translations</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project


![Product Name Screen Shot](https://github.com/BitgesellOfficial/bitgesell/blob/master/share/pixmaps/BGL64.png) 



Features:
* Bitcoin Core-derived full node, wallet, and RPC software for the Bitgesell network.
* Keccak (SHA-3) block hashing.
* 100% SegWit transaction policy.
* 90% transaction-fee burn model: miners receive `nFees * 0.1 + GetBlockSubsidy()`.
* Smaller 400,000-unit block weight target.
* One-year halving interval (`210000 / 4` blocks) with a 21,000,000 BGL maximum supply.

`master` is regularly built and tested, but it is not guaranteed to be completely stable. See the platform-specific guides in [`doc/`](https://github.com/BitgesellOfficial/bitgesell/tree/master/doc) for full build instructions. [Tags](https://github.com/BitgesellOfficial/bitgesell/tags) are created for official stable BGL Core releases.


### Built With

* C++ full-node and wallet code derived from Bitcoin Core.
* Autotools-based build system with platform-specific documentation under `doc/`.
* LevelDB for chain-state storage.
* secp256k1 cryptography for ECDSA/Schnorr primitives.
* Qt GUI components for the desktop wallet.
* Functional, unit, and lint test suites under `test/` and `src/test/`.

Building with Autotools
-----------------------

    $ ./autogen.sh
    $ ./configure
    $ make
    $ make check  # run the test suite
    $ sudo make install  # optional

For dependency and platform-specific setup, start with the guides in [`doc/`](doc/), especially the Unix, Windows, macOS, and OpenBSD build documents.

Building with CMake (experimental)
----------------------------------

To maintain a pristine source tree, CMake encourages out-of-source builds using a separate build directory.

### Building on POSIX systems

    $ mkdir build && cd build
    $ cmake ..
    $ make
    $ make check  # run the test suite
    $ sudo make install  # optional

### Cross compiling

To alleviate issues with cross compiling, preconfigured toolchain files are available in the `cmake` directory.
For example, to cross compile for Windows:

    $ cmake .. -DCMAKE_TOOLCHAIN_FILE=../cmake/x86_64-w64-mingw32.toolchain.cmake

To cross compile for Android with [NDK](https://developer.android.com/ndk/guides/cmake) (using NDK's toolchain file, and assuming the `ANDROID_NDK_ROOT` environment variable has been set):

    $ cmake .. -DCMAKE_TOOLCHAIN_FILE="${ANDROID_NDK_ROOT}/build/cmake/android.toolchain.cmake" -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=28

### Building on Windows

To build on Windows with Visual Studio, a proper [generator](https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html#visual-studio-generators) must be specified for a new build tree.

The following example assumes using of Visual Studio 2022 and CMake v3.21+.

In "Developer Command Prompt for VS 2022":

    >cmake -G "Visual Studio 17 2022" -A x64 -S . -B build
    >cmake --build build --config RelWithDebInfo

Usage examples
-----------
Usage examples can be found in the [examples](examples) directory. To compile them you need to configure with `--enable-examples`.
  * [ECDSA example](examples/ecdsa.c)
  * [Schnorr signatures example](examples/schnorr.c)
  * [Deriving a shared secret (ECDH) example](examples/ecdh.c)

To compile the Schnorr signature and ECDH examples, you also need to configure with `--enable-module-schnorrsig` and `--enable-module-ecdh`.

Benchmark
------------
If configured with `--enable-benchmark` (which is the default), binaries for benchmarking the libsecp256k1 functions will be present in the root directory after the build.

Facebook: [Bitgesell](https://www.facebook.com/Bitgesell)


<!-- ACKNOWLEDGEMENTS -->
## Translations

Changes to translations as well as new translations can be submitted to
[BGL Core's Transifex page](https://www.transifex.com/bitcoin/bitcoin/).

Translations are periodically pulled from Transifex and merged into the git repository. See the
[translation process](doc/translation_process.md) for details on how this works.

See [SECURITY.md](SECURITY.md)

Contributing to libsecp256k1
------------

See [CONTRIBUTING.md](CONTRIBUTING.md)
