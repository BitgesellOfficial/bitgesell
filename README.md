BGL Core integration/staging tree        ![](share/pixmaps/BGL64.png)
=====================================

What is BGL?
----------------

BGL is an experimental digital currency that enables instant payments to
anyone, anywhere in the world. BGL uses peer-to-peer technology to operate
with no central authority: managing transactions and issuing money are carried
out collectively by the network. BGL Core is the name of open source
software which enables the use of this currency.

Specifications

Essentially this is a full bitcoin fork, but:
* Block Reward = nFees*0.1 + GetBlockSubsidy()    // Burn rate is 90% of tx fees
* Block Weight <= 400,000;                        // 10 times smaller than bitcoin
* 100% Segwit                                     // Eliminates problems with legacy types of transactions
* Halving Interval = 210000 blocks / 4;           // Halving is every year (bitcoin halving is every 4 years)
* Block Subsidy = 50 * 4;                         // 21 000 000 coins max
* Hashing algorithm for blocks is Keccak (sha-3).

Official thread: https://bitcointalk.org/index.php?topic=5238559.0

License
-------

BGL Core is released under the terms of the MIT license. See [COPYING](COPYING) for more
information or see https://opensource.org/licenses/MIT.
