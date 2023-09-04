#!/usr/bin/env bash
#
# Copyright (c) 2018-2022 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

export LC_ALL=C.UTF-8

set -ex

if [ "$CI_OS_NAME" == "macos" ]; then
  top -l 1 -s 0 | awk ' /PhysMem/ {print}'
  echo "Number of CPUs: $(sysctl -n hw.logicalcpu)"
else
  CI_EXEC free -m -h
  CI_EXEC echo "Number of CPUs \(nproc\):" \$\(nproc\)
  CI_EXEC echo "$(lscpu | grep Endian)"
fi
CI_EXEC echo "Free disk space:"
CI_EXEC df -h

if [ "$RUN_FUZZ_TESTS" = "true" ]; then
  export DIR_FUZZ_IN=${DIR_QA_ASSETS}/fuzz_seed_corpus/
  if [ ! -d "$DIR_FUZZ_IN" ]; then
    CI_EXEC git clone --depth=1 https://github.com/bitcoin-core/qa-assets "${DIR_QA_ASSETS}"
  fi
elif [ "$RUN_UNIT_TESTS" = "true" ] || [ "$RUN_UNIT_TESTS_SEQUENTIAL" = "true" ]; then
  export DIR_UNIT_TEST_DATA=${DIR_QA_ASSETS}/unit_test_data/
  if [ ! -d "$DIR_UNIT_TEST_DATA" ]; then
    CI_EXEC mkdir -p "$DIR_UNIT_TEST_DATA"
    CI_EXEC curl --location --fail https://github.com/bitcoin-core/qa-assets/raw/main/unit_test_data/script_assets_test.json -o "${DIR_UNIT_TEST_DATA}/script_assets_test.json"
  fi
fi

CI_EXEC mkdir -p "${BASE_SCRATCH_DIR}/sanitizer-output/"

if [ "$USE_BUSY_BOX" = "true" ]; then
  echo "Setup to use BusyBox utils"
  # tar excluded for now because it requires passing in the exact archive type in ./depends (fixed in later BusyBox version)
  # ar excluded for now because it does not recognize the -q option in ./depends (unknown if fixed)
  # shellcheck disable=SC1010
  CI_EXEC for util in \$\(busybox --list \| grep -v "^ar$" \| grep -v "^tar$" \)\; do ln -s \$\(command -v busybox\) "${BINS_SCRATCH_DIR}/\$util"\; done
  # Print BusyBox version
  CI_EXEC patch --help
fi

# Make sure default datadir does not exist and is never read by creating a dummy file
if [ "$CI_OS_NAME" == "macos" ]; then
  echo > "${HOME}/Library/Application Support/Bitcoin"
else
  CI_EXEC echo \> \$HOME/.bitcoin
fi

if [ -z "$NO_DEPENDS" ]; then
  if [[ $CI_IMAGE_NAME_TAG == *centos* ]]; then
    # CentOS has problems building the depends if the config shell is not explicitly set
    # (i.e. for libevent a Makefile with an empty SHELL variable is generated, leading to
    #  an error as the first command is executed)
    SHELL_OPTS="LC_ALL=en_US.UTF-8 CONFIG_SHELL=/bin/dash"
  else
    SHELL_OPTS="CONFIG_SHELL="
  fi
  CI_EXEC "$SHELL_OPTS" make "$MAKEJOBS" -C depends HOST="$HOST" "$DEP_OPTS" LOG=1
fi
if [ "$DOWNLOAD_PREVIOUS_RELEASES" = "true" ]; then
  CI_EXEC test/get_previous_releases.py -b -t "$PREVIOUS_RELEASES_DIR"
fi

BITCOIN_CONFIG_ALL="--enable-suppress-external-warnings --disable-dependency-tracking"
if [ -z "$NO_DEPENDS" ]; then
  BITCOIN_CONFIG_ALL="${BITCOIN_CONFIG_ALL} CONFIG_SITE=$DEPENDS_DIR/$HOST/share/config.site"
fi
if [ -z "$NO_WERROR" ]; then
  BITCOIN_CONFIG_ALL="${BITCOIN_CONFIG_ALL} --enable-werror"
fi

