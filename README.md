### Bitgesell (BGL)

Bitgesell (BGL) is a digital currency with built-in scarcity.

[Explore more about the project](https://bitgesell.ca)

English | [Chinese](README_zh.md)

## Table of Contents

1. [About The Project](#about-the-project)
2. [Built With](#built-with)
3. [Building with Autotools](#building-with-autotools)
4. [Building with CMake](#building-with-cmake-experimental)
5. [Usage Examples](#usage-examples)
6. [Benchmark](#benchmark)
7. [Translations](#translations)
8. [Security](#security)
9. [Contributing](#contributing)

## About The Project

![Bitgesell logo](https://github.com/BitgesellOfficial/bitgesell/blob/master/share/pixmaps/BGL64.png)

Bitgesell is a fork of Bitcoin with the following changes:

* Block reward: 90% of transaction fees are burned.

  ```sh
  nFees * 0.1 + GetBlockSubsidy()
  ```

* Block weight: 10 times smaller than Bitcoin.

  ```sh
  <= 400,000
  ```

* 100% SegWit: eliminates problems with legacy transaction types.
* Halving interval: Bitgesell has a 1-year halving cycle, compared with Bitcoin's 4-year cycle.

  ```sh
  210000 blocks / 4
  ```

* Block subsidy: maximum supply is 21,000,000 coins.

Bitgesell uses Keccak (SHA-3) as the block hashing algorithm.

The `master` branch is regularly built and tested. See [doc/build-*.md](https://github.com/BitgesellOfficial/bitgesell/tree/master/doc) for build instructions. The branch is not guaranteed to be completely stable.

[Tags](https://github.com/BitgesellOfficial/bitgesell/tags) are created regularly to indicate official stable release versions of BGL Core.

## Built With

Bitgesell includes libsecp256k1 cryptography code with the following properties:

* secp256k1 ECDSA signing, verification, and key generation.
* Additive and multiplicative tweaking of secret and public keys.
* Serialization and parsing of secret keys, public keys, and signatures.
* Constant-time, constant-memory-access signing and public key generation.
* Derandomized ECDSA through RFC6979 or a caller-provided function.
* Optional modules for public key recovery, ECDH key exchange, and Schnorr signatures according to [BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki).

General implementation properties:

* No runtime heap allocation.
* Extensive testing infrastructure.
* Structured to facilitate review and analysis.
* Intended to be portable to any system with a C89 compiler and `uint64_t` support.
* No use of floating types.
* Higher-level interfaces are exposed to minimize the API surface and improve application security.

Field operations:

* Optimized arithmetic modulo the curve's field size, `2^256 - 0x1000003D1`.
* 5 52-bit limbs.
* 10 26-bit limbs, including hand-optimized assembly for 32-bit ARM by Wladimir J. van der Laan.

Scalar operations:

* Optimized arithmetic modulo the curve's order without data-dependent branches.
* 4 64-bit limbs, relying on `__int128` support in the compiler.
* 8 32-bit limbs.
* Modular inverses for field elements and scalars based on [safegcd](https://gcd.cr.yp.to/index.html), with modifications and a variable-time variant by Peter Dettman.

Group operations:

* Point addition formula simplified for the curve equation, `y^2 = x^3 + 7`.
* Addition between points in Jacobian and affine coordinates where possible.
* Unified addition and doubling formula where necessary to avoid data-dependent branches.
* Point/x comparison without a field inversion by comparing in the Jacobian coordinate space.
* Point multiplication for verification, `a*P + b*G`.
* wNAF notation for point multiplicands.
* Larger window for multiples of `G`, using precomputed multiples.
* Shamir's trick to multiply with the public key and generator simultaneously.
* secp256k1's efficiently computable endomorphism to split the `P` multiplicand into two half-sized values.

Point multiplication for signing:

* Precomputed table of multiples of powers of 16 multiplied with the generator, so general multiplication becomes a series of additions.
* Designed to be free of timing side channels for secret-key operations on reasonable hardware and toolchains.
* Branch-free conditional moves for uniform table access.
* No data-dependent branches.
* Optional runtime blinding that attempts to frustrate differential power analysis.

## Building with Autotools

```sh
./autogen.sh
./configure
make
make check
sudo make install
```

To compile optional modules, such as Schnorr signatures, run `./configure` with the corresponding flags, such as `--enable-module-schnorrsig`.

Run the following command to see the full list of available flags:

```sh
./configure --help
```

## Building with CMake (experimental)

To maintain a pristine source tree, CMake encourages an out-of-source build with a separate build tree.

### Building on POSIX systems

```sh
mkdir build && cd build
cmake ..
make
make check
sudo make install
```

To compile optional modules, such as Schnorr signatures, run `cmake` with the corresponding flags, such as `-DSECP256K1_ENABLE_MODULE_SCHNORRSIG=ON`.

Run the following command to see the full list of available flags:

```sh
cmake .. -LH
```

### Cross compiling

Preconfigured toolchain files are available in the `cmake` directory. For example, to cross compile for Windows:

```sh
cmake .. -DCMAKE_TOOLCHAIN_FILE=../cmake/x86_64-w64-mingw32.toolchain.cmake
```

To cross compile for Android with the [NDK](https://developer.android.com/ndk/guides/cmake), assuming the `ANDROID_NDK_ROOT` environment variable has been set:

```sh
cmake .. \
  -DCMAKE_TOOLCHAIN_FILE="${ANDROID_NDK_ROOT}/build/cmake/android.toolchain.cmake" \
  -DANDROID_ABI=arm64-v8a \
  -DANDROID_PLATFORM=28
```

### Building on Windows

To build on Windows with Visual Studio, specify a proper [generator](https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html#visual-studio-generators) for a new build tree.

The following example assumes Visual Studio 2022 and CMake v3.21+ in "Developer Command Prompt for VS 2022":

```bat
cmake -G "Visual Studio 17 2022" -A x64 -S . -B build
cmake --build build --config RelWithDebInfo
```

## Usage Examples

Usage examples can be found in the [examples](examples) directory. To compile them, configure with `--enable-examples`.

* [ECDSA example](examples/ecdsa.c)
* [Schnorr signatures example](examples/schnorr.c)
* [Deriving a shared secret (ECDH) example](examples/ecdh.c)

To compile the Schnorr signature and ECDH examples, configure with `--enable-module-schnorrsig` and `--enable-module-ecdh`.

## Benchmark

If configured with `--enable-benchmark`, which is the default, benchmarking binaries for libsecp256k1 functions will be available in the root directory after the build.

## Translations

Changes to translations, as well as new translations, can be submitted to [BGL Core's Transifex page](https://www.transifex.com/bitcoin/bitcoin/).

Translations are periodically pulled from Transifex and merged into the git repository. See the [translation process](doc/translation_process.md) for details.

## Security

See [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
