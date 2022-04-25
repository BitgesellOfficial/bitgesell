#!/usr/bin/env bash
#
# Copyright (c) 2018-2021 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

export LC_ALL=C

GIT_HEAD=$(git rev-parse HEAD)
if [ -n "$CIRRUS_PR" ]; then
  COMMIT_RANGE="${CIRRUS_BASE_SHA}..$GIT_HEAD"
  test/lint/commit-script-check.sh "$COMMIT_RANGE"
fi

test/lint/git-subtree-check.sh src/crypto/ctaes
test/lint/git-subtree-check.sh src/secp256k1
test/lint/git-subtree-check.sh src/univalue
test/lint/git-subtree-check.sh src/leveldb
test/lint/git-subtree-check.sh src/crc32c
test/lint/check-doc.py
test/lint/lint-all.py

if [ "$CIRRUS_REPO_FULL_NAME" = "BGL/BGL" ] && [ "$CIRRUS_PR" = "" ] ; then
    # Sanity check only the last few commits to get notified of missing sigs,
    # missing keys, or expired keys. Usually there is only one new merge commit
    # per push on the master branch and a few commits on release branches, so
    # sanity checking only a few (10) commits seems sufficient and cheap.
    git log HEAD~10 -1 --format='%H' > ./contrib/verify-commits/trusted-sha512-root-commit
    git log HEAD~10 -1 --format='%H' > ./contrib/verify-commits/trusted-git-root
    mapfile -t KEYS < contrib/verify-commits/trusted-keys
    ${CI_RETRY_EXE} gpg --keyserver hkps://keys.openpgp.org --recv-keys "${KEYS[@]}" &&
    ./contrib/verify-commits/verify-commits.py;
fi

if [ -n "$COMMIT_RANGE" ]; then
  echo
  git log --no-merges --oneline "$COMMIT_RANGE"
fi
