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

The https://github.com/BGL-core/gui repository is used exclusively for the development of the GUI. Its master branch is identical in all monotree repositories. Release branches and tags do not exist, so please do not fork that repository unless it is for development reasons.

Official thread: [click here](https://bitcointalk.org/index.php?topic=5238559.0)


## Automated Testing

Developers are strongly encouraged to write [unit tests](https://github.com/BitgesellOfficial/bitgesell/blob/master/src/test/README.md) for new code, and to
submit new unit tests for old code. Unit tests can be compiled and run
(assuming they weren't disabled in configure) with: `make check`. Further details on running
and extending unit tests can be found in [src/test/README.md](https://github.com/BitgesellOfficial/bitgesell/blob/master/src/test/README.md). <br>

There are also [regression and integration tests](https://github.com/BitgesellOfficial/bitgesell/tree/master/test), written
in Python. <br>
These tests can be run (if the [test dependencies](https://github.com/BitgesellOfficial/bitgesell/tree/master/test) with: `test/functional/test_runner.py` <br>

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

If you don't mind more setup in return for more speed, replace
`autocomplete-clang` and `linter-clang` with `you-complete-me`. This requires
[setting up ycmd](https://github.com/ycm-core/ycmd#building).

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch 
3. Commit your Changes 
4. Push to the Branch  
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See [LICENSE](https://github.com/BitgesellOfficial/bitgesell/blob/master/COPYING) for more information.



<!-- CONTACT -->
## Contact

Discord - [Bitgesell](https://discord.com/invite/Ubp359vZEF)

Twitter: [Bitgesell](https://twitter.com/Bitgesell)

Medium: [Bitgesell](https://bitgesell.medium.com/)

Facebook: [Bitgesell](https://www.facebook.com/Bitgesell)


<!-- ACKNOWLEDGEMENTS -->
## Translations

Changes to translations as well as new translations can be submitted to
[BGL Core's Transifex page](https://www.transifex.com/bitcoin/bitcoin/).

Translations are periodically pulled from Transifex and merged into the git repository. See the
[translation process](doc/translation_process.md) for details on how this works.

**Important**: We do not accept translation changes as GitHub pull requests because the next
pull from Transifex would automatically overwrite them again.


