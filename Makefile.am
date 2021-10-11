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

EXTRA_DIST=$(UNIVALUE_TEST_FILES_INT) $(GEN_SRCS)
