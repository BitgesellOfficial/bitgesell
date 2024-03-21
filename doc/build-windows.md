WINDOWS BUILD NOTES
====================

Below are some notes on how to build BGL Core for Windows.

The options known to work for building BGL Core on Windows are:

* On Linux, using the [Mingw-w64](https://www.mingw-w64.org/) cross compiler tool chain.
* On Windows, using [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/about) and Mingw-w64.
* On Windows, using [Microsoft Visual Studio](https://visualstudio.microsoft.com). See [README.md](/build_msvc/README.md).

Other options which may work, but which have not been extensively tested are (please contribute instructions):

* On Windows, using a POSIX compatibility layer application such as [cygwin](https://www.cygwin.com/) or [msys2](https://www.msys2.org/).

Installing Windows Subsystem for Linux
---------------------------------------

Follow the upstream installation instructions, available [here](https://learn.microsoft.com/en-us/windows/wsl/install).

Cross-compilation for Ubuntu and Windows Subsystem for Linux
===

The dependencies for cross-compile for Windows x64 + x32 on Linux are already compiled at:   */bitgesell/depends/*    folder, see codes below to now compile Windows wallets on Linux 18.04:


To compile for Windows on Linux 18.04:
------------------------------------------------------------

   - x64:
```
./autogen.sh && ./configure --prefix=`pwd`/depends/x86_64-w64-mingw32 && make -j$(nproc)
```
   - x32:
```
./autogen.sh && ./configure --prefix=`pwd`/depends/i686-w64-mingw32 && make -j$(nproc)
```


--


Or follow the steps below:
------------------------------------------------------------


The steps below can be performed on Ubuntu (including in a VM) or WSL. The depends system
will also work on other Linux distributions, however the commands for
installing the toolchain will be different.

First, install the general dependencies:

    sudo apt update
    sudo apt upgrade
    sudo apt install build-essential libtool autotools-dev automake pkg-config bsdmainutils curl git

A host toolchain (`build-essential`) is necessary because some dependency
packages need to build host utilities that are used in the build process.

See [dependencies.md](dependencies.md) for a complete overview.

If you want to build the windows installer with `make deploy` you need [NSIS](https://nsis.sourceforge.io/Main_Page):

    sudo apt install nsis

Acquire the source in the usual way:

    git clone https://github.com/Original-Tasty/bitgesell.git
    cd bitgesell

## Building for 64-bit Windows

The first step is to install the mingw-w64 cross-compilation tool chain:
  - on modern systems (Ubuntu 21.04 Hirsute Hippo or newer, Debian 11 Bullseye or newer):

```sh
sudo apt install g++-mingw-w64-x86-64-posix
```

  - on older systems:

```sh
sudo apt install g++-mingw-w64-x86-64
```

Next, set the default `mingw32 g++` compiler option to POSIX<sup>[1](#footnote1)</sup>:

```
sudo update-alternatives --config x86_64-w64-mingw32-g++
```

After running the above command, you should see output similar to that below.
Choose the option that ends with `posix`.

```
There are 2 choices for the alternative x86_64-w64-mingw32-g++ (providing /usr/bin/x86_64-w64-mingw32-g++).

  Selection    Path                                   Priority   Status
------------------------------------------------------------
  0            /usr/bin/x86_64-w64-mingw32-g++-win32   60        auto mode
* 1            /usr/bin/x86_64-w64-mingw32-g++-posix   30        manual mode
  2            /usr/bin/x86_64-w64-mingw32-g++-win32   60        manual mode

Press <enter> to keep the current choice[*], or type selection number:
```

Once the toolchain is installed the build steps are common:

Note that for WSL the BGL Core source path MUST be somewhere in the default mount file system, for
example /usr/src/BGL, AND not under /mnt/d/. If this is not the case the dependency autoconf scripts will fail.
This means you cannot use a directory that is located directly on the host Windows file system to perform the build.

Additional WSL Note: WSL support for [launching Win32 applications](https://learn.microsoft.com/en-us/archive/blogs/wsl/windows-and-ubuntu-interoperability#launching-win32-applications-from-within-wsl)
results in `Autoconf` configure scripts being able to execute Windows Portable Executable files. This can cause
unexpected behaviour during the build, such as Win32 error dialogs for missing libraries. The recommended approach
is to temporarily disable WSL support for Win32 applications.

Build using:

    PATH=$(echo "$PATH" | sed -e 's/:\/mnt.*//g') # strip out problematic Windows %PATH% imported var
    sudo bash -c "echo 0 > /proc/sys/fs/binfmt_misc/status" # Disable WSL support for Win32 applications.
    cd depends
    make HOST=x86_64-w64-mingw32
    cd ..
    ./autogen.sh
    CONFIG_SITE=$PWD/depends/x86_64-w64-mingw32/share/config.site ./configure --prefix=/
    make # use "-j N" for N parallel jobs
    sudo bash -c "echo 1 > /proc/sys/fs/binfmt_misc/status" # Enable WSL support for Win32 applications.

## Depends system

For further documentation on the depends system see [README.md](../depends/README.md) in the depends directory.

Installation
-------------

After building using the Windows subsystem it can be useful to copy the compiled
executables to a directory on the Windows drive in the same directory structure
as they appear in the release `.zip` archive. This can be done in the following
way. This will install to `c:\workspace\BGL`, for example:

    make install DESTDIR=/mnt/c/workspace/BGL

You can also create an installer using:

    make deploy

Footnotes
---------

<a name="footnote1">1</a>: Starting from Ubuntu Xenial 16.04, both the 32 and 64 bit Mingw-w64 packages install two different
compiler options to allow a choice between either posix or win32 threads. The default option is win32 threads which is the more
efficient since it will result in binary code that links directly with the Windows kernel32.lib. Unfortunately, the headers
required to support win32 threads conflict with some of the classes in the C++11 standard library, in particular std::mutex.
It's not possible to build the BGL Core code using the win32 version of the Mingw-w64 cross compilers (at least not without
modifying headers in the BGL Core source code).
