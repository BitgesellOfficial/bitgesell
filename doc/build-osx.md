# macOS Build Guide

**Updated for MacOS [11.2](https://www.apple.com/macos/big-sur/)**

This guide describes how to build BGLd, command-line utilities, and GUI on macOS

## Preparation

The commands in this guide should be executed in a Terminal application.
The built-in one is located in
```
/Applications/Utilities/Terminal.app
```

## Preparation
Install the macOS command line tools:

```shell
xcode-select --install
```

Upon running the command, you should see a popup appear.
Click on `Install` to continue the installation process.

### 2. Homebrew Package Manager

Homebrew is a package manager for macOS that allows one to install packages from the command line easily.
While several package managers are available for macOS, this guide will focus on Homebrew as it is the most popular.
Since the examples in this guide which walk through the installation of a package will use Homebrew, it is recommended that you install it to follow along.
Otherwise, you can adapt the commands to your package manager of choice.

To install the Homebrew package manager, see: https://brew.sh

Note: If you run into issues while installing Homebrew or pulling packages, refer to [Homebrew's troubleshooting page](https://docs.brew.sh/Troubleshooting).

### 3. Install Required Dependencies

The first step is to download the required dependencies.
These dependencies represent the packages required to get a barebones installation up and running.

See [dependencies.md](dependencies.md) for a complete overview.

To install, run the following from your terminal:

``` bash
brew install automake libtool boost pkg-config libevent
```

### 4. Clone BGL repository

`git` should already be installed by default on your system.
Now that all the required dependencies are installed, let's clone the BGL Core repository to a directory.
All build scripts and commands will run from this directory.

``` bash
git clone https://github.com/BitgesellOfficial/bitgesell.git
```

### 5. Install Optional Dependencies

#### Wallet Dependencies

It is not necessary to build wallet functionality to run `BGLd` or  `BGL-qt`.

###### Descriptor Wallet Support

`sqlite` is required to support for descriptor wallets.

macOS ships with a useable `sqlite` package, meaning you don't need to
install anything.

###### Legacy Wallet Support

`berkeley-db@4` is only required to support for legacy wallets.
Skip if you don't intend to use legacy wallets.

``` bash
brew install berkeley-db@4
```
---

#### GUI Dependencies

###### Qt

BGL Core includes a GUI built with the cross-platform Qt Framework.
To compile the GUI, we need to install `qt@5`.
Skip if you don't intend to use the GUI.

``` bash
brew install qt@5
```

Note: Building with Qt binaries downloaded from the Qt website is not officially supported.
See the notes in [#7714](https://github.com/bitcoin/bitcoin/issues/7714).

###### qrencode

The GUI can encode addresses in a QR Code. To build in QR support for the GUI, install `qrencode`.
Skip if not using the GUI or don't want QR code functionality.

``` bash
brew install qrencode
```
---

Then install [Homebrew](https://brew.sh).

## Dependencies
```shell
brew install automake libtool boost miniupnpc libnatpmp pkg-config python qt@5 libevent qrencode
```

---

#### Deploy Dependencies

You can deploy a `.zip` containing the Bitgesell Core application using `make deploy`.
It is required that you have `python` installed.

The wallet support requires one or both of the dependencies ([*SQLite*](#sqlite) and [*Berkeley DB*](#berkeley-db)) in the sections below.
To build BGL Core without wallet, see [*Disable-wallet mode*](#disable-wallet-mode).

#### SQLite

If `berkeley-db@4` is installed, then legacy wallet support will be built.
If `sqlite` is installed, then descriptor wallet support will also be built.
Additionally, this explicitly disables the GUI.

```shell
brew install sqlite
```

In that case the Homebrew package will prevail.

#### Berkeley DB

It is recommended to use Berkeley DB 4.8. If you have to build it yourself,
you can use [this](/contrib/install_db4.sh) script to install it
like so:

```shell
./contrib/install_db4.sh .
```

from the root of the repository.

Also, the Homebrew package could be installed:

```shell
brew install berkeley-db4
```

## Build BGL Core

1. Clone the BGL Core source code:
    ```shell
    git clone https://github.com/BitgesellOfficial/bitgesell
    cd bitgesell
    ```

``` bash
make        # use "-j N" here for N parallel jobs
make check  # Run tests if Python 3 is available
```

    Configure and build the headless BGL Core binaries as well as the GUI (if Qt is found).

You can also create a  `.zip` containing the `.app` bundle by running the following command:

3.  It is recommended to build and run the unit tests:
    ```shell
    make check
    ```

4.  You can also create a  `.dmg` that contains the `.app` bundle (optional):
    ```shell
    make deploy
    ```

## `disable-wallet` mode
When the intention is to run only a P2P node without a wallet, BGL Core may be
compiled in `disable-wallet` mode with:
```shell
./configure --disable-wallet
```

In this case there is no dependency on [*Berkeley DB*](#berkeley-db) and [*SQLite*](#sqlite).

Mining is also possible in disable-wallet mode using the `getblocktemplate` RPC call.

## Running
BGL Core is now available at `./src/BGLd`

Before running, you may create an empty configuration file:
```shell
mkdir -p "/Users/${USER}/Library/Application Support/BGL"

touch "/Users/${USER}/Library/Application Support/BGL/BGL.conf"

chmod 600 "/Users/${USER}/Library/Application Support/BGL/BGL.conf"
```

The first time you run BGLd, it will start downloading the blockchain. This process could
take many hours, or even days on slower than average systems.

You can monitor the download process by looking at the debug.log file:
```shell
tail -f $HOME/Library/Application\ Support/BGL/debug.log
```

## Other commands:
```shell
./src/BGLd -daemon      # Starts the BGL daemon.
./src/BGL-cli --help    # Outputs a list of command-line options.
./src/BGL-cli help      # Outputs a list of RPC commands when the daemon is running.
```

## Notes
* Tested on OS X 10.14 Mojave through macOS 11 Big Sur on 64-bit Intel
processors only.
* Building with downloaded Qt binaries is not officially supported. See the notes in [#7714](https://github.com/bitcoin/bitcoin/issues/7714).