CI_EXEC "ccache --zero-stats --max-size=$CCACHE_SIZE"
PRINT_CCACHE_STATISTICS="ccache --version | head -n 1 && ccache --show-stats"

if [ -n "$ANDROID_TOOLS_URL" ]; then
  CI_EXEC make distclean || true
  CI_EXEC ./autogen.sh
  CI_EXEC ./configure "$BITCOIN_CONFIG_ALL" "$BITCOIN_CONFIG" || ( (CI_EXEC cat config.log) && false)
  CI_EXEC "make $MAKEJOBS && cd src/qt && ANDROID_HOME=${ANDROID_HOME} ANDROID_NDK_HOME=${ANDROID_NDK_HOME} make apk"
  CI_EXEC "${PRINT_CCACHE_STATISTICS}"
  exit 0
fi

BITCOIN_CONFIG_ALL="${BITCOIN_CONFIG_ALL} --enable-external-signer --prefix=$BASE_OUTDIR"

if [ -n "$CONFIG_SHELL" ]; then
  CI_EXEC "$CONFIG_SHELL" -c "./autogen.sh"
else
  CI_EXEC ./autogen.sh
fi

CI_EXEC mkdir -p "${BASE_BUILD_DIR}"
export P_CI_DIR="${BASE_BUILD_DIR}"

CI_EXEC "${BASE_ROOT_DIR}/configure" --cache-file=config.cache "$BITCOIN_CONFIG_ALL" "$BITCOIN_CONFIG" || ( (CI_EXEC cat config.log) && false)

CI_EXEC make distdir VERSION="$HOST"

export P_CI_DIR="${BASE_BUILD_DIR}/bitcoin-$HOST"

CI_EXEC ./configure --cache-file=../config.cache "$BITCOIN_CONFIG_ALL" "$BITCOIN_CONFIG" || ( (CI_EXEC cat config.log) && false)

set -o errtrace
trap 'CI_EXEC "cat ${BASE_SCRATCH_DIR}/sanitizer-output/* 2> /dev/null"' ERR

if [[ ${USE_MEMORY_SANITIZER} == "true" ]]; then
  # MemorySanitizer (MSAN) does not support tracking memory initialization done by
  # using the Linux getrandom syscall. Avoid using getrandom by undefining
  # HAVE_SYS_GETRANDOM. See https://github.com/google/sanitizers/issues/852 for
  # details.
  CI_EXEC 'grep -v HAVE_SYS_GETRANDOM src/config/bitcoin-config.h > src/config/bitcoin-config.h.tmp && mv src/config/bitcoin-config.h.tmp src/config/bitcoin-config.h'
fi

if [[ "${RUN_TIDY}" == "true" ]]; then
  MAYBE_BEAR="bear --config src/.bear-tidy-config"
  MAYBE_TOKEN="--"
fi

CI_EXEC "${MAYBE_BEAR}" "${MAYBE_TOKEN}" make "$MAKEJOBS" "$GOAL" || ( echo "Build failure. Verbose build follows." && CI_EXEC make "$GOAL" V=1 ; false )

