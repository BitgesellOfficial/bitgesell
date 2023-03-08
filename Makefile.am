# Copyright (c) 2013-2020 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Pattern rule to print variables, e.g. make print-top_srcdir
print-%: FORCE
	@echo '$*'='$($*)'

# AM_CFLAGS will be automatically prepended to CFLAGS by Automake when compiling some foo
# which does not have an explicit foo_CFLAGS variable set.
AM_CFLAGS = $(SECP_CFLAGS)

lib_LTLIBRARIES = libsecp256k1.la
include_HEADERS = include/secp256k1.h
include_HEADERS += include/secp256k1_preallocated.h
noinst_HEADERS =
noinst_HEADERS += src/scalar.h
noinst_HEADERS += src/scalar_4x64.h
noinst_HEADERS += src/scalar_8x32.h
noinst_HEADERS += src/scalar_low.h
noinst_HEADERS += src/scalar_impl.h
noinst_HEADERS += src/scalar_4x64_impl.h
noinst_HEADERS += src/scalar_8x32_impl.h
noinst_HEADERS += src/scalar_low_impl.h
noinst_HEADERS += src/group.h
noinst_HEADERS += src/group_impl.h
noinst_HEADERS += src/ecdsa.h
noinst_HEADERS += src/ecdsa_impl.h
noinst_HEADERS += src/eckey.h
noinst_HEADERS += src/eckey_impl.h
noinst_HEADERS += src/ecmult.h
noinst_HEADERS += src/ecmult_impl.h
noinst_HEADERS += src/ecmult_compute_table.h
noinst_HEADERS += src/ecmult_compute_table_impl.h
noinst_HEADERS += src/ecmult_const.h
noinst_HEADERS += src/ecmult_const_impl.h
noinst_HEADERS += src/ecmult_gen.h
noinst_HEADERS += src/ecmult_gen_impl.h
noinst_HEADERS += src/ecmult_gen_compute_table.h
noinst_HEADERS += src/ecmult_gen_compute_table_impl.h
noinst_HEADERS += src/field_10x26.h
noinst_HEADERS += src/field_10x26_impl.h
noinst_HEADERS += src/field_5x52.h
noinst_HEADERS += src/field_5x52_impl.h
noinst_HEADERS += src/field_5x52_int128_impl.h
noinst_HEADERS += src/field_5x52_asm_impl.h
noinst_HEADERS += src/modinv32.h
noinst_HEADERS += src/modinv32_impl.h
noinst_HEADERS += src/modinv64.h
noinst_HEADERS += src/modinv64_impl.h
noinst_HEADERS += src/precomputed_ecmult.h
noinst_HEADERS += src/precomputed_ecmult_gen.h
noinst_HEADERS += src/assumptions.h
noinst_HEADERS += src/checkmem.h
noinst_HEADERS += src/util.h
noinst_HEADERS += src/int128.h
noinst_HEADERS += src/int128_impl.h
noinst_HEADERS += src/int128_native.h
noinst_HEADERS += src/int128_native_impl.h
noinst_HEADERS += src/int128_struct.h
noinst_HEADERS += src/int128_struct_impl.h
noinst_HEADERS += src/scratch.h
noinst_HEADERS += src/scratch_impl.h
noinst_HEADERS += src/selftest.h
noinst_HEADERS += src/testrand.h
noinst_HEADERS += src/testrand_impl.h
noinst_HEADERS += src/hash.h
noinst_HEADERS += src/hash_impl.h
noinst_HEADERS += src/field.h
noinst_HEADERS += src/field_impl.h
noinst_HEADERS += src/bench.h
noinst_HEADERS += contrib/lax_der_parsing.h
noinst_HEADERS += contrib/lax_der_parsing.c
noinst_HEADERS += contrib/lax_der_privatekey_parsing.h
noinst_HEADERS += contrib/lax_der_privatekey_parsing.c
noinst_HEADERS += examples/examples_util.h

