# Bitgesell Core Windows Installer Build

This directory contains scripts to build a Windows installer (.exe) for Bitgesell Core, using the NSIS (Nullsoft Scriptable Install System) installer system.

The resulting installer is a 64-bit executable compatible with Windows 7 x64 and newer.

## Prerequisites

On a Linux (Debian/Ubuntu) build host:

```bash
# NSIS (for building the installer)
sudo apt install nsis

# MinGW cross-compilation toolchain
sudo apt install g++-mingw-w64-x86-64

# Bitgesell Core depends prerequisites (see depends/README.md)
sudo apt install build-essential libtool autotools-dev automake pkg-config bsdmainutils python3
```

## Building

### Quick build

```bash
# From the project root:
./contrib/installers/windows/build-win-installer.sh
```

This will:

1. Cross-compile Bitgesell Core for `x86_64-w64-mingw32` using the depends system
2. Strip debugging symbols from the built binaries
3. Run `makensis` to produce the installer `.exe`

### Custom version

```bash
./contrib/installers/windows/build-win-installer.sh -v 0.1.14.0
```

### Parallel jobs

```bash
./contrib/installers/windows/build-win-installer.sh -j8
```

### Clean rebuild

```bash
./contrib/installers/windows/build-win-installer.sh -c
```

## Output

The installer is written to `build/installer/bitgesell-<version>-win64-setup.exe`.

## CI / AppVeyor Integration

To build on AppVeyor (as described in issue #23):

1. Use the `windows-2022` or `vs2019-win64` image
2. Install NSIS: `choco install nsis`
3. Cross-compile using the `build_msvc/` solution or depends with MSYS2
4. Run `makensis` with the `bitgesell.nsi` script

A sample AppVeyor configuration is available at `.appveyor.yml`.

## Files

| File | Purpose |
|------|---------|
| `bitgesell.nsi` | NSIS installer script (parameterized via `-D` flags) |
| `build-win-installer.sh` | Cross-compilation + installer build script |
| `README.md` | This file |
