<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/BitgesellOfficial/bitgesell">
    <img src="https://github.com/BitgesellOfficial/bitgesell/blob/master/share/pixmaps/BGL64.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Bitgesell (BGL)</h3>

  <p align="center">
    Bitgesell (BGL) is an experimental digital currency
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
* Optional module for Schnorr signatures according to [BIP-340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki) (experimental).

<b>Bitgesell is a fork of BGL with the following changes:</b> <br>
* Block Reward [Burn rate is 90% of tx fees]
  ```sh
  nFees*0.1 + GetBlockSubsidy()  
  ```
* Block Weight [10 times smaller than Bitgesell]
  ```sh
  <= 400,000
  ```
* 100% Segwit 
  ```sh
  Eliminates problems with legacy type of transactions
  ```
* Halving Interval [Halving cycle of bitgetsell is 1yr while that of BGL is 4yr]
  ```sh
  210000 blocks/4
  ```
* Block Subsidy [Max coins = 21,000,000] <br>
  `210000 blocks/4` <br> <hr>
  `Hashing algorithm for blocks is Keccak (sha-3).` <br> <hr>
  `The master branch is regularly built (see` [doc/build-*.md](https://github.com/BitgesellOfficial/bitgesell/tree/master/doc) `for instructions) and tested, but is not guaranteed to be completely stable.` <br> <hr>
  [tags](https://github.com/BitgesellOfficial/bitgesell/tags) `are created regularly to indicate new official, stable release versions of BGL Core.` <br>
 
 
### Built With

* [C++](#)
* [C](#)
* [Python](#)
* [SourcePawn](#)
* [M4](#)
* [Shell](#)


<!-- GETTING STARTED -->
## Getting Started

Visit official website: [click here](https://bitgesell.ca/) <br>

    $ ./autogen.sh
    $ ./configure
    $ make
    $ make check  # run the test suite
    $ sudo make install  # optional

Test coverage
-----------

The CI (Continuous Integration) systems make sure that every pull request is built for Windows, Linux, and macOS,
and that unit/sanity tests are run automatically. <br>


## Manual Quality Assurance (QA) Testing

Changes should be tested by somebody other than the developer who wrote the
code. This is especially important for large or high-risk changes. It is useful
to add a test plan to the pull request description if testing the changes is
not straightforward.


<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/BitgesellOfficial/bitgesell/issues) for a list of proposed features (and known issues).


    $ mkdir -p coverage
    $ gcovr --exclude 'src/bench*' --html --html-details -o coverage/coverage.html

Benchmark
------------
If configured with `--enable-benchmark` (which is the default), binaries for benchmarking the libsecp256k1 functions will be present in the root directory after the build.

To print the benchmark result to the command line:

    $ ./bench_name

To create a CSV file for the benchmark result :

    $ ./bench_name | sed '2d;s/ \{1,\}//g' > bench_name.csv

Reporting a vulnerability
------------