PRECOMPUTED_LIB = libsecp256k1_precomputed.la
noinst_LTLIBRARIES = $(PRECOMPUTED_LIB)
libsecp256k1_precomputed_la_SOURCES =  src/precomputed_ecmult.c src/precomputed_ecmult_gen.c
# We need `-I$(top_srcdir)/src` in VPATH builds if libsecp256k1_precomputed_la_SOURCES have been recreated in the build tree.
# This helps users and packagers who insist on recreating the precomputed files (e.g., Gentoo).
libsecp256k1_precomputed_la_CPPFLAGS = -I$(top_srcdir)/src $(SECP_CONFIG_DEFINES)

if USE_EXTERNAL_ASM
COMMON_LIB = libsecp256k1_common.la
else
COMMON_LIB =
endif
.PHONY: deploy FORCE
.INTERMEDIATE: $(COVERAGE_INFO)

export PYTHONPATH

if BUILD_BGL_LIBS
pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = libBGLconsensus.pc
endif

libsecp256k1_la_SOURCES = src/secp256k1.c
libsecp256k1_la_CPPFLAGS = $(SECP_CONFIG_DEFINES)
libsecp256k1_la_LIBADD = $(COMMON_LIB) $(PRECOMPUTED_LIB)
libsecp256k1_la_LDFLAGS = -no-undefined -version-info $(LIB_VERSION_CURRENT):$(LIB_VERSION_REVISION):$(LIB_VERSION_AGE)

noinst_PROGRAMS =
if USE_BENCHMARK
noinst_PROGRAMS += bench bench_internal bench_ecmult
bench_SOURCES = src/bench.c
bench_LDADD = libsecp256k1.la
bench_CPPFLAGS = $(SECP_CONFIG_DEFINES)
bench_internal_SOURCES = src/bench_internal.c
bench_internal_LDADD = $(COMMON_LIB) $(PRECOMPUTED_LIB)
bench_internal_CPPFLAGS = $(SECP_CONFIG_DEFINES)
bench_ecmult_SOURCES = src/bench_ecmult.c
bench_ecmult_LDADD = $(COMMON_LIB) $(PRECOMPUTED_LIB)
bench_ecmult_CPPFLAGS = $(SECP_CONFIG_DEFINES)
endif

TESTS =
if USE_TESTS
TESTS += noverify_tests
noinst_PROGRAMS += noverify_tests
noverify_tests_SOURCES = src/tests.c
noverify_tests_CPPFLAGS = $(SECP_CONFIG_DEFINES)
noverify_tests_LDADD = $(COMMON_LIB) $(PRECOMPUTED_LIB)
noverify_tests_LDFLAGS = -static
if !ENABLE_COVERAGE
TESTS += tests
noinst_PROGRAMS += tests
tests_SOURCES  = $(noverify_tests_SOURCES)
tests_CPPFLAGS = $(noverify_tests_CPPFLAGS) -DVERIFY
tests_LDADD    = $(noverify_tests_LDADD)
tests_LDFLAGS  = $(noverify_tests_LDFLAGS)
endif
endif

if USE_CTIME_TESTS
noinst_PROGRAMS += ctime_tests
ctime_tests_SOURCES = src/ctime_tests.c
ctime_tests_LDADD = libsecp256k1.la
ctime_tests_CPPFLAGS = $(SECP_CONFIG_DEFINES)
endif

if USE_EXHAUSTIVE_TESTS
noinst_PROGRAMS += exhaustive_tests
exhaustive_tests_SOURCES = src/tests_exhaustive.c
exhaustive_tests_CPPFLAGS = $(SECP_CONFIG_DEFINES)
if !ENABLE_COVERAGE
exhaustive_tests_CPPFLAGS += -DVERIFY
endif
# Note: do not include $(PRECOMPUTED_LIB) in exhaustive_tests (it uses runtime-generated tables).
exhaustive_tests_LDADD = $(COMMON_LIB)
exhaustive_tests_LDFLAGS = -static
TESTS += exhaustive_tests
endif

BIN_CHECKS=$(top_srcdir)/contrib/devtools/symbol-check.py \
           $(top_srcdir)/contrib/devtools/security-check.py \
           $(top_srcdir)/contrib/devtools/utils.py

