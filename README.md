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
* secp256k1 ECDSA signing/verification and key generation.
* Additive and multiplicative tweaking of secret/public keys.
* Serialization/parsing of secret keys, public keys, signatures.
* Constant time, constant memory access signing and public key generation.
* Derandomized ECDSA (via RFC6979 or with a caller provided function.)
* Very efficient implementation.
* Suitable for embedded systems.
* Optional module for public key recovery.
* Optional module for ECDH key exchange.
* Optional module for Schnorr signatures according to [BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki).

<b>Bitgesell is a fork of Bitcoin with the following changes:</b> <br>
* Block Reward [Burn rate is 90% of tx fees]
  ```sh
  nFees*0.1 + GetBlockSubsidy()  
  ```
* Block Weight [10 times smaller than Bitcoin]
  ```sh
  <= 400,000
  ```
* 100% Segwit 
  ```sh
  Eliminates problems with legacy type of transactions
  ```
* Halving Interval [Halving cycle of Bitgesell is 1 year while that of Bitcoin is 4 years]
  ```sh
  210000 blocks/4
  ```
* Block Subsidy [Max coins = 21,000,000] <br>
  `210000 blocks/4` <br> <hr>
  `Hashing algorithm for blocks is Keccak (sha-3).` <br> <hr>
  `The master branch is regularly built (see` [doc/build-*.md](https://github.com/BitgesellOfficial/bitgesell/tree/master/doc) `for instructions) and tested, but is not guaranteed to be completely stable.` <br> <hr>
  [tags](https://github.com/BitgesellOfficial/bitgesell/tags) `are created regularly to indicate new official, stable release versions of BGL Core.` <br>
 
 
### Built With

* General
  * No runtime heap allocation.
  * Extensive testing infrastructure.
  * Structured to facilitate review and analysis.
  * Intended to be portable to any system with a C89 compiler and uint64_t support.
  * No use of floating types.
  * Expose only higher level interfaces to minimize the API surface and improve application security. ("Be difficult to use insecurely.")
* Field operations
  * Optimized implementation of arithmetic modulo the curve's field size (2^256 - 0x1000003D1).
    * Using 5 52-bit limbs
    * Using 10 26-bit limbs (including hand-optimized assembly for 32-bit ARM, by Wladimir J. van der Laan).
      * This is an experimental feature that has not received enough scrutiny to satisfy the standard of quality of this library but is made available for testing and review by the community.
* Scalar operations
  * Optimized implementation without data-dependent branches of arithmetic modulo the curve's order.
    * Using 4 64-bit limbs (relying on __int128 support in the compiler).
    * Using 8 32-bit limbs.
* Modular inverses (both field elements and scalars) based on [safegcd](https://gcd.cr.yp.to/index.html) with some modifications, and a variable-time variant (by Peter Dettman).
* Group operations
  * Point addition formula specifically simplified for the curve equation (y^2 = x^3 + 7).
  * Use addition between points in Jacobian and affine coordinates where possible.
  * Use a unified addition/doubling formula where necessary to avoid data-dependent branches.
  * Point/x comparison without a field inversion by comparison in the Jacobian coordinate space.
* Point multiplication for verification (a*P + b*G).
  * Use wNAF notation for point multiplicands.
  * Use a much larger window for multiples of G, using precomputed multiples.
  * Use Shamir's trick to do the multiplication with the public key and the generator simultaneously.
  * Use secp256k1's efficiently-computable endomorphism to split the P multiplicand into 2 half-sized ones.
* Point multiplication for signing
  * Use a precomputed table of multiples of powers of 16 multiplied with the generator, so general multiplication becomes a series of additions.
  * Intended to be completely free of timing sidechannels for secret-key operations (on reasonable hardware/toolchains)
    * Access the table with branch-free conditional moves so memory access is uniform.
    * No data-dependent branches
  * Optional runtime blinding which attempts to frustrate differential power analysis.
  * The precomputed tables add and eventually subtract points for which no known scalar (secret key) is known, preventing even an attacker with control over the secret key used to control the data internally.

Building with Autotools
-----------------------

    $ ./autogen.sh
    $ ./configure
    $ make
    $ make check  # run the test suite
    $ sudo make install  # optional

To compile optional modules (such as Schnorr signatures), you need to run `./configure` with additional flags (such as `--enable-module-schnorrsig`). Run `./configure --help` to see the full list of available flags.

Building with CMake (experimental)
----------------------------------

To maintain a pristine source tree, CMake encourages to perform an out-of-source build by using a separate dedicated build tree.

### Building on POSIX systems

    $ mkdir build && cd build
    $ cmake ..
    $ make
    $ make check  # run the test suite
    $ sudo make install  # optional

To compile optional modules (such as Schnorr signatures), you need to run `cmake` with additional flags (such as `-DSECP256K1_ENABLE_MODULE_SCHNORRSIG=ON`). Run `cmake .. -LH` to see the full list of available flags.

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
