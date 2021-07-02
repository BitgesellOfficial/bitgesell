include sources.mk
ACLOCAL_AMFLAGS = -I build-aux/m4
.PHONY: gen FORCE
.INTERMEDIATE: $(GENBIN)

include_HEADERS = $(UNIVALUE_DIST_HEADERS_INT)
noinst_HEADERS = $(UNIVALUE_LIB_HEADERS_INT)

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
noinst_HEADERS += src/ecmult_const.h
noinst_HEADERS += src/ecmult_const_impl.h
noinst_HEADERS += src/ecmult_gen.h
noinst_HEADERS += src/ecmult_gen_impl.h
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
noinst_HEADERS += src/assumptions.h
noinst_HEADERS += src/util.h
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

if USE_EXTERNAL_ASM
COMMON_LIB = libsecp256k1_common.la
noinst_LTLIBRARIES = $(COMMON_LIB)
else
COMMON_LIB =
endif
.PHONY: deploy FORCE
.INTERMEDIATE: $(OSX_TEMP_ISO) $(COVERAGE_INFO)

export PYTHONPATH

if BUILD_BGL_LIBS
pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = pc/libunivalue.pc

libunivalue_la_SOURCES = $(UNIVALUE_LIB_SOURCES_INT)

libunivalue_la_LDFLAGS = \
	-version-info $(LIBUNIVALUE_CURRENT):$(LIBUNIVALUE_REVISION):$(LIBUNIVALUE_AGE) \
	-no-undefined
libunivalue_la_CXXFLAGS = -I$(top_srcdir)/include

TESTS = test/object test/unitester test/no_nul

GENBIN = gen/gen$(BUILD_EXEEXT)
GEN_SRCS = gen/gen.cpp

$(GENBIN): $(GEN_SRCS)
	@echo Building $@
	$(AM_V_at)c++ -I$(top_srcdir)/include -o $@ $<

gen: $(GENBIN) FORCE
	@echo Updating lib/univalue_escapes.h
	$(AM_V_at)$(GENBIN) > lib/univalue_escapes.h

noinst_PROGRAMS = $(TESTS) test/test_json

test_unitester_SOURCES = $(UNIVALUE_TEST_UNITESTER_INT)
test_unitester_LDADD = libunivalue.la
test_unitester_CXXFLAGS = -I$(top_srcdir)/include -DJSON_TEST_SRC=\"$(srcdir)/$(UNIVALUE_TEST_DATA_DIR_INT)\"
test_unitester_LDFLAGS = -static $(LIBTOOL_APP_LDFLAGS)

test_test_json_SOURCES = $(UNIVALUE_TEST_JSON_INT)
test_test_json_LDADD = libunivalue.la
test_test_json_CXXFLAGS = -I$(top_srcdir)/include
test_test_json_LDFLAGS = -static $(LIBTOOL_APP_LDFLAGS)

test_no_nul_SOURCES = $(UNIVALUE_TEST_NO_NUL_INT)
test_no_nul_LDADD = libunivalue.la
test_no_nul_CXXFLAGS = -I$(top_srcdir)/include
test_no_nul_LDFLAGS = -static $(LIBTOOL_APP_LDFLAGS)

test_object_SOURCES = $(UNIVALUE_TEST_OBJECT_INT)
test_object_LDADD = libunivalue.la
test_object_CXXFLAGS = -I$(top_srcdir)/include
test_object_LDFLAGS = -static $(LIBTOOL_APP_LDFLAGS)

TEST_FILES = $(UNIVALUE_TEST_FILES_INT)

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
	rm -rf osx_volname dist/ dpi36.background.tiff dpi72.background.tiff

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
