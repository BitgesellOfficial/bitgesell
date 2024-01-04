# Release Process

This document outlines the process for releasing versions of the form `$MAJOR.$MINOR.$PATCH`.

We distinguish between two types of releases: *regular* and *maintenance* releases.
Regular releases are releases of a new major or minor version as well as patches of the most recent release.
Maintenance releases, on the other hand, are required for patches of older releases.

You should coordinate with the other maintainers on the release date, if possible.
This date will be part of the release entry in [CHANGELOG.md](../CHANGELOG.md) and it should match the dates of the remaining steps in the release process (including the date of the tag and the GitHub release).
It is best if the maintainers are present during the release, so they can help ensure that the process is followed correctly and, in the case of a regular release, they are aware that they should not modify the master branch between merging the PR in step 1 and the PR in step 3.

This process also assumes that there will be no minor releases for old major releases.

* Update [bips.md](bips.md) to account for changes since the last release.
* Update version in `configure.ac` (don't forget to set `CLIENT_VERSION_RC` to `0`).
* Update manpages (see previous section)
* Write release notes (see "Write the release notes" below).

## Sanity Checks
Perform these checks before creating a release:

* On both the master branch and the new release branch:
  - update `CLIENT_VERSION_MAJOR` in [`configure.ac`](../configure.ac)
* On the new release branch in [`configure.ac`](../configure.ac)(see [this commit](https://github.com/bitcoin/bitcoin/commit/742f7dd)):
  - set `CLIENT_VERSION_MINOR` to `0`
  - set `CLIENT_VERSION_BUILD` to `0`
  - set `CLIENT_VERSION_IS_RELEASE` to `true`

#### Before branch-off

* Update hardcoded [seeds](/contrib/seeds/README.md), see [this pull request](https://github.com/bitcoin/bitcoin/pull/27488) for an example.
* Update the following variables in [`src/kernel/chainparams.cpp`](/src/kernel/chainparams.cpp) for mainnet, testnet, and signet:
  - `m_assumed_blockchain_size` and `m_assumed_chain_state_size` with the current size plus some overhead (see
    [this](#how-to-calculate-assumed-blockchain-and-chain-state-size) for information on how to calculate them).
  - The following updates should be reviewed with `reindex-chainstate` and `assumevalid=0` to catch any defect
    that causes rejection of blocks in the past history.
  - `chainTxData` with statistics about the transaction count and rate. Use the output of the `getchaintxstats` RPC with an
    `nBlocks` of 4096 (28 days) and a `bestblockhash` of RPC `getbestblockhash`; see
    [this pull request](https://github.com/bitcoin/bitcoin/pull/28591) for an example. Reviewers can verify the results by running
    `getchaintxstats <window_block_count> <window_final_block_hash>` with the `window_block_count` and `window_final_block_hash` from your output.
  - `defaultAssumeValid` with the output of RPC `getblockhash` using the `height` of `window_final_block_height` above
    (and update the block height comment with that height), taking into account the following:
    - On mainnet, the selected value must not be orphaned, so it may be useful to set the height two blocks back from the tip.
    - Testnet should be set with a height some tens of thousands back from the tip, due to reorgs there.
  - `nMinimumChainWork` with the "chainwork" value of RPC `getblockheader` using the same height as that selected for the previous step.
* Consider updating the headers synchronization tuning parameters to account for the chainparams updates.
  The optimal values change very slowly, so this isn't strictly necessary every release, but doing so doesn't hurt.
  - Update configuration variables in [`contrib/devtools/headerssync-params.py`](/contrib/devtools/headerssync-params.py):
    - Set `TIME` to the software's expected supported lifetime -- after this time, its ability to defend against a high bandwidth timewarp attacker will begin to degrade.
    - Set `MINCHAINWORK_HEADERS` to the height used for the `nMinimumChainWork` calculation above.
    - Check that the other variables still look reasonable.
  - Run the script. It works fine in CPython, but PyPy is much faster (seconds instead of minutes): `pypy3 contrib/devtools/headerssync-params.py`.
  - Paste the output defining `HEADER_COMMITMENT_PERIOD` and `REDOWNLOAD_BUFFER_SIZE` into the top of [`src/headerssync.cpp`](/src/headerssync.cpp).
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
- Create a pinned meta-issue for testing the release candidate (see [this issue](https://github.com/bitcoin/bitcoin/issues/27621) for an example) and provide a link to it in the release announcements where useful.
- Translations on Transifex
    - Change the auto-update URL for the new major version's resource away from `master` and to the branch, e.g. `https://raw.githubusercontent.com/bitcoin/bitcoin/<branch>/src/qt/locale/bitcoin_en.xlf`. Do not forget this or it will keep tracking the translations on master instead, drifting away from the specific major release.
- Prune inputs from the qa-assets repo (See [pruning
  inputs](https://github.com/bitcoin-core/qa-assets#pruning-inputs)).

#### Before final release

- Merge the release notes from [the wiki](https://github.com/bitcoin-core/bitcoin-devwiki/wiki/) into the branch.
- Ensure the "Needs release note" label is removed from all relevant pull
  requests and issues:
  https://github.com/bitcoin/bitcoin/issues?q=label%3A%22Needs+release+note%22

#### Tagging a release (candidate)

To tag the version (or release candidate) in git, use the `make-tag.py` script from [bitcoin-maintainer-tools](https://github.com/bitcoin-core/bitcoin-maintainer-tools). From the root of the repository run:

    ../bitcoin-maintainer-tools/make-tag.py v(new version, e.g. 25.0)

This will perform a few last-minute consistency checks in the build system files, and if they pass, create a signed tag.

## Building

### First time / New builders

Install Guix using one of the installation methods detailed in
[contrib/guix/INSTALL.md](/contrib/guix/INSTALL.md).

Check out the source code in the following directory hierarchy.

    cd /path/to/your/toplevel/build
    git clone https://github.com/BitgesellOfficial/bitgesell.git

### Write the release notes

Open a draft of the release notes for collaborative editing at https://github.com/bitcoin-core/bitcoin-devwiki/wiki.

For the period during which the notes are being edited on the wiki, the version on the branch should be wiped and replaced with a link to the wiki which should be used for all announcements until `-final`.

Generate list of authors:

    git log --format='- %aN' v(current version, e.g. 25.0)..v(new version, e.g. 25.1) | grep -v 'merge-script' | sort -fiu

### Setup and perform Guix builds

Checkout the Bitcoin Core version you'd like to build:

```sh
pushd ./bitcoin
SIGNER='(your builder key, ie bluematt, sipa, etc)'
VERSION='(new version without v-prefix, e.g. 25.0)'
git fetch origin "v${VERSION}"
git checkout "v${VERSION}"
popd
```
<<<<<<< HEAD

Ensure your guix.sigs are up-to-date if you wish to `guix-verify` your builds
against other `guix-attest` signatures.

```sh
git -C ./guix.sigs pull
```

### Create the macOS SDK tarball (first time, or when SDK version changes)

Create the macOS SDK tarball, see the [macdeploy
instructions](/contrib/macdeploy/README.md#deterministic-macos-app-notes) for
details.

### Build and attest to build outputs

Follow the relevant Guix README.md sections:
- [Building](/contrib/guix/README.md#building)
- [Attesting to build outputs](/contrib/guix/README.md#attesting-to-build-outputs)

### Verify other builders' signatures to your own (optional)

- [Verifying build output attestations](/contrib/guix/README.md#verifying-build-output-attestations)

### Commit your non codesigned signature to guix.sigs

```sh
pushd ./guix.sigs
git add "${VERSION}/${SIGNER}"/noncodesigned.SHA256SUMS{,.asc}
git commit -m "Add attestations by ${SIGNER} for ${VERSION} non-codesigned"
popd
=======
2. Check installation with autotools:
```shell
dir=$(mktemp -d)
./autogen.sh && ./configure --prefix=$dir && make clean && make install && ls -RlAh $dir
gcc -o ecdsa examples/ecdsa.c $(PKG_CONFIG_PATH=$dir/lib/pkgconfig pkg-config --cflags --libs libsecp256k1) -Wl,-rpath,"$dir/lib" && ./ecdsa
```
3. Check installation with CMake:
```shell
dir=$(mktemp -d)
build=$(mktemp -d)
cmake -B $build -DCMAKE_INSTALL_PREFIX=$dir && cmake --build $build --target install && ls -RlAh $dir
gcc -o ecdsa examples/ecdsa.c -I $dir/include -L $dir/lib*/ -l secp256k1 -Wl,-rpath,"$dir/lib",-rpath,"$dir/lib64" && ./ecdsa
>>>>>>> 29fde0223a... Squashed 'src/secp256k1/' changes from 199d27cea3..efe85c70a2
```
4. Use the [`check-abi.sh`](/tools/check-abi.sh) tool to ensure there are no unexpected ABI incompatibilities and that the version number and release notes accurately reflect all potential ABI changes. To run this tool, the `abi-dumper` and `abi-compliance-checker` packages are required.

```shell
tools/check-abi.sh
```

<<<<<<< HEAD
Then open a Pull Request to the [guix.sigs repository](https://github.com/bitcoin-core/guix.sigs).

## Codesigning

### macOS codesigner only: Create detached macOS signatures (assuming [signapple](https://github.com/achow101/signapple/) is installed and up to date with master branch)

    tar xf bitcoin-osx-unsigned.tar.gz
    ./detached-sig-create.sh /path/to/codesign.p12
    Enter the keychain password and authorize the signature
    signature-osx.tar.gz will be created

### Windows codesigner only: Create detached Windows signatures

    tar xf bitcoin-win-unsigned.tar.gz
    ./detached-sig-create.sh -key /path/to/codesign.key
    Enter the passphrase for the key when prompted
    signature-win.tar.gz will be created

### Windows and macOS codesigners only: test code signatures
It is advised to test that the code signature attaches properly prior to tagging by performing the `guix-codesign` step.
However if this is done, once the release has been tagged in the bitcoin-detached-sigs repo, the `guix-codesign` step must be performed again in order for the guix attestation to be valid when compared against the attestations of non-codesigner builds.

### Windows and macOS codesigners only: Commit the detached codesign payloads

```sh
pushd ./bitcoin-detached-sigs
# checkout the appropriate branch for this release series
rm -rf ./*
tar xf signature-osx.tar.gz
tar xf signature-win.tar.gz
git add -A
git commit -m "point to ${VERSION}"
git tag -s "v${VERSION}" HEAD
git push the current branch and new tag
popd
```

### Non-codesigners: wait for Windows and macOS detached signatures

- Once the Windows and macOS builds each have 3 matching signatures, they will be signed with their respective release keys.
- Detached signatures will then be committed to the [bitcoin-detached-sigs](https://github.com/bitcoin-core/bitcoin-detached-sigs) repository, which can be combined with the unsigned apps to create signed binaries.

### Create the codesigned build outputs

- [Codesigning build outputs](/contrib/guix/README.md#codesigning-build-outputs)

### Verify other builders' signatures to your own (optional)

- [Verifying build output attestations](/contrib/guix/README.md#verifying-build-output-attestations)

### Commit your codesigned signature to guix.sigs (for the signed macOS/Windows binaries)

```sh
pushd ./guix.sigs
git add "${VERSION}/${SIGNER}"/all.SHA256SUMS{,.asc}
git commit -m "Add attestations by ${SIGNER} for ${VERSION} codesigned"
popd
```

Then open a Pull Request to the [guix.sigs repository](https://github.com/bitcoin-core/guix.sigs).

## After 3 or more people have guix-built and their results match

Combine the `all.SHA256SUMS.asc` file from all signers into `SHA256SUMS.asc`:

```bash
cat "$VERSION"/*/all.SHA256SUMS.asc > SHA256SUMS.asc
```


- Upload to the bitcoincore.org server (`/var/www/bin/bitcoin-core-${VERSION}/`):
    1. The contents of each `./bitcoin/guix-build-${VERSION}/output/${HOST}/` directory, except for
       `*-debug*` files.

       Guix will output all of the results into host subdirectories, but the SHA256SUMS
       file does not include these subdirectories. In order for downloads via torrent
       to verify without directory structure modification, all of the uploaded files
       need to be in the same directory as the SHA256SUMS file.

       The `*-debug*` files generated by the guix build contain debug symbols
       for troubleshooting by developers. It is assumed that anyone that is
       interested in debugging can run guix to generate the files for
       themselves. To avoid end-user confusion about which file to pick, as well
       as save storage space *do not upload these to the bitcoincore.org server,
       nor put them in the torrent*.

       ```sh
       find guix-build-${VERSION}/output/ -maxdepth 2 -type f -not -name "SHA256SUMS.part" -and -not -name "*debug*" -exec scp {} user@bitcoincore.org:/var/www/bin/bitcoin-core-${VERSION} \;
       ```

    2. The `SHA256SUMS` file

    3. The `SHA256SUMS.asc` combined signature file you just created

- Create a torrent of the `/var/www/bin/bitcoin-core-${VERSION}` directory such
  that at the top level there is only one file: the `bitcoin-core-${VERSION}`
  directory containing everything else. Name the torrent
  `bitcoin-${VERSION}.torrent` (note that there is no `-core-` in this name).

  Optionally help seed this torrent. To get the `magnet:` URI use:

  ```sh
  transmission-show -m <torrent file>
  ```

  Insert the magnet URI into the announcement sent to mailing lists. This permits
  people without access to `bitcoincore.org` to download the binary distribution.
  Also put it into the `optional_magnetlink:` slot in the YAML file for
  bitcoincore.org.

- Update other repositories and websites for new version

  - bitcoincore.org blog post

  - bitcoincore.org maintained versions update:
    [table](https://github.com/bitcoin-core/bitcoincore.org/commits/master/_includes/posts/maintenance-table.md)

  - Delete post-EOL [release branches](https://github.com/bitcoin/bitcoin/branches/all) and create a tag `v${branch_name}-final`.

  - Delete ["Needs backport" labels](https://github.com/bitcoin/bitcoin/labels?q=backport) for non-existing branches.

  - bitcoincore.org RPC documentation update

      - See https://github.com/bitcoin-core/bitcoincore.org/blob/master/contrib/doc-gen/

  - Update packaging repo

      - Push the flatpak to flathub, e.g. https://github.com/flathub/org.bitcoincore.bitcoin-qt/pull/2

      - Push the snap, see https://github.com/bitcoin-core/packaging/blob/main/snap/local/build.md

  - This repo

      - Archive the release notes for the new version to `doc/release-notes/` (branch `master` and branch of the release)

      - Create a [new GitHub release](https://github.com/BitgesellOfficial/bitgesell/releases/new) with a link to the archived release notes

- Announce the release:

  - bitcoin-dev and bitcoin-core-dev mailing list

  - BGL Core announcements list https://bitgesell.ca/en/list/announcements/join/

  - Bitcoin Core Twitter https://twitter.com/bitcoincoreorg

  - Celebrate

### Additional information

#### <a name="how-to-calculate-assumed-blockchain-and-chain-state-size"></a>How to calculate `m_assumed_blockchain_size` and `m_assumed_chain_state_size`

Both variables are used as a guideline for how much space the user needs on their drive in total, not just strictly for the blockchain.
Note that all values should be taken from a **fully synced** node and have an overhead of 5-10% added on top of its base value.

To calculate `m_assumed_blockchain_size`, take the size in GiB of these directories:
- For `mainnet` -> the data directory, excluding the `/testnet3`, `/signet`, and `/regtest` directories and any overly large files, e.g. a huge `debug.log`
- For `testnet` -> `/testnet3`
- For `signet` -> `/signet`

To calculate `m_assumed_chain_state_size`, take the size in GiB of these directories:
- For `mainnet` -> `/chainstate`
- For `testnet` -> `/testnet3/chainstate`
- For `signet` -> `/signet/chainstate`

Notes:
- When taking the size for `m_assumed_blockchain_size`, there's no need to exclude the `/chainstate` directory since it's a guideline value and an overhead will be added anyway.
- The expected overhead for growth may change over time. Consider whether the percentage needs to be changed in response; if so, update it here in this section.
=======
## Regular release

1. Open a PR to the master branch with a commit (using message `"release: prepare for $MAJOR.$MINOR.$PATCH"`, for example) that
   * finalizes the release notes in [CHANGELOG.md](../CHANGELOG.md) by
       * adding a section for the release (make sure that the version number is a link to a diff between the previous and new version),
       * removing the `[Unreleased]` section header, and
       * including an entry for `### ABI Compatibility` if it doesn't exist,
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
>>>>>>> 29fde0223a... Squashed 'src/secp256k1/' changes from 199d27cea3..efe85c70a2
