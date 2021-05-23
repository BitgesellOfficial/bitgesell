![](share/pixmaps/BGL64.png) BGL Core integration/staging tree

What is BGL?
----------------

BGL is an experimental digital currency that enables instant payments to
anyone, anywhere in the world. BGL uses peer-to-peer technology to operate
with no central authority: managing transactions and issuing money are carried
out collectively by the network. BGL Core is the name of open source
software which enables the use of this currency.

For more information read the original BGL whitepaper.

License
-------

Essentially this is a full BGL fork, but:
* Block Reward = nFees*0.1 + GetBlockSubsidy()    // Burn rate is 90% of tx fees
* Block Weight <= 400,000;                        // 10 times smaller than BGL
* 100% Segwit                                     // Eliminates problems with legacy types of transactions
* Halving Interval = 210000 blocks / 4;           // Halving is every year (BGL halving is every 4 years)
* Block Subsidy = 50 * 4;                         // 21 000 000 coins max
* Hashing algorithm for blocks is Keccak (sha-3).
The `master` branch is regularly built (see doc/build-*.md for instructions) and tested, but is not guaranteed to be
completely stable. [Tags](https://github.com/BGL/BGL/tags) are created
regularly to indicate new official, stable release versions of BGL Core.

The https://github.com/BGL-core/gui repository is used exclusively for the
development of the GUI. Its master branch is identical in all monotree
repositories. Release branches and tags do not exist, so please do not fork
that repository unless it is for development reasons.

Official thread: https://BGLtalk.org/index.php?topic=5238559.0

License
-------

Testing and code review is the bottleneck for development; we get more pull
requests than we can review and test on short notice. Please be patient and help out by testing
other people's pull requests, and remember this is a security-critical project where any mistake might cost people
lots of money.

### Automated Testing

Developers are strongly encouraged to write [unit tests](src/test/README.md) for new code, and to
submit new unit tests for old code. Unit tests can be compiled and run
(assuming they weren't disabled in configure) with: `make check`. Further details on running
and extending unit tests can be found in [/src/test/README.md](/src/test/README.md).

There are also [regression and integration tests](/test), written
in Python.
These tests can be run (if the [test dependencies](/test) are installed) with: `test/functional/test_runner.py`

The CI (Continuous Integration) systems make sure that every pull request is built for Windows, Linux, and macOS,
and that unit/sanity tests are run automatically.

### Manual Quality Assurance (QA) Testing

Changes should be tested by somebody other than the developer who wrote the
code. This is especially important for large or high-risk changes. It is useful
to add a test plan to the pull request description if testing the changes is
not straightforward.

Translations
------------

Changes to translations as well as new translations can be submitted to
[BGL Core's Transifex page](https://www.transifex.com/bitcoin/bitcoin/).

Translations are periodically pulled from Transifex and merged into the git repository. See the
[translation process](doc/translation_process.md) for details on how this works.

**Important**: We do not accept translation changes as GitHub pull requests because the next
pull from Transifex would automatically overwrite them again.
