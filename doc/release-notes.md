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

Updated RPCs
------------

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

Low-level changes
=================

RPC
---

- `getblockchaininfo` now returns a new `time` field, that provides the chain tip time. (#22407)

Tests
-----

- For the `regtest` network the activation heights of several softforks were
  changed.
  * BIP 34 (blockheight in coinbase) from 500 to 2 (#16333)
  * BIP 66 (DERSIG) from 1251 to 102 (#22632)
  * BIP 65 (CLTV) from 1351 to 111 (#21862)

Credits
=======

Thanks to everyone who directly contributed to this release:


As well as to everyone that helped with translations on
[Transifex](https://www.transifex.com/BGL/BGL/).