WINDOWS_PACKAGING = $(top_srcdir)/share/pixmaps/BGL.ico \
  $(top_srcdir)/share/pixmaps/nsis-header.bmp \
  $(top_srcdir)/share/pixmaps/nsis-wizard.bmp \
  $(top_srcdir)/doc/README_windows.txt

OSX_PACKAGING = $(OSX_DEPLOY_SCRIPT) $(OSX_INSTALLER_ICONS) \
  $(top_srcdir)/contrib/macdeploy/detached-sig-create.sh

COVERAGE_INFO = $(COV_TOOL_WRAPPER) baseline.info \
  test_BGL_filtered.info total_coverage.info \
  baseline_filtered.info functional_test.info functional_test_filtered.info \
  test_BGL_coverage.info test_BGL.info fuzz.info fuzz_filtered.info fuzz_coverage.info

dist-hook:
	-$(GIT) archive --format=tar HEAD -- src/clientversion.cpp | $(AMTAR) -C $(top_distdir) -xf -

if TARGET_WINDOWS
$(BGL_WIN_INSTALLER): all-recursive
	$(MKDIR_P) $(top_builddir)/release
	STRIPPROG="$(STRIP)" $(INSTALL_STRIP_PROGRAM) $(BGLD_BIN) $(top_builddir)/release
	STRIPPROG="$(STRIP)" $(INSTALL_STRIP_PROGRAM) $(BGL_QT_BIN) $(top_builddir)/release
	STRIPPROG="$(STRIP)" $(INSTALL_STRIP_PROGRAM) $(BGL_TEST_BIN) $(top_builddir)/release
	STRIPPROG="$(STRIP)" $(INSTALL_STRIP_PROGRAM) $(BGL_CLI_BIN) $(top_builddir)/release
	STRIPPROG="$(STRIP)" $(INSTALL_STRIP_PROGRAM) $(BGL_TX_BIN) $(top_builddir)/release
	STRIPPROG="$(STRIP)" $(INSTALL_STRIP_PROGRAM) $(BGL_WALLET_BIN) $(top_builddir)/release
	STRIPPROG="$(STRIP)" $(INSTALL_STRIP_PROGRAM) $(BGL_UTIL_BIN) $(top_builddir)/release
	@test -f $(MAKENSIS) && echo 'OutFile "$@"' | cat $(top_builddir)/share/setup.nsi - | $(MAKENSIS) -V2 - || \
	  echo error: could not build $@
	@echo built $@

deploy: $(BGL_WIN_INSTALLER)
endif

### Precomputed tables
EXTRA_PROGRAMS = precompute_ecmult precompute_ecmult_gen
CLEANFILES = $(EXTRA_PROGRAMS)

precompute_ecmult_SOURCES = src/precompute_ecmult.c
precompute_ecmult_CPPFLAGS = $(SECP_CONFIG_DEFINES)
precompute_ecmult_LDADD = $(COMMON_LIB)

precompute_ecmult_gen_SOURCES = src/precompute_ecmult_gen.c
precompute_ecmult_gen_CPPFLAGS = $(SECP_CONFIG_DEFINES)
precompute_ecmult_gen_LDADD = $(COMMON_LIB)

# See Automake manual, Section "Errors with distclean".
# We don't list any dependencies for the prebuilt files here because
# otherwise make's decision whether to rebuild them (even in the first
# build by a normal user) depends on mtimes, and thus is very fragile.
# This means that rebuilds of the prebuilt files always need to be
# forced by deleting them, e.g., by invoking `make clean-precomp`.
src/precomputed_ecmult.c:
	$(MAKE) $(AM_MAKEFLAGS) precompute_ecmult$(EXEEXT)
	./precompute_ecmult$(EXEEXT)
src/precomputed_ecmult_gen.c:
	$(MAKE) $(AM_MAKEFLAGS) precompute_ecmult_gen$(EXEEXT)
	./precompute_ecmult_gen$(EXEEXT)

