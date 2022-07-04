*After branching off for a major version release of Bitcoin Core, use this
template to create the initial release notes draft.*

https://github.com/wu-emma/BGL-devwiki/wiki/0.20.0-Release-Notes-Draft
*The release notes draft is a temporary file that can be added to by anyone. See
[/doc/developer-notes.md#release-notes](/doc/developer-notes.md#release-notes)
for the process.*

*Create the draft, named* "*version* Release Notes Draft"
*(e.g. "22.0 Release Notes Draft"), as a collaborative wiki in:*


*Before the final release, move the notes back to this git repository.*

*version* Release Notes Draft
===============================

BGL Core version *version* is now available from:

  <https://BGLcore.org/bin/BGL-core-*version*/>

This release includes new features, various bug fixes and performance
improvements, as well as updated translations.

Please report bugs using the issue tracker at GitHub:

  <https://github.com/BGL/BGL/issues>

To receive security and update notifications, please subscribe to:

  <https://BGLcore.org/en/list/announcements/join/>

How to Upgrade
==============

If you are running an older version, shut it down. Wait until it has completely
shut down (which might take a few minutes for older versions), then run the
installer (on Windows) or just copy over `/Applications/BGL-Qt` (on Mac)
or `BGLd`/`BGL-qt` (on Linux).

Upgrading directly from a version of BGL Core that has reached its EOL is
possible, but it might take some time if the datadir needs to be migrated. Old
wallet versions of BGL Core are generally supported.

Compatibility
==============

BGL Core is supported and extensively tested on operating systems
using the Linux kernel, macOS 10.15+, and Windows 7 and newer.  BGL
Core should also work on most other Unix-like systems but is not as
frequently tested on them.  It is not recommended to use BGL Core on
unsupported systems.

Notable changes
===============

P2P and network changes
-----------------------

- A BGLd node will no longer rumour addresses to inbound peers by default.
  They will become eligible for address gossip after sending an ADDR, ADDRV2,
  or GETADDR message. (#21528)

Fee estimation changes
----------------------

- Fee estimation now takes the feerate of replacement (RBF) transactions into
  account. (#22539)

Rescan startup parameter removed
--------------------------------

The `-rescan` startup parameter has been removed. Wallets which require
rescanning due to corruption will still be rescanned on startup.
Otherwise, please use the `rescanblockchain` RPC to trigger a rescan. (#23123)

Updated RPCs
------------

- `upgradewallet` will now automatically flush the keypool if upgrading
  from a non-HD wallet to an HD wallet, to immediately start using the
  newly-generated HD keys. (#23093)

- a new RPC `newkeypool` has been added, which will flush (entirely
  clear and refill) the keypool. (#23093)

- The `validateaddress` RPC now returns an `error_locations` array for invalid
  addresses, with the indices of invalid character locations in the address (if
  known). For example, this will attempt to locate up to two Bech32 errors, and
  return their locations if successful. Success and correctness are only guaranteed
  if fewer than two substitution errors have been made.
  The error message returned in the `error` field now also returns more specific
  errors when decoding fails. (#16807)

- The `-deprecatedrpc=addresses` configuration option has been removed.  RPCs
  `gettxout`, `getrawtransaction`, `decoderawtransaction`, `decodescript`,
  `gettransaction verbose=true` and REST endpoints `/rest/tx`, `/rest/getutxos`,
  `/rest/block` no longer return the `addresses` and `reqSigs` fields, which
  were previously deprecated in 22.0. (#22650)
- The `getblock` RPC command now supports verbose level 3 containing transaction inputs
  `prevout` information.  The existing `/rest/block/` REST endpoint is modified to contain
  this information too. Every `vin` field will contain an additional `prevout` subfield
  describing the spent output. `prevout` contains the following keys:
  - `generated` - true if the spent coins was a coinbase.
  - `height`
  - `value`
  - `scriptPubKey`

- `listunspent` now includes `ancestorcount`, `ancestorsize`, and
  `ancestorfees` for each transaction output that is still in the mempool.
  (#12677)

- `lockunspent` now optionally takes a third parameter, `persistent`, which
  causes the lock to be written persistently to the wallet database. This
  allows UTXOs to remain locked even after node restarts or crashes. (#23065)

- The top-level fee fields `fee`, `modifiedfee`, `ancestorfees` and `descendantfees`
  returned by RPCs `getmempoolentry`,`getrawmempool(verbose=true)`,
  `getmempoolancestors(verbose=true)` and `getmempooldescendants(verbose=true)`
  are deprecated and will be removed in the next major version (use
  `-deprecated=fees` if needed in this version). The same fee fields can be accessed
  through the `fees` object in the result. WARNING: deprecated
  fields `ancestorfees` and `descendantfees` are denominated in sats, whereas all
  fields in the `fees` object are denominated in BTC. (#22689)

New RPCs
--------

Build System
------------

Files
-----

* On startup, the list of banned hosts and networks (via `setban` RPC) in
  `banlist.dat` is ignored and only `banlist.json` is considered. Bitcoin Core
  version 22.x is the only version that can read `banlist.dat` and also write
  it to `banlist.json`. If `banlist.json` already exists, version 22.x will not
  try to translate the `banlist.dat` into json. After an upgrade, `listbanned`
  can be used to double check the parsed entries. (#22570)

New settings
------------

Updated settings
----------------

- In previous releases, the meaning of the command line option
  `-persistmempool` (without a value provided) incorrectly disabled mempool
  persistence.  `-persistmempool` is now treated like other boolean options to
  mean `-persistmempool=1`. Passing `-persistmempool=0`, `-persistmempool=1`
  and `-nopersistmempool` is unaffected. (#23061)

- `-maxuploadtarget` now allows human readable byte units [k|K|m|M|g|G|t|T].
  E.g. `-maxuploadtarget=500g`. No whitespace, +- or fractions allowed.
  Default is `M` if no suffix provided. (#23249)

- If `-proxy=` is given together with `-noonion` then the provided proxy will
  not be set as a proxy for reaching the Tor network. So it will not be
  possible to open manual connections to the Tor network for example with the
  `addnode` RPC. To mimic the old behavior use `-proxy=` together with
  `-onlynet=` listing all relevant networks except `onion`. (#22834)

Tools and Utilities
-------------------

- Update `-getinfo` to return data in a user-friendly format that also reduces vertical space. (#21832)

- CLI `-addrinfo` now returns a single field for the number of `onion` addresses
  known to the node instead of separate `torv2` and `torv3` fields, as support
  for Tor V2 addresses was removed from Bitcoin Core in 22.0. (#22544)

Wallet
------

GUI changes
-----------

- UTXOs which are locked via the GUI are now stored persistently in the
  wallet database, so are not lost on node shutdown or crash. (#23065)

Low-level changes
=================

RPC
---

- `getblockchaininfo` now returns a new `time` field, that provides the chain tip time. (#22407)

Tests
-----

- For the `regtest` network the activation heights of several softforks were
  set to block height 1. They can be changed by the runtime setting
  `-testactivationheight=name@height`. (#22818)

Credits
=======

Thanks to everyone who directly contributed to this release:


As well as to everyone that helped with translations on
[Transifex](https://www.transifex.com/BGL/BGL/).