CI_EXEC "${PRINT_CCACHE_STATISTICS}"
CI_EXEC du -sh "${DEPENDS_DIR}"/*/
CI_EXEC du -sh "${PREVIOUS_RELEASES_DIR}"

if [[ $HOST = *-mingw32 ]]; then
  # Generate all binaries, so that they can be wrapped
  make "$MAKEJOBS" -C src/secp256k1 VERBOSE=1
  make "$MAKEJOBS" -C src minisketch/test.exe VERBOSE=1
  "${BASE_ROOT_DIR}/ci/test/wrap-wine.sh"
fi

if [ -n "$QEMU_USER_CMD" ]; then
  # Generate all binaries, so that they can be wrapped
  make "$MAKEJOBS" -C src/secp256k1 VERBOSE=1
  make "$MAKEJOBS" -C src minisketch/test VERBOSE=1
  "${BASE_ROOT_DIR}/ci/test/wrap-qemu.sh"
fi

if [ -n "$USE_VALGRIND" ]; then
  "${BASE_ROOT_DIR}/ci/test/wrap-valgrind.sh"
fi

if [ "$RUN_UNIT_TESTS" = "true" ]; then
  bash -c "${TEST_RUNNER_ENV} DIR_UNIT_TEST_DATA=${DIR_UNIT_TEST_DATA} LD_LIBRARY_PATH=${DEPENDS_DIR}/${HOST}/lib make $MAKEJOBS check VERBOSE=1"
fi

if [ "$RUN_UNIT_TESTS_SEQUENTIAL" = "true" ]; then
  bash -c "${TEST_RUNNER_ENV} DIR_UNIT_TEST_DATA=${DIR_UNIT_TEST_DATA} LD_LIBRARY_PATH=${DEPENDS_DIR}/${HOST}/lib ${BASE_OUTDIR}/bin/test_bitcoin --catch_system_errors=no -l test_suite"
fi

if [ "$RUN_FUNCTIONAL_TESTS" = "true" ]; then
  bash -c "LD_LIBRARY_PATH=${DEPENDS_DIR}/${HOST}/lib ${TEST_RUNNER_ENV} test/functional/test_runner.py --ci $MAKEJOBS --tmpdirprefix ${BASE_SCRATCH_DIR}/test_runner/ --ansi --combinedlogslen=99999999 --timeout-factor=${TEST_RUNNER_TIMEOUT_FACTOR} ${TEST_RUNNER_EXTRA} --quiet --failfast"
fi

if [ "${RUN_TIDY}" = "true" ]; then
  set -eo pipefail
  cd "${BASE_BUILD_DIR}/bitcoin-$HOST/src/"
  ( run-clang-tidy-16 -quiet "${MAKEJOBS}" ) | grep -C5 "error"
  cd "${BASE_BUILD_DIR}/bitcoin-$HOST/"
  python3 "${DIR_IWYU}/include-what-you-use/iwyu_tool.py" \
           src/common/args.cpp \
           src/common/config.cpp \
           src/common/init.cpp \
           src/common/url.cpp \
           src/compat \
           src/dbwrapper.cpp \
           src/init \
           src/kernel \
           src/node/chainstate.cpp \
           src/node/chainstatemanager_args.cpp \
           src/node/mempool_args.cpp \
           src/node/minisketchwrapper.cpp \
           src/node/utxo_snapshot.cpp \
           src/node/validation_cache_args.cpp \
           src/policy/feerate.cpp \
           src/policy/packages.cpp \
           src/policy/settings.cpp \
           src/primitives/transaction.cpp \
           src/random.cpp \
           src/rpc/fees.cpp \
           src/rpc/signmessage.cpp \
           src/test/fuzz/string.cpp \
           src/test/fuzz/txorphan.cpp \
           src/test/fuzz/util \
           src/test/util/coins.cpp \
           src/uint256.cpp \
           src/util/bip32.cpp \
           src/util/bytevectorhash.cpp \
           src/util/check.cpp \
           src/util/error.cpp \
           src/util/exception.cpp \
           src/util/getuniquepath.cpp \
           src/util/hasher.cpp \
           src/util/message.cpp \
           src/util/moneystr.cpp \
           src/util/serfloat.cpp \
           src/util/spanparsing.cpp \
           src/util/strencodings.cpp \
           src/util/string.cpp \
           src/util/syserror.cpp \
           src/util/threadinterrupt.cpp \
           src/zmq \
           -p . "${MAKEJOBS}" \
           -- -Xiwyu --cxx17ns -Xiwyu --mapping_file="${BASE_BUILD_DIR}/bitcoin-$HOST/contrib/devtools/iwyu/bitcoin.core.imp" \
           2>&1 | tee /tmp/iwyu_ci.out
  cd "${BASE_ROOT_DIR}/src"
  python3 "${DIR_IWYU}/include-what-you-use/fix_includes.py" --nosafe_headers < /tmp/iwyu_ci.out
  git --no-pager diff
fi

if [ "$RUN_SECURITY_TESTS" = "true" ]; then
  make test-security-check
fi

if [ "$RUN_FUZZ_TESTS" = "true" ]; then
  bash -c "LD_LIBRARY_PATH=${DEPENDS_DIR}/${HOST}/lib test/fuzz/test_runner.py ${FUZZ_TESTS_CONFIG} $MAKEJOBS -l DEBUG ${DIR_FUZZ_IN}"
fi
