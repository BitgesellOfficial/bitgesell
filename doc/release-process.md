# Release Process

This document outlines the process for releasing versions of the form `$MAJOR.$MINOR.$PATCH`.

We distinguish between two types of releases: *regular* and *maintenance* releases.
Regular releases are releases of a new major or minor version as well as patches of the most recent release.
Maintenance releases, on the other hand, are required for patches of older releases.

You should coordinate with the other maintainers on the release date, if possible.
This date will be part of the release entry in [CHANGELOG.md](../CHANGELOG.md) and it should match the dates of the remaining steps in the release process (including the date of the tag and the GitHub release).
It is best if the maintainers are present during the release, so they can help ensure that the process is followed correctly and, in the case of a regular release, they are aware that they should not modify the master branch between merging the PR in step 1 and the PR in step 3.

This process also assumes that there will be no minor releases for old major releases.

We aim to cut a regular release every 3-4 months, approximately twice as frequent as major Bitcoin Core releases. Every second release should be published one month before the feature freeze of the next major Bitcoin Core release, allowing sufficient time to update the library in Core.

## Sanity Checks
Perform these checks before creating a release:

* On both the master branch and the new release branch:
  - update `CLIENT_VERSION_MAJOR` in [`configure.ac`](../configure.ac)
* On the new release branch in [`configure.ac`](../configure.ac)(see [this commit](https://github.com/bitcoin/bitcoin/commit/742f7dd)):
  - set `CLIENT_VERSION_MINOR` to `0`
  - set `CLIENT_VERSION_BUILD` to `0`
  - set `CLIENT_VERSION_IS_RELEASE` to `true`

#### Before branch-off

* Update hardcoded [seeds](/contrib/seeds/README.md), see [this pull request](https://github.com/bitcoin/bitcoin/pull/7415) for an example.
* Update the following variables in [`src/kernel/chainparams.cpp`](/src/kernel/chainparams.cpp) for mainnet, testnet, and signet:
  - `m_assumed_blockchain_size` and `m_assumed_chain_state_size` with the current size plus some overhead (see
    [this](#how-to-calculate-assumed-blockchain-and-chain-state-size) for information on how to calculate them).
  - The following updates should be reviewed with `reindex-chainstate` and `assumevalid=0` to catch any defect
    that causes rejection of blocks in the past history.
  - `chainTxData` with statistics about the transaction count and rate. Use the output of the `getchaintxstats` RPC with an
    `nBlocks` of 4096 (28 days) and a `bestblockhash` of RPC `getbestblockhash`; see
    [this pull request](https://github.com/bitcoin/bitcoin/pull/20263) for an example. Reviewers can verify the results by running
    `getchaintxstats <window_block_count> <window_final_block_hash>` with the `window_block_count` and `window_final_block_hash` from your output.
  - `defaultAssumeValid` with the output of RPC `getblockhash` using the `height` of `window_final_block_height` above
    (and update the block height comment with that height), taking into account the following:
    - On mainnet, the selected value must not be orphaned, so it may be useful to set the height two blocks back from the tip.
    - Testnet should be set with a height some tens of thousands back from the tip, due to reorgs there.
  - `nMinimumChainWork` with the "chainwork" value of RPC `getblockheader` using the same height as that selected for the previous step.
- Clear the release notes and move them to the wiki (see "Write the release notes" below).
- Translations on Transifex:
    - Pull translations from Transifex into the master branch.
    - Create [a new resource](https://www.transifex.com/bitcoin/bitcoin/content/) named after the major version with the slug `qt-translation-<RRR>x`, where `RRR` is the major branch number padded with zeros. Use `src/qt/locale/bitcoin_en.xlf` to create it.
    - In the project workflow settings, ensure that [Translation Memory Fill-up](https://help.transifex.com/en/articles/6224817-setting-up-translation-memory-fill-up) is enabled and that [Translation Memory Context Matching](https://help.transifex.com/en/articles/6224753-translation-memory-with-context) is disabled.
    - Update the Transifex slug in [`.tx/config`](/.tx/config) to the slug of the resource created in the first step. This identifies which resource the translations will be synchronized from.
    - Make an announcement that translators can start translating for the new version. You can use one of the [previous announcements](https://www.transifex.com/bitcoin/communication/) as a template.
    - Change the auto-update URL for the resource to `master`, e.g. `https://raw.githubusercontent.com/bitcoin/bitcoin/master/src/qt/locale/bitcoin_en.xlf`. (Do this only after the previous steps, to prevent an auto-update from interfering.)

#### After branch-off (on the major release branch)

- Update the versions.
- Create the draft, named "*version* Release Notes Draft", as a [collaborative wiki](https://github.com/bitcoin-core/bitcoin-devwiki/wiki/_new).
- Clear the release notes: `cp doc/release-notes-empty-template.md doc/release-notes.md`
- Create a pinned meta-issue for testing the release candidate (see [this issue](https://github.com/bitcoin/bitcoin/issues/17079) for an example) and provide a link to it in the release announcements where useful.
- Translations on Transifex
    - Change the auto-update URL for the new major version's resource away from `master` and to the branch, e.g. `https://raw.githubusercontent.com/bitcoin/bitcoin/<branch>/src/qt/locale/bitcoin_en.xlf`. Do not forget this or it will keep tracking the translations on master instead, drifting away from the specific major release.
- Prune inputs from the qa-assets repo (See [pruning
  inputs](https://github.com/bitcoin-core/qa-assets#pruning-inputs)).

#### Before final release

- Merge the release notes from [the wiki](https://github.com/bitcoin-core/bitcoin-devwiki/wiki/) into the branch.
- Ensure the "Needs release note" label is removed from all relevant pull requests and issues.

#### Tagging a release (candidate)

To tag the version (or release candidate) in git, use the `make-tag.py` script from [bitcoin-maintainer-tools](https://github.com/bitcoin-core/bitcoin-maintainer-tools). From the root of the repository run:

    ../bitcoin-maintainer-tools/make-tag.py v(new version, e.g. 23.0)

This will perform a few last-minute consistency checks in the build system files, and if they pass, create a signed tag.

## Building

### First time / New builders

Install Guix using one of the installation methods detailed in
[contrib/guix/INSTALL.md](/contrib/guix/INSTALL.md).

Check out the source code in the following directory hierarchy.

    cd /path/to/your/toplevel/build
    git clone https://github.com/bitcoin-core/guix.sigs.git
    git clone https://github.com/bitcoin-core/bitcoin-detached-sigs.git
    git clone https://github.com/bitcoin/bitcoin.git

### Write the release notes

Open a draft of the release notes for collaborative editing at https://github.com/bitcoin-core/bitcoin-devwiki/wiki.

For the period during which the notes are being edited on the wiki, the version on the branch should be wiped and replaced with a link to the wiki which should be used for all announcements until `-final`.

Generate list of authors:

    git log --format='- %aN' v(current version, e.g. 24.0)..v(new version, e.g. 24.1) | sort -fiu

### Setup and perform Guix builds

Checkout the Bitcoin Core version you'd like to build:

```sh
pushd ./bitcoin
SIGNER='(your builder key, ie bluematt, sipa, etc)'
VERSION='(new version without v-prefix, e.g. 24.0)'
git fetch origin "v${VERSION}"
git checkout "v${VERSION}"
popd
```
2. Check installation with autotools:
```shell
dir=$(mktemp -d)
./autogen.sh && ./configure --prefix=$dir && make clean && make install && ls -l $dir/include $dir/lib
gcc -o ecdsa examples/ecdsa.c $(PKG_CONFIG_PATH=$dir/lib/pkgconfig pkg-config --cflags --libs libsecp256k1) -Wl,-rpath,"$dir/lib" && ./ecdsa
```
3. Check installation with CMake:
```shell
dir=$(mktemp -d)
build=$(mktemp -d)
cmake -B $build -DCMAKE_INSTALL_PREFIX=$dir && cmake --build $build --target install && ls -l $dir/include $dir/lib*
gcc -o ecdsa examples/ecdsa.c -I $dir/include -L $dir/lib*/ -l secp256k1 -Wl,-rpath,"$dir/lib",-rpath,"$dir/lib64" && ./ecdsa
```

## Regular release

1. Open a PR to the master branch with a commit (using message `"release: prepare for $MAJOR.$MINOR.$PATCH"`, for example) that
   * finalizes the release notes in [CHANGELOG.md](../CHANGELOG.md) by
       * adding a section for the release (make sure that the version number is a link to a diff between the previous and new version),
       * removing the `[Unreleased]` section header, and
       * including an entry for `### ABI Compatibility` if it doesn't exist that mentions the library soname of the release,
   * sets `_PKG_VERSION_IS_RELEASE` to `true` in `configure.ac`, and
   * if this is not a patch release
       * updates `_PKG_VERSION_*` and `_LIB_VERSION_*`  in `configure.ac` and
       * updates `project(libsecp256k1 VERSION ...)` and `${PROJECT_NAME}_LIB_VERSION_*` in `CMakeLists.txt`.
2. After the PR is merged, tag the commit and push it:
   ```
   RELEASE_COMMIT=<merge commit of step 1>
   git tag -s v$MAJOR.$MINOR.$PATCH -m "libsecp256k1 $MAJOR.$MINOR.$PATCH" $RELEASE_COMMIT
   git push git@github.com:bitcoin-core/secp256k1.git v$MAJOR.$MINOR.$PATCH
   ```
3. Open a PR to the master branch with a commit (using message `"release cleanup: bump version after $MAJOR.$MINOR.$PATCH"`, for example) that
   * sets `_PKG_VERSION_IS_RELEASE` to `false` and increments `_PKG_VERSION_PATCH` and `_LIB_VERSION_REVISION` in `configure.ac`,
   * increments the `$PATCH` component of `project(libsecp256k1 VERSION ...)` and `${PROJECT_NAME}_LIB_VERSION_REVISION` in `CMakeLists.txt`, and
   * adds an `[Unreleased]` section header to the [CHANGELOG.md](../CHANGELOG.md).

   If other maintainers are not present to approve the PR, it can be merged without ACKs.
4. Create a new GitHub release with a link to the corresponding entry in [CHANGELOG.md](../CHANGELOG.md).

## Maintenance release

Note that bugfixes only need to be backported to releases for which no compatible release without the bug exists.

1. If there's no maintenance branch `$MAJOR.$MINOR`, create one:
   ```
   git checkout -b $MAJOR.$MINOR v$MAJOR.$MINOR.$((PATCH - 1))
   git push git@github.com:bitcoin-core/secp256k1.git $MAJOR.$MINOR
   ```
2. Open a pull request to the `$MAJOR.$MINOR` branch that
   * includes the bugfixes,
   * finalizes the release notes similar to a regular release,
   * increments `_PKG_VERSION_PATCH` and `_LIB_VERSION_REVISION` in `configure.ac`
     and the `$PATCH` component of `project(libsecp256k1 VERSION ...)` and `${PROJECT_NAME}_LIB_VERSION_REVISION` in `CMakeLists.txt`
     (with commit message `"release: bump versions for $MAJOR.$MINOR.$PATCH"`, for example).
3. After the PRs are merged, update the release branch and tag the commit:
   ```
   git checkout $MAJOR.$MINOR && git pull
   git tag -s v$MAJOR.$MINOR.$PATCH -m "libsecp256k1 $MAJOR.$MINOR.$PATCH"
   ```
4. Push tag:
   ```
   git push git@github.com:bitcoin-core/secp256k1.git v$MAJOR.$MINOR.$PATCH
   ```
5. Create a new GitHub release with a link to the corresponding entry in [CHANGELOG.md](../CHANGELOG.md).
6. Open PR to the master branch that includes a commit (with commit message `"release notes: add $MAJOR.$MINOR.$PATCH"`, for example) that adds release notes to [CHANGELOG.md](../CHANGELOG.md).
