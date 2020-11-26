BGL Core
=============

Setup
---------------------
BGL Core is the original BGL client and it builds the backbone of the network. It downloads and, by default, stores the entire history of BGL transactions, which requires a few hundred gigabytes of disk space. Depending on the speed of your computer and network connection, the synchronization process can take anywhere from a few hours to a day or more.

To download BGL Core, visit [BGLcore.org](https://BGLcore.org/en/download/).

Running
---------------------
The following are some helpful notes on how to run BGL Core on your native platform.

### Unix

Unpack the files into a directory and run:

- `bin/BGL-qt` (GUI) or
- `bin/BGLd` (headless)

### Windows

Unpack the files into a directory, and then run BGL-qt.exe.

### macOS

Drag BGL Core to your applications folder, and then run BGL Core.

### Need Help?

* See the documentation at the [BGL Wiki](https://bitgesell.ca)
for help and more information. The compatibility is largely maintained with BTC code base, so it's wiki and developer documentation stays relevant to BGL.
* Ask for help on [#BGL](http://webchat.freenode.net?channels=BGL) on Freenode. If you don't have an IRC client, use [webchat here](http://webchat.freenode.net?channels=BGL).
* Ask for help on the [BGLTalk](https://BGLtalk.org/) forums, in the [Technical Support board](https://BGLtalk.org/index.php?board=4.0).

Building
---------------------
The following are developer notes on how to build BGL Core on your native platform. They are not complete guides, but include notes on the necessary libraries, compile flags, etc.

- [Dependencies](dependencies.md)
- [macOS Build Notes](build-osx.md)
- [Unix Build Notes](build-unix.md)
- [Windows Build Notes](build-windows.md)
- [FreeBSD Build Notes](build-freebsd.md)
- [OpenBSD Build Notes](build-openbsd.md)
- [NetBSD Build Notes](build-netbsd.md)
- [Gitian Building Guide (External Link)](https://github.com/BGL-core/docs/blob/master/gitian-building.md)

Development
---------------------
The BGL repo's [root README](/README.md) contains relevant information on the development process and automated testing.

- [Developer Notes](developer-notes.md)
- [Productivity Notes](productivity.md)
- [Release Notes](release-notes.md)
- [Release Process](release-process.md)
- [Source Code Documentation (External Link)](https://doxygen.BGLcore.org/)
- [Translation Process](translation_process.md)
- [Translation Strings Policy](translation_strings_policy.md)
- [JSON-RPC Interface](JSON-RPC-interface.md)
- [Unauthenticated REST Interface](REST-interface.md)
- [Shared Libraries](shared-libraries.md)
- [BIPS](bips.md)
- [Dnsseed Policy](dnsseed-policy.md)
- [Benchmarking](benchmarking.md)

### Resources
* Discuss on the [BGLTalk](https://BGLtalk.org/) forums, in the [Development & Technical Discussion board](https://BGLtalk.org/index.php?board=6.0).
* Discuss project-specific development on #BGL-core-dev on Freenode. If you don't have an IRC client, use [webchat here](http://webchat.freenode.net/?channels=BGL-core-dev).
* Discuss general BGL development on #BGL-dev on Freenode. If you don't have an IRC client, use [webchat here](http://webchat.freenode.net/?channels=BGL-dev).

### Miscellaneous
- [Assets Attribution](assets-attribution.md)
- [BGL.conf Configuration File](BGL-conf.md)
- [Files](files.md)
- [Fuzz-testing](fuzzing.md)
- [Reduce Memory](reduce-memory.md)
- [Reduce Traffic](reduce-traffic.md)
- [Tor Support](tor.md)
- [Init Scripts (systemd/upstart/openrc)](init.md)
- [ZMQ](zmq.md)
- [PSBT support](psbt.md)

License
---------------------
Distributed under the [MIT software license](/COPYING).