PRECOMP = src/precomputed_ecmult_gen.c src/precomputed_ecmult.c
precomp: $(PRECOMP)

# Ensure the prebuilt files will be build first (only if they don't exist,
# e.g., after `make maintainer-clean`).
BUILT_SOURCES = $(PRECOMP)

maintainer-clean-local: clean-precomp

clean-precomp:
	rm -f $(PRECOMP)

EXTRA_DIST = autogen.sh CHANGELOG.md SECURITY.md
EXTRA_DIST += doc/release-process.md doc/safegcd_implementation.md
EXTRA_DIST += examples/EXAMPLES_COPYING
EXTRA_DIST += sage/gen_exhaustive_groups.sage
EXTRA_DIST += sage/gen_split_lambda_constants.sage
EXTRA_DIST += sage/group_prover.sage
EXTRA_DIST += sage/prove_group_implementations.sage
EXTRA_DIST += sage/secp256k1_params.sage
EXTRA_DIST += sage/weierstrass_prover.sage

if ENABLE_MODULE_ECDH
include src/modules/ecdh/Makefile.am.include
endif

$(BGL_QT_BIN): FORCE
	$(MAKE) -C src qt/$(@F)

$(BGLD_BIN): FORCE
	$(MAKE) -C src $(@F)

$(BGL_CLI_BIN): FORCE
	$(MAKE) -C src $(@F)

$(BGL_TX_BIN): FORCE
	$(MAKE) -C src $(@F)

$(BGL_UTIL_BIN): FORCE
	$(MAKE) -C src $(@F)

$(BGL_WALLET_BIN): FORCE
	$(MAKE) -C src $(@F)

$(BGL_NODE_BIN): FORCE
	$(MAKE) -C src $(@F)

$(BGL_GUI_BIN): FORCE
	$(MAKE) -C src $(@F)

if USE_LCOV
LCOV_FILTER_PATTERN = \
	-p "/usr/local/" \
	-p "/usr/include/" \
	-p "/usr/lib/" \
	-p "/usr/lib64/" \
	-p "src/leveldb/" \
	-p "src/crc32c/" \
	-p "src/bench/" \
	-p "src/crypto/ctaes" \
	-p "src/minisketch" \
	-p "src/secp256k1" \
	-p "depends"

DIR_FUZZ_SEED_CORPUS ?= qa-assets/fuzz_seed_corpus

$(COV_TOOL_WRAPPER):
	@echo 'exec $(COV_TOOL) "$$@"' > $(COV_TOOL_WRAPPER)
	@chmod +x $(COV_TOOL_WRAPPER)

baseline.info: $(COV_TOOL_WRAPPER)
	$(LCOV) -c -i -d $(abs_builddir)/src -o $@

baseline_filtered.info: baseline.info
	$(abs_builddir)/contrib/filter-lcov.py $(LCOV_FILTER_PATTERN) $< $@
	$(LCOV) -a $@ $(LCOV_OPTS) -o $@

fuzz.info: baseline_filtered.info
	@TIMEOUT=15 test/fuzz/test_runner.py $(DIR_FUZZ_SEED_CORPUS) -l DEBUG
	$(LCOV) -c $(LCOV_OPTS) -d $(abs_builddir)/src --t fuzz-tests -o $@
	$(LCOV) -z $(LCOV_OPTS) -d $(abs_builddir)/src

fuzz_filtered.info: fuzz.info
	$(abs_builddir)/contrib/filter-lcov.py $(LCOV_FILTER_PATTERN) $< $@
	$(LCOV) -a $@ $(LCOV_OPTS) -o $@

test_BGL.info: baseline_filtered.info
	$(MAKE) -C src/ check
	$(LCOV) -c $(LCOV_OPTS) -d $(abs_builddir)/src -t test_BGL -o $@
	$(LCOV) -z $(LCOV_OPTS) -d $(abs_builddir)/src

test_BGL_filtered.info: test_BGL.info
	$(abs_builddir)/contrib/filter-lcov.py $(LCOV_FILTER_PATTERN) $< $@
	$(LCOV) -a $@ $(LCOV_OPTS) -o $@

functional_test.info: test_BGL_filtered.info
	@TIMEOUT=15 test/functional/test_runner.py $(EXTENDED_FUNCTIONAL_TESTS)
	$(LCOV) -c $(LCOV_OPTS) -d $(abs_builddir)/src --t functional-tests -o $@
	$(LCOV) -z $(LCOV_OPTS) -d $(abs_builddir)/src

functional_test_filtered.info: functional_test.info
	$(abs_builddir)/contrib/filter-lcov.py $(LCOV_FILTER_PATTERN) $< $@
	$(LCOV) -a $@ $(LCOV_OPTS) -o $@

fuzz_coverage.info: fuzz_filtered.info
	$(LCOV) -a $(LCOV_OPTS) baseline_filtered.info -a fuzz_filtered.info -o $@ | $(GREP) "\%" | $(AWK) '{ print substr($$3,2,50) "/" $$5 }' > coverage_percent.txt

test_BGL_coverage.info: baseline_filtered.info test_BGL_filtered.info
	$(LCOV) -a $(LCOV_OPTS) baseline_filtered.info -a test_BGL_filtered.info -o $@

total_coverage.info: test_BGL_filtered.info functional_test_filtered.info
	$(LCOV) -a $(LCOV_OPTS) baseline_filtered.info -a test_BGL_filtered.info -a functional_test_filtered.info -o $@ | $(GREP) "\%" | $(AWK) '{ print substr($$3,2,50) "/" $$5 }' > coverage_percent.txt

fuzz.coverage/.dirstamp: fuzz_coverage.info
	$(GENHTML) -s $(LCOV_OPTS) $< -o $(@D)
	@touch $@

test_BGL.coverage/.dirstamp:  test_BGL_coverage.info
	$(GENHTML) -s $(LCOV_OPTS) $< -o $(@D)
	@touch $@

total.coverage/.dirstamp: total_coverage.info
	$(GENHTML) -s $(LCOV_OPTS) $< -o $(@D)
	@touch $@

cov_fuzz: fuzz.coverage/.dirstamp

cov: test_BGL.coverage/.dirstamp total.coverage/.dirstamp

endif

dist_noinst_SCRIPTS = autogen.sh

EXTRA_DIST = $(DIST_SHARE) $(DIST_CONTRIB) $(WINDOWS_PACKAGING) $(OSX_PACKAGING) $(BIN_CHECKS)

EXTRA_DIST += \
    test/functional \
    test/fuzz

EXTRA_DIST += \
    test/util/test_runner.py \
    test/util/data/BGL-util-test.json \
    test/util/data/blanktxv1.hex \
    test/util/data/blanktxv1.json \
    test/util/data/blanktxv2.hex \
    test/util/data/blanktxv2.json \
    test/util/data/tt-delin1-out.hex \
    test/util/data/tt-delin1-out.json \
    test/util/data/tt-delout1-out.hex \
    test/util/data/tt-delout1-out.json \
    test/util/data/tt-locktime317000-out.hex \
    test/util/data/tt-locktime317000-out.json \
    test/util/data/tx394b54bb.hex \
    test/util/data/txcreate1.hex \
    test/util/data/txcreate1.json \
    test/util/data/txcreate2.hex \
    test/util/data/txcreate2.json \
    test/util/data/txcreatedata1.hex \
    test/util/data/txcreatedata1.json \
    test/util/data/txcreatedata2.hex \
    test/util/data/txcreatedata2.json \
    test/util/data/txcreatedata_seq0.hex \
    test/util/data/txcreatedata_seq0.json \
    test/util/data/txcreatedata_seq1.hex \
    test/util/data/txcreatedata_seq1.json \
    test/util/data/txcreatemultisig1.hex \
    test/util/data/txcreatemultisig1.json \
    test/util/data/txcreatemultisig2.hex \
    test/util/data/txcreatemultisig2.json \
    test/util/data/txcreatemultisig3.hex \
    test/util/data/txcreatemultisig3.json \
    test/util/data/txcreatemultisig4.hex \
    test/util/data/txcreatemultisig4.json \
    test/util/data/txcreatemultisig5.json \
    test/util/data/txcreateoutpubkey1.hex \
    test/util/data/txcreateoutpubkey1.json \
    test/util/data/txcreateoutpubkey2.hex \
    test/util/data/txcreateoutpubkey2.json \
    test/util/data/txcreateoutpubkey3.hex \
    test/util/data/txcreateoutpubkey3.json \
    test/util/data/txcreatescript1.hex \
    test/util/data/txcreatescript1.json \
    test/util/data/txcreatescript2.hex \
    test/util/data/txcreatescript2.json \
    test/util/data/txcreatescript3.hex \
    test/util/data/txcreatescript3.json \
    test/util/data/txcreatescript4.hex \
    test/util/data/txcreatescript4.json \
    test/util/data/txcreatescript5.hex \
    test/util/data/txcreatescript6.hex \
    test/util/data/txcreatesignsegwit1.hex \
    test/util/data/txcreatesignv1.hex \
    test/util/data/txcreatesignv1.json \
    test/util/data/txcreatesignv2.hex \
    test/util/rpcauth-test.py

CLEANFILES = $(OSX_DMG) $(BGL_WIN_INSTALLER)

DISTCHECK_CONFIGURE_FLAGS = --enable-man

doc/doxygen/.stamp: doc/Doxyfile FORCE
	$(MKDIR_P) $(@D)
	$(DOXYGEN) $^
	$(AM_V_at) touch $@

if HAVE_DOXYGEN
docs: doc/doxygen/.stamp
else
docs:
	@echo "error: doxygen not found"
endif

clean-docs:
	rm -rf doc/doxygen

clean-local: clean-docs
	rm -rf coverage_percent.txt test_BGL.coverage/ total.coverage/ fuzz.coverage/ test/tmp/ cache/ $(OSX_APP)
	rm -rf test/functional/__pycache__ test/functional/test_framework/__pycache__ test/cache share/rpcauth/__pycache__
	rm -rf osx_volname dist/

test-security-check:
if TARGET_DARWIN
	$(AM_V_at) CC='$(CC)' CFLAGS='$(CFLAGS)' CPPFLAGS='$(CPPFLAGS)' LDFLAGS='$(LDFLAGS)' $(PYTHON) $(top_srcdir)/contrib/devtools/test-security-check.py TestSecurityChecks.test_MACHO
	$(AM_V_at) CC='$(CC)' CFLAGS='$(CFLAGS)' CPPFLAGS='$(CPPFLAGS)' LDFLAGS='$(LDFLAGS)' $(PYTHON) $(top_srcdir)/contrib/devtools/test-symbol-check.py TestSymbolChecks.test_MACHO
endif
if TARGET_WINDOWS
	$(AM_V_at) CC='$(CC)' CFLAGS='$(CFLAGS)' CPPFLAGS='$(CPPFLAGS)' LDFLAGS='$(LDFLAGS)' $(PYTHON) $(top_srcdir)/contrib/devtools/test-security-check.py TestSecurityChecks.test_PE
	$(AM_V_at) CC='$(CC)' CFLAGS='$(CFLAGS)' CPPFLAGS='$(CPPFLAGS)' LDFLAGS='$(LDFLAGS)' $(PYTHON) $(top_srcdir)/contrib/devtools/test-symbol-check.py TestSymbolChecks.test_PE
endif
if TARGET_LINUX
	$(AM_V_at) CC='$(CC)' CFLAGS='$(CFLAGS)' CPPFLAGS='$(CPPFLAGS)' LDFLAGS='$(LDFLAGS)' $(PYTHON) $(top_srcdir)/contrib/devtools/test-security-check.py TestSecurityChecks.test_ELF
	$(AM_V_at) CC='$(CC)' CFLAGS='$(CFLAGS)' CPPFLAGS='$(CPPFLAGS)' LDFLAGS='$(LDFLAGS)' $(PYTHON) $(top_srcdir)/contrib/devtools/test-symbol-check.py TestSymbolChecks.test_ELF
endif
