AC_PREREQ([2.69])
define(_CLIENT_VERSION_MAJOR, 22)
define(_CLIENT_VERSION_MINOR, 99)
define(_CLIENT_VERSION_BUILD, 0)
define(_CLIENT_VERSION_RC, 0)
define(_CLIENT_VERSION_IS_RELEASE, false)
define(_COPYRIGHT_YEAR, 2022)
define(_COPYRIGHT_HOLDERS,[The %s developers])
define(_COPYRIGHT_HOLDERS_SUBSTITUTION,[[BGL Core]])
AC_INIT([BGL Core],m4_join([.], _CLIENT_VERSION_MAJOR, _CLIENT_VERSION_MINOR, _CLIENT_VERSION_BUILD)m4_if(_CLIENT_VERSION_RC, [0], [], [rc]_CLIENT_VERSION_RC),[https://github.com/bitcoin/bitcoin/issues],[BGL],[https://bitcoincore.org/])
AC_CONFIG_SRCDIR([src/validation.cpp])
AC_CONFIG_HEADERS([src/config/BGL-config.h])
AC_CONFIG_AUX_DIR([build-aux])
AC_CONFIG_MACRO_DIR([build-aux/m4])

m4_ifndef([PKG_PROG_PKG_CONFIG], [m4_fatal([PKG_PROG_PKG_CONFIG macro not found. Please install pkg-config and re-run autogen.sh])])
PKG_PROG_PKG_CONFIG
if test "$PKG_CONFIG" = ""; then
  AC_MSG_ERROR([pkg-config not found])
fi

BGL_DAEMON_NAME=BGLd
BGL_GUI_NAME=BGL-qt
BGL_CLI_NAME=BGL-cli
BGL_TX_NAME=BGL-tx
BGL_UTIL_NAME=BGL-util
BGL_WALLET_TOOL_NAME=BGL-wallet
dnl Multi Process
BGL_MP_NODE_NAME=BGL-node
BGL_MP_GUI_NAME=BGL-gui

dnl Unless the user specified ARFLAGS, force it to be cr
AC_ARG_VAR([ARFLAGS], [Flags for the archiver, defaults to <cr> if not set])
if test "${ARFLAGS+set}" != "set"; then
  ARFLAGS="cr"
fi

AC_CANONICAL_HOST

LT_INIT([win32-dll])

dnl faketime breaks configure and is only needed for make. Disable it here.
unset FAKETIME

dnl Automake init set-up and checks
AM_INIT_AUTOMAKE([1.13 no-define subdir-objects foreign])

dnl faketime messes with timestamps and causes configure to be re-run.
dnl --disable-maintainer-mode can be used to bypass this.
AM_MAINTAINER_MODE([enable])

AM_PROG_CC_C_O
AC_PROG_CC_C89
if test x"$ac_cv_prog_cc_c89" = x"no"; then
  AC_MSG_ERROR([c89 compiler support required])
fi
AM_PROG_AS

case $host_os in
  *darwin*)
     if  test x$cross_compiling != xyes; then
       AC_CHECK_PROG([BREW], brew, brew)
       if test x$BREW = xbrew; then
         # These Homebrew packages may be keg-only, meaning that they won't be found
         # in expected paths because they may conflict with system files. Ask
         # Homebrew where each one is located, then adjust paths accordingly.
         if $BREW list --versions valgrind >/dev/null; then
           valgrind_prefix=$($BREW --prefix valgrind 2>/dev/null)
           VALGRIND_CPPFLAGS="-I$valgrind_prefix/include"
         fi
       else
         AC_CHECK_PROG([PORT], port, port)
         # If homebrew isn't installed and macports is, add the macports default paths
         # as a last resort.
         if test x$PORT = xport; then
           CPPFLAGS="$CPPFLAGS -isystem /opt/local/include"
           LDFLAGS="$LDFLAGS -L/opt/local/lib"
         fi
       fi
     fi
   ;;
esac

AC_ARG_WITH([seccomp],
  [AS_HELP_STRING([--with-seccomp],
  [enable experimental syscall sandbox feature (-sandbox), default is yes if seccomp-bpf is detected under Linux x86_64])],
  [seccomp_found=$withval],
  [seccomp_found=auto])

dnl Require C++17 compiler (no GNU extensions)
AX_CXX_COMPILE_STDCXX([17], [noext], [mandatory])

dnl Check if -latomic is required for <std::atomic>
CHECK_ATOMIC

dnl Unless the user specified OBJCXX, force it to be the same as CXX. This ensures
dnl that we get the same -std flags for both.
m4_ifdef([AC_PROG_OBJCXX],[
if test "${OBJCXX+set}" = ""; then
  OBJCXX="${CXX}"
fi
AC_PROG_OBJCXX
])

dnl Since libtool 1.5.2 (released 2004-01-25), on Linux libtool no longer
dnl sets RPATH for any directories in the dynamic linker search path.
dnl See more: https://wiki.debian.org/RpathIssue
LT_PREREQ([1.5.2])
dnl Libtool init checks.
LT_INIT([pic-only])

dnl Check/return PATH for base programs.
AC_PATH_TOOL([AR], [ar])
AC_PATH_TOOL([RANLIB], [ranlib])
AC_PATH_TOOL([STRIP], [strip])
AC_PATH_TOOL([GCOV], [gcov])
AC_PATH_TOOL([LLVM_COV], [llvm-cov])
AC_PATH_PROG([LCOV], [lcov])
dnl Python 3.6 is specified in .python-version and should be used if available, see doc/dependencies.md
AC_PATH_PROGS([PYTHON], [python3.6 python3.7 python3.8 python3.9 python3.10 python3.11 python3 python])
AC_PATH_PROG([GENHTML], [genhtml])
AC_PATH_PROG([GIT], [git])
AC_PATH_PROG([CCACHE], [ccache])
AC_PATH_PROG([XGETTEXT], [xgettext])
AC_PATH_PROG([HEXDUMP], [hexdump])
AC_PATH_TOOL([OBJCOPY], [objcopy])
AC_PATH_PROG([DOXYGEN], [doxygen])
AM_CONDITIONAL([HAVE_DOXYGEN], [test -n "$DOXYGEN"])

AC_ARG_VAR([PYTHONPATH], [Augments the default search path for python module files])

AC_ARG_ENABLE([wallet],
  [AS_HELP_STRING([--disable-wallet],
  [disable wallet (enabled by default)])],
  [enable_wallet=$enableval],
  [enable_wallet=auto])

AC_ARG_WITH([sqlite],
  [AS_HELP_STRING([--with-sqlite=yes|no|auto],
  [enable sqlite wallet support (default: auto, i.e., enabled if wallet is enabled and sqlite is found)])],
  [use_sqlite=$withval],
  [use_sqlite=auto])

AC_ARG_WITH([bdb],
  [AS_HELP_STRING([--without-bdb],
  [disable bdb wallet support (default is enabled if wallet is enabled)])],
  [use_bdb=$withval],
  [use_bdb=auto])

AC_ARG_ENABLE([usdt],
  [AS_HELP_STRING([--enable-usdt],
  [enable tracepoints for Userspace, Statically Defined Tracing (default is yes if sys/sdt.h is found)])],
  [use_usdt=$enableval],
  [use_usdt=yes])

AC_ARG_WITH([miniupnpc],
  [AS_HELP_STRING([--with-miniupnpc],
  [enable UPNP (default is yes if libminiupnpc is found)])],
  [use_upnp=$withval],
  [use_upnp=auto])

AC_ARG_ENABLE([upnp-default],
  [AS_HELP_STRING([--enable-upnp-default],
  [if UPNP is enabled, turn it on at startup (default is no)])],
  [use_upnp_default=$enableval],
  [use_upnp_default=no])

AC_ARG_WITH([natpmp],
            [AS_HELP_STRING([--with-natpmp],
                            [enable NAT-PMP (default is yes if libnatpmp is found)])],
            [use_natpmp=$withval],
            [use_natpmp=auto])

AC_ARG_ENABLE([natpmp-default],
              [AS_HELP_STRING([--enable-natpmp-default],
                              [if NAT-PMP is enabled, turn it on at startup (default is no)])],
              [use_natpmp_default=$enableval],
              [use_natpmp_default=no])

AC_ARG_ENABLE(tests,
    AS_HELP_STRING([--disable-tests],[do not compile tests (default is to compile)]),
    [use_tests=$enableval],
    [use_tests=yes])

AC_ARG_ENABLE(experimental,
    AS_HELP_STRING([--enable-experimental],[allow experimental configure options [default=no]]),
    [use_experimental=$enableval],
    [use_experimental=no])

AC_ARG_ENABLE(exhaustive_tests,
    AS_HELP_STRING([--enable-exhaustive-tests],[compile exhaustive tests [default=yes]]),
    [use_exhaustive_tests=$enableval],
    [use_exhaustive_tests=yes])

AC_ARG_ENABLE(module_ecdh,
    AS_HELP_STRING([--enable-module-ecdh],[enable ECDH shared secret computation]),
    [enable_module_ecdh=$enableval],
    [enable_module_ecdh=no])

AC_ARG_ENABLE(module_recovery,
    AS_HELP_STRING([--enable-module-recovery],[enable ECDSA pubkey recovery module [default=no]]),
    [enable_module_recovery=$enableval],
    [enable_module_recovery=no])

AC_ARG_ENABLE(module_extrakeys,
    AS_HELP_STRING([--enable-module-extrakeys],[enable extrakeys module (experimental)]),
    [enable_module_extrakeys=$enableval],
    [enable_module_extrakeys=no])

AC_ARG_ENABLE(module_schnorrsig,
    AS_HELP_STRING([--enable-module-schnorrsig],[enable schnorrsig module (experimental)]),
    [enable_module_schnorrsig=$enableval],
    [enable_module_schnorrsig=no])

AC_ARG_ENABLE(external_default_callbacks,
    AS_HELP_STRING([--enable-external-default-callbacks],[enable external default callback functions [default=no]]),
    [use_external_default_callbacks=$enableval],
    [use_external_default_callbacks=no])

# Test-only override of the (autodetected by the C code) "widemul" setting.
# Legal values are int64 (for [u]int64_t), int128 (for [unsigned] __int128), and auto (the default).
AC_ARG_WITH([test-override-wide-multiply], [] ,[set_widemul=$withval], [set_widemul=auto])

AC_ARG_WITH([asm], [AS_HELP_STRING([--with-asm=x86_64|arm|no|auto],
[assembly optimizations to use (experimental: arm) [default=auto]])],[req_asm=$withval], [req_asm=auto])

AC_ARG_WITH([ecmult-window], [AS_HELP_STRING([--with-ecmult-window=SIZE|auto],
[window size for ecmult precomputation for verification, specified as integer in range [2..24].]
[Larger values result in possibly better performance at the cost of an exponentially larger precomputed table.]
[The table will store 2^(SIZE-1) * 64 bytes of data but can be larger in memory due to platform-specific padding and alignment.]
[A window size larger than 15 will require you delete the prebuilt ecmult_static_pre_g.h file so that it can be rebuilt.]
[For very large window sizes, use "make -j 1" to reduce memory use during compilation.]
["auto" is a reasonable setting for desktop machines (currently 15). [default=auto]]
)],
[req_ecmult_window=$withval], [req_ecmult_window=auto])

AC_ARG_WITH([ecmult-gen-precision], [AS_HELP_STRING([--with-ecmult-gen-precision=2|4|8|auto],
[Precision bits to tune the precomputed table size for signing.]
[The size of the table is 32kB for 2 bits, 64kB for 4 bits, 512kB for 8 bits of precision.]
[A larger table size usually results in possible faster signing.]
["auto" is a reasonable setting for desktop machines (currently 4). [default=auto]]
)],
[req_ecmult_gen_precision=$withval], [req_ecmult_gen_precision=auto])

AC_ARG_WITH([valgrind], [AS_HELP_STRING([--with-valgrind=yes|no|auto],
[Build with extra checks for running inside Valgrind [default=auto]]
)],
[req_valgrind=$withval], [req_valgrind=auto])

###
### Handle config options (except for modules)
###

if test x"$req_valgrind" = x"no"; then
  enable_valgrind=no
else
  SECP_VALGRIND_CHECK
  if test x"$has_valgrind" != x"yes"; then
    if test x"$req_valgrind" = x"yes"; then
      AC_MSG_ERROR([Valgrind support explicitly requested but valgrind/memcheck.h header not available])
    fi
    enable_valgrind=no
  else
    enable_valgrind=yes
  fi

  dnl Disable all optimizations
  AX_CHECK_COMPILE_FLAG([-O0], [DEBUG_CXXFLAGS="$DEBUG_CXXFLAGS -O0"], [], [$CXXFLAG_WERROR])

  dnl Prefer -g3, fall back to -g if that is unavailable.
  AX_CHECK_COMPILE_FLAG(
    [-g3],
    [DEBUG_CXXFLAGS="$DEBUG_CXXFLAGS -g3"],
    [AX_CHECK_COMPILE_FLAG([-g], [DEBUG_CXXFLAGS="$DEBUG_CXXFLAGS -g"], [], [$CXXFLAG_WERROR])],
    [$CXXFLAG_WERROR])

  AX_CHECK_PREPROC_FLAG([-DDEBUG], [DEBUG_CPPFLAGS="$DEBUG_CPPFLAGS -DDEBUG"], [], [$CXXFLAG_WERROR])
  AX_CHECK_PREPROC_FLAG([-DDEBUG_LOCKORDER], [DEBUG_CPPFLAGS="$DEBUG_CPPFLAGS -DDEBUG_LOCKORDER"], [], [$CXXFLAG_WERROR])
  AX_CHECK_PREPROC_FLAG([-DABORT_ON_FAILED_ASSUME], [DEBUG_CPPFLAGS="$DEBUG_CPPFLAGS -DABORT_ON_FAILED_ASSUME"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-ftrapv], [DEBUG_CXXFLAGS="$DEBUG_CXXFLAGS -ftrapv"], [], [$CXXFLAG_WERROR])
fi

if test x"$enable_coverage" = x"yes"; then
    AC_DEFINE(COVERAGE, 1, [Define this symbol to compile out all VERIFY code])
    SECP_CFLAGS="-O0 --coverage $SECP_CFLAGS"
    LDFLAGS="--coverage $LDFLAGS"
else
    # Most likely the CFLAGS already contain -O2 because that is autoconf's default.
    # We still add it here because passing it twice is not an issue, and handling
    # this case would just add unnecessary complexity (see #896).
    SECP_CFLAGS="-O2 $SECP_CFLAGS"
fi

ERROR_CXXFLAGS=
if test "$enable_werror" = "yes"; then
  if test "$CXXFLAG_WERROR" = ""; then
    AC_MSG_ERROR([enable-werror set but -Werror is not usable])
  fi
  ERROR_CXXFLAGS=$CXXFLAG_WERROR

  dnl -Wreturn-type is broken in GCC for MinGW-w64.
  dnl https://sourceforge.net/p/mingw-w64/bugs/306/
  AX_CHECK_COMPILE_FLAG([-Werror=return-type], [], [ERROR_CXXFLAGS="$ERROR_CXXFLAGS -Wno-error=return-type"], [$CXXFLAG_WERROR],
                        [AC_LANG_SOURCE([[#include <cassert>
                                          int f(){ assert(false); }]])])
fi

if test "$CXXFLAGS_overridden" = "no"; then
  AX_CHECK_COMPILE_FLAG([-Wall], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wall"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wextra], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wextra"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wgnu], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wgnu"], [], [$CXXFLAG_WERROR])
  dnl some compilers will ignore -Wformat-security without -Wformat, so just combine the two here.
  AX_CHECK_COMPILE_FLAG([-Wformat -Wformat-security], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wformat -Wformat-security"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wvla], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wvla"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wshadow-field], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wshadow-field"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wthread-safety], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wthread-safety"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wloop-analysis], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wrange-loop-analysis"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wredundant-decls], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wredundant-decls"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wunused-member-function], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wunused-member-function"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wdate-time], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wdate-time"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wconditional-uninitialized], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wconditional-uninitialized"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wduplicated-branches], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wduplicated-branches"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wduplicated-cond], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wduplicated-cond"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wlogical-op], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wlogical-op"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Woverloaded-virtual], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Woverloaded-virtual"], [], [$CXXFLAG_WERROR])
  dnl -Wsuggest-override is broken with GCC before 9.2
  dnl https://gcc.gnu.org/bugzilla/show_bug.cgi?id=78010
  AX_CHECK_COMPILE_FLAG([-Wsuggest-override], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wsuggest-override"], [], [$CXXFLAG_WERROR],
                        [AC_LANG_SOURCE([[struct A { virtual void f(); }; struct B : A { void f() final; };]])])
  AX_CHECK_COMPILE_FLAG([-Wunreachable-code-loop-increment], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wunreachable-code-loop-increment"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wimplicit-fallthrough], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wimplicit-fallthrough"], [], [$CXXFLAG_WERROR])

  if test "$suppress_external_warnings" != "no" ; then
    AX_CHECK_COMPILE_FLAG([-Wdocumentation], [WARN_CXXFLAGS="$WARN_CXXFLAGS -Wdocumentation"], [], [$CXXFLAG_WERROR])
  fi

  dnl Some compilers (gcc) ignore unknown -Wno-* options, but warn about all
  dnl unknown options if any other warning is produced. Test the -Wfoo case, and
  dnl set the -Wno-foo case if it works.
  AX_CHECK_COMPILE_FLAG([-Wunused-parameter], [NOWARN_CXXFLAGS="$NOWARN_CXXFLAGS -Wno-unused-parameter"], [], [$CXXFLAG_WERROR])
  AX_CHECK_COMPILE_FLAG([-Wself-assign], [NOWARN_CXXFLAGS="$NOWARN_CXXFLAGS -Wno-self-assign"], [], [$CXXFLAG_WERROR])
  if test "$suppress_external_warnings" != "yes" ; then
    AX_CHECK_COMPILE_FLAG([-Wdeprecated-copy], [NOWARN_CXXFLAGS="$NOWARN_CXXFLAGS -Wno-deprecated-copy"], [], [$CXXFLAG_WERROR])
  fi
fi

dnl Don't allow extended (non-ASCII) symbols in identifiers. This is easier for code review.
AX_CHECK_COMPILE_FLAG([-fno-extended-identifiers], [CXXFLAGS="$CXXFLAGS -fno-extended-identifiers"], [], [$CXXFLAG_WERROR])

enable_sse42=no
enable_sse41=no
enable_avx2=no
enable_shani=no

if test "$use_asm" = "yes"; then

dnl Check for optional instruction set support. Enabling these does _not_ imply that all code will
dnl be compiled with them, rather that specific objects/libs may use them after checking for runtime
dnl compatibility.

dnl x86
AX_CHECK_COMPILE_FLAG([-msse4.2], [SSE42_CXXFLAGS="-msse4.2"], [], [$CXXFLAG_WERROR])
AX_CHECK_COMPILE_FLAG([-msse4.1], [SSE41_CXXFLAGS="-msse4.1"], [], [$CXXFLAG_WERROR])
AX_CHECK_COMPILE_FLAG([-mavx -mavx2], [AVX2_CXXFLAGS="-mavx -mavx2"], [], [$CXXFLAG_WERROR])
AX_CHECK_COMPILE_FLAG([-msse4 -msha], [SHANI_CXXFLAGS="-msse4 -msha"], [], [$CXXFLAG_WERROR])

enable_clmul=
AX_CHECK_COMPILE_FLAG([-mpclmul], [enable_clmul=yes], [], [$CXXFLAG_WERROR], [AC_LANG_PROGRAM([
  #include <stdint.h>
  #include <x86intrin.h>
], [
  __m128i a = _mm_cvtsi64_si128((uint64_t)7);
  __m128i b = _mm_clmulepi64_si128(a, a, 37);
  __m128i c = _mm_srli_epi64(b, 41);
  __m128i d = _mm_xor_si128(b, c);
  uint64_t e = _mm_cvtsi128_si64(d);
  return e == 0;
])])

if test "$enable_clmul" = "yes"; then
  CLMUL_CXXFLAGS="-mpclmul"
  AC_DEFINE([HAVE_CLMUL], [1], [Define this symbol if clmul instructions can be used])
fi

TEMP_CXXFLAGS="$CXXFLAGS"
CXXFLAGS="$CXXFLAGS $SSE42_CXXFLAGS"
AC_MSG_CHECKING([for SSE4.2 intrinsics])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[
    #include <stdint.h>
    #if defined(_MSC_VER)
    #include <intrin.h>
    #elif defined(__GNUC__) && defined(__SSE4_2__)
    #include <nmmintrin.h>
    #endif
  ]],[[
    uint64_t l = 0;
    l = _mm_crc32_u8(l, 0);
    l = _mm_crc32_u32(l, 0);
    l = _mm_crc32_u64(l, 0);
    return l;
  ]])],
 [ AC_MSG_RESULT([yes]); enable_sse42=yes],
 [ AC_MSG_RESULT([no])]
)
CXXFLAGS="$TEMP_CXXFLAGS"

TEMP_CXXFLAGS="$CXXFLAGS"
CXXFLAGS="$CXXFLAGS $SSE41_CXXFLAGS"
AC_MSG_CHECKING([for SSE4.1 intrinsics])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[
    #include <stdint.h>
    #include <immintrin.h>
  ]],[[
    __m128i l = _mm_set1_epi32(0);
    return _mm_extract_epi32(l, 3);
  ]])],
 [ AC_MSG_RESULT([yes]); enable_sse41=yes; AC_DEFINE([ENABLE_SSE41], [1], [Define this symbol to build code that uses SSE4.1 intrinsics]) ],
 [ AC_MSG_RESULT([no])]
)
CXXFLAGS="$TEMP_CXXFLAGS"

TEMP_CXXFLAGS="$CXXFLAGS"
CXXFLAGS="$CXXFLAGS $AVX2_CXXFLAGS"
AC_MSG_CHECKING([for AVX2 intrinsics])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[
    #include <stdint.h>
    #include <immintrin.h>
  ]],[[
    __m256i l = _mm256_set1_epi32(0);
    return _mm256_extract_epi32(l, 7);
  ]])],
 [ AC_MSG_RESULT([yes]); enable_avx2=yes; AC_DEFINE([ENABLE_AVX2], [1], [Define this symbol to build code that uses AVX2 intrinsics]) ],
 [ AC_MSG_RESULT([no])]
)
CXXFLAGS="$TEMP_CXXFLAGS"

TEMP_CXXFLAGS="$CXXFLAGS"
CXXFLAGS="$CXXFLAGS $SHANI_CXXFLAGS"
AC_MSG_CHECKING([for SHA-NI intrinsics])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[
    #include <stdint.h>
    #include <immintrin.h>
  ]],[[
    __m128i i = _mm_set1_epi32(0);
    __m128i j = _mm_set1_epi32(1);
    __m128i k = _mm_set1_epi32(2);
    return _mm_extract_epi32(_mm_sha256rnds2_epu32(i, i, k), 0);
  ]])],
 [ AC_MSG_RESULT([yes]); enable_shani=yes; AC_DEFINE([ENABLE_SHANI], [1], [Define this symbol to build code that uses SHA-NI intrinsics]) ],
 [ AC_MSG_RESULT([no])]
)
CXXFLAGS="$TEMP_CXXFLAGS"

# ARM
AX_CHECK_COMPILE_FLAG([-march=armv8-a+crc+crypto], [ARM_CRC_CXXFLAGS="-march=armv8-a+crc+crypto"], [], [$CXXFLAG_WERROR])

TEMP_CXXFLAGS="$CXXFLAGS"
CXXFLAGS="$CXXFLAGS $ARM_CRC_CXXFLAGS"
AC_MSG_CHECKING([for AArch64 CRC32 intrinsics])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[
    #include <arm_acle.h>
    #include <arm_neon.h>
  ]],[[
#ifdef __aarch64__
    __crc32cb(0, 0); __crc32ch(0, 0); __crc32cw(0, 0); __crc32cd(0, 0);
    vmull_p64(0, 0);
#else
#error "crc32c library does not support hardware acceleration on 32-bit ARM"
#endif
  ]])],
 [ AC_MSG_RESULT([yes]); enable_arm_crc=yes; ],
 [ AC_MSG_RESULT([no])]
)
CXXFLAGS="$TEMP_CXXFLAGS"

fi

CPPFLAGS="$CPPFLAGS -DHAVE_BUILD_INFO"

AC_ARG_WITH([utils],
  [AS_HELP_STRING([--with-utils],
  [build BGL-cli BGL-tx BGL-util BGL-wallet (default=yes)])],
  [build_BGL_utils=$withval],
  [build_BGL_utils=yes])

AC_ARG_ENABLE([util-cli],
  [AS_HELP_STRING([--enable-util-cli],
  [build BGL-cli])],
  [build_BGL_cli=$enableval],
  [build_BGL_cli=$build_BGL_utils])

AC_ARG_ENABLE([util-tx],
  [AS_HELP_STRING([--enable-util-tx],
  [build BGL-tx])],
  [build_BGL_tx=$enableval],
  [build_BGL_tx=$build_BGL_utils])

AC_ARG_ENABLE([util-wallet],
  [AS_HELP_STRING([--enable-util-wallet],
  [build BGL-wallet])],
  [build_BGL_wallet=$enableval],
  [build_BGL_wallet=$build_BGL_utils])

AC_ARG_ENABLE([util-util],
  [AS_HELP_STRING([--enable-util-util],
  [build BGL-util])],
  [build_BGL_util=$enableval],
  [build_BGL_util=$build_BGL_utils])

AC_ARG_WITH([libs],
  [AS_HELP_STRING([--with-libs],
  [build libraries (default=yes)])],
  [build_BGL_libs=$withval],
  [build_BGL_libs=yes])

AC_ARG_WITH([daemon],
  [AS_HELP_STRING([--with-daemon],
  [build BGLd daemon (default=yes)])],
  [build_BGLd=$withval],
  [build_BGLd=yes])

case $host in
  *mingw*)
     TARGET_OS=windows
     AC_CHECK_LIB([kernel32], [GetModuleFileNameA],      [], [AC_MSG_ERROR([libkernel32 missing])])
     AC_CHECK_LIB([user32],   [main],                    [], [AC_MSG_ERROR([libuser32 missing])])
     AC_CHECK_LIB([gdi32],    [main],                    [], [AC_MSG_ERROR([libgdi32 missing])])
     AC_CHECK_LIB([comdlg32], [main],                    [], [AC_MSG_ERROR([libcomdlg32 missing])])
     AC_CHECK_LIB([winmm],    [main],                    [], [AC_MSG_ERROR([libwinmm missing])])
     AC_CHECK_LIB([shell32],  [SHGetSpecialFolderPathW], [], [AC_MSG_ERROR([libshell32 missing])])
     AC_CHECK_LIB([comctl32], [main],                    [], [AC_MSG_ERROR([libcomctl32 missing])])
     AC_CHECK_LIB([ole32],    [CoCreateInstance],        [], [AC_MSG_ERROR([libole32 missing])])
     AC_CHECK_LIB([oleaut32], [main],                    [], [AC_MSG_ERROR([liboleaut32 missing])])
     AC_CHECK_LIB([uuid],     [main],                    [], [AC_MSG_ERROR([libuuid missing])])
     AC_CHECK_LIB([advapi32], [CryptAcquireContextW],    [], [AC_MSG_ERROR([libadvapi32 missing])])
     AC_CHECK_LIB([ws2_32],   [WSAStartup],              [], [AC_MSG_ERROR([libws2_32 missing])])
     AC_CHECK_LIB([shlwapi],  [PathRemoveFileSpecW],     [], [AC_MSG_ERROR([libshlwapi missing])])
     AC_CHECK_LIB([iphlpapi], [GetAdaptersAddresses],    [], [AC_MSG_ERROR([libiphlpapi missing])])

     dnl -static is interpreted by libtool, where it has a different meaning.
     dnl In libtool-speak, it's -all-static.
     AX_CHECK_LINK_FLAG([-static], [LIBTOOL_APP_LDFLAGS="$LIBTOOL_APP_LDFLAGS -all-static"])

     AC_PATH_PROG([MAKENSIS], [makensis], [none])
     if test "$MAKENSIS" = "none"; then
       AC_MSG_WARN([makensis not found. Cannot create installer.])
     fi

     AC_PATH_TOOL([WINDRES], [windres], [none])
     if test "$WINDRES" = "none"; then
       AC_MSG_ERROR([windres not found])
     fi

     CPPFLAGS="$CPPFLAGS -D_MT -DWIN32 -D_WINDOWS -D_WIN32_WINNT=0x0601 -D_WIN32_IE=0x0501 -DWIN32_LEAN_AND_MEAN"

     dnl libtool insists upon adding -nostdlib and a list of objects/libs to link against.
     dnl That breaks our ability to build dll's with static libgcc/libstdc++/libssp. Override
     dnl its command here, with the predeps/postdeps removed, and -static inserted. Postdeps are
     dnl also overridden to prevent their insertion later.
     dnl This should only affect dll's.
     archive_cmds_CXX="\$CC -shared \$libobjs \$deplibs \$compiler_flags -static -o \$output_objdir/\$soname \${wl}--enable-auto-image-base -Xlinker --out-implib -Xlinker \$lib"
     postdeps_CXX=

     dnl We require Windows 7 (NT 6.1) or later
     AX_CHECK_LINK_FLAG([-Wl,--major-subsystem-version -Wl,6 -Wl,--minor-subsystem-version -Wl,1], [LDFLAGS="$LDFLAGS -Wl,--major-subsystem-version -Wl,6 -Wl,--minor-subsystem-version -Wl,1"], [], [$LDFLAG_WERROR])
     ;;
  *darwin*)
     TARGET_OS=darwin
     if  test $cross_compiling != "yes"; then
       BUILD_OS=darwin
       AC_CHECK_PROG([BREW], [brew], [brew])
       if test "$BREW" = "brew"; then
         dnl These Homebrew packages may be keg-only, meaning that they won't be found
         dnl in expected paths because they may conflict with system files. Ask
         dnl Homebrew where each one is located, then adjust paths accordingly.
         dnl It's safe to add these paths even if the functionality is disabled by
         dnl the user (--without-wallet or --without-gui for example).

         if test "$use_bdb" != "no" && $BREW list --versions berkeley-db@4 >/dev/null && test "$BDB_CFLAGS" = "" && test "$BDB_LIBS" = ""; then
           bdb_prefix=$($BREW --prefix berkeley-db@4 2>/dev/null)
           dnl This must precede the call to BGL_FIND_BDB48 below.
           BDB_CFLAGS="-I$bdb_prefix/include"
           BDB_LIBS="-L$bdb_prefix/lib -ldb_cxx-4.8"
         fi

         if test "$use_sqlite" != "no" && $BREW list --versions sqlite3 >/dev/null; then
           export PKG_CONFIG_PATH="$($BREW --prefix sqlite3 2>/dev/null)/lib/pkgconfig:$PKG_CONFIG_PATH"
         fi

         if $BREW list --versions qt@5 >/dev/null; then
           export PKG_CONFIG_PATH="$($BREW --prefix qt@5 2>/dev/null)/lib/pkgconfig:$PKG_CONFIG_PATH"
         fi

         case $host in
           *aarch64*)
             dnl The preferred Homebrew prefix for Apple Silicon is /opt/homebrew.
             dnl Therefore, as we do not use pkg-config to detect miniupnpc and libnatpmp
             dnl packages, we should set the CPPFLAGS and LDFLAGS variables for them
             dnl explicitly.
             if test "$use_upnp" != "no" && $BREW list --versions miniupnpc >/dev/null; then
               miniupnpc_prefix=$($BREW --prefix miniupnpc 2>/dev/null)
               if test "$suppress_external_warnings" != "no"; then
                 CPPFLAGS="$CPPFLAGS -isystem $miniupnpc_prefix/include"
               else
                 CPPFLAGS="$CPPFLAGS -I$miniupnpc_prefix/include"
               fi
               LDFLAGS="$LDFLAGS -L$miniupnpc_prefix/lib"
             fi
             if test "$use_natpmp" != "no" && $BREW list --versions libnatpmp >/dev/null; then
               libnatpmp_prefix=$($BREW --prefix libnatpmp 2>/dev/null)
               if test "$suppress_external_warnings" != "no"; then
                 CPPFLAGS="$CPPFLAGS -isystem $libnatpmp_prefix/include"
               else
                 CPPFLAGS="$CPPFLAGS -I$libnatpmp_prefix/include"
               fi
               LDFLAGS="$LDFLAGS -L$libnatpmp_prefix/lib"
             fi
             ;;
         esac
       fi
     else
       case $build_os in
         *darwin*)
           BUILD_OS=darwin
           ;;
         *)
           AC_PATH_TOOL([DSYMUTIL], [dsymutil], [dsymutil])
           AC_PATH_TOOL([INSTALLNAMETOOL], [install_name_tool], [install_name_tool])
           AC_PATH_TOOL([OTOOL], [otool], [otool])
           AC_PATH_PROGS([XORRISOFS], [xorrisofs], [xorrisofs])
           AC_PATH_PROGS([DMG], [dmg], [dmg])

           dnl libtool will try to strip the static lib, which is a problem for
           dnl cross-builds because strip attempts to call a hard-coded ld,
           dnl which may not exist in the path. Stripping the .a is not
           dnl necessary, so just disable it.
           old_striplib=
           ;;
       esac
     fi

     AX_CHECK_LINK_FLAG([-Wl,-headerpad_max_install_names], [LDFLAGS="$LDFLAGS -Wl,-headerpad_max_install_names"], [], [$LDFLAG_WERROR])
     CPPFLAGS="$CPPFLAGS -DMAC_OSX -DOBJC_OLD_DISPATCH_PROTOTYPES=0"
     OBJCXXFLAGS="$CXXFLAGS"
     ;;
   *android*)
     dnl make sure android stays above linux for hosts like *linux-android*
     TARGET_OS=android
     case $host in
       *x86_64*)
          ANDROID_ARCH=x86_64
          ;;
        *aarch64*)
          ANDROID_ARCH=arm64-v8a
          ;;
        *armv7a*)
          ANDROID_ARCH=armeabi-v7a
          ;;
        *) AC_MSG_ERROR([Could not determine Android arch, or it is unsupported]) ;;
      esac
     ;;
   *linux*)
     TARGET_OS=linux
     ;;
esac

if test "$use_extended_functional_tests" != "no"; then
  AC_SUBST(EXTENDED_FUNCTIONAL_TESTS, --extended)
fi

if test "$use_lcov" = "yes"; then
  if test "$LCOV" = ""; then
    AC_MSG_ERROR([lcov testing requested but lcov not found])
  fi
  if test "$PYTHON" = ""; then
    AC_MSG_ERROR([lcov testing requested but python not found])
  fi
  if test "$GENHTML" = ""; then
    AC_MSG_ERROR([lcov testing requested but genhtml not found])
  fi

  AC_MSG_CHECKING([whether compiler is Clang])
  AC_PREPROC_IFELSE([AC_LANG_SOURCE([[
      #if defined(__clang__) && defined(__llvm__)
      // Compiler is Clang
      #else
      #  error Compiler is not Clang
      #endif
    ]])],[
      AC_MSG_RESULT([yes])
      if test "$LLVM_COV" = ""; then
        AC_MSG_ERROR([lcov testing requested but llvm-cov not found])
      fi
      COV_TOOL="$LLVM_COV gcov"
    ],[
      AC_MSG_RESULT([no])
      if test "$GCOV" = "x"; then
        AC_MSG_ERROR([lcov testing requested but gcov not found])
      fi
      COV_TOOL="$GCOV"
  ])
  AC_SUBST(COV_TOOL)
  AC_SUBST(COV_TOOL_WRAPPER, "cov_tool_wrapper.sh")
  LCOV="$LCOV --gcov-tool $(pwd)/$COV_TOOL_WRAPPER"

  AX_CHECK_LINK_FLAG([--coverage], [LDFLAGS="$LDFLAGS --coverage"],
    [AC_MSG_ERROR([lcov testing requested but --coverage linker flag does not work])])
  AX_CHECK_COMPILE_FLAG([--coverage],[CXXFLAGS="$CXXFLAGS --coverage"],
    [AC_MSG_ERROR([lcov testing requested but --coverage flag does not work])])
  CXXFLAGS="$CXXFLAGS -Og"
fi

if test "$use_lcov_branch" != "no"; then
  AC_SUBST(LCOV_OPTS, "$LCOV_OPTS --rc lcov_branch_coverage=1")
fi

if test x"$enable_valgrind" = x"yes"; then
  SECP_INCLUDES="$SECP_INCLUDES $VALGRIND_CPPFLAGS"
fi

if test "$enable_wallet" != "no"; then
    dnl Check for libdb_cxx only if wallet enabled
    if test "x$use_bdb" != "xno"; then
      BGL_FIND_BDB48
      if test x$suppress_external_warnings != xno ; then
        BDB_CPPFLAGS=SUPPRESS_WARNINGS($BDB_CPPFLAGS)
      fi
    fi

    dnl Check for sqlite3
    if test "$use_sqlite" != "no"; then
      PKG_CHECK_MODULES([SQLITE], [sqlite3 >= 3.7.17], [have_sqlite=yes], [have_sqlite=no])
    fi
    AC_MSG_CHECKING([whether to build wallet with support for sqlite])
    if test "$use_sqlite" = "no"; then
      use_sqlite=no
    elif test "$have_sqlite" = "no"; then
      if test "$use_sqlite" = "yes"; then
        AC_MSG_ERROR([sqlite support requested but cannot be built. Use --without-sqlite])
      fi
      use_sqlite=no
    else
      if test "$use_sqlite" != "no"; then
        AC_DEFINE([USE_SQLITE],[1],[Define if sqlite support should be compiled in])
        use_sqlite=yes
      fi
    fi
    AC_MSG_RESULT([$use_sqlite])

    dnl Disable wallet if both --without-bdb and --without-sqlite
    if test "$use_bdb$use_sqlite" = "nono"; then
        if test "$enable_wallet" = "yes"; then
            AC_MSG_ERROR([wallet functionality requested but no BDB or SQLite support available.])
        fi
        enable_wallet=no
    fi
fi

if test "$use_usdt" != "no"; then
  AC_MSG_CHECKING([whether Userspace, Statically Defined Tracing tracepoints are supported])
  AC_COMPILE_IFELSE([
    AC_LANG_PROGRAM(
      [#include <sys/sdt.h>],
      [DTRACE_PROBE("context", "event");]
    )],
    [AC_MSG_RESULT([yes]); AC_DEFINE([ENABLE_TRACING], [1], [Define to 1 to enable tracepoints for Userspace, Statically Defined Tracing])],
    [AC_MSG_RESULT([no]); use_usdt=no;]
  )
fi

if test "$build_BGL_cli$build_BGL_tx$build_BGL_util$build_BGLd$BGL_enable_qt$use_bench$use_tests" = "nonononononono"; then
  use_upnp=no
  use_natpmp=no
  use_zmq=no
fi

dnl Check for libminiupnpc (optional)
if test "$use_upnp" != "no"; then
  AC_CHECK_HEADERS(
    [miniupnpc/miniupnpc.h miniupnpc/upnpcommands.h miniupnpc/upnperrors.h],
    [AC_CHECK_LIB([miniupnpc], [upnpDiscover], [MINIUPNPC_LIBS=-lminiupnpc], [have_miniupnpc=no])],
    [have_miniupnpc=no]
  )
dnl The minimum supported miniUPnPc API version is set to 10. This keeps compatibility
dnl with Ubuntu 16.04 LTS and Debian 8 libminiupnpc-dev packages.
if test "$have_miniupnpc" != "no"; then
  AC_MSG_CHECKING([whether miniUPnPc API version is supported])
  AC_PREPROC_IFELSE([AC_LANG_PROGRAM([[
      @%:@include <miniupnpc/miniupnpc.h>
    ]], [[
      #if MINIUPNPC_API_VERSION >= 10
      // Everything is okay
      #else
      #  error miniUPnPc API version is too old
      #endif
    ]])],[
      AC_MSG_RESULT([yes])
    ],[
    AC_MSG_RESULT([no])
    AC_MSG_WARN([miniUPnPc API version < 10 is unsupported, disabling UPnP support.])
    have_miniupnpc=no
  ])
fi
fi

dnl Check for libnatpmp (optional).
if test "$use_natpmp" != "no"; then
  AC_CHECK_HEADERS([natpmp.h],
                   [AC_CHECK_LIB([natpmp], [initnatpmp], [NATPMP_LIBS=-lnatpmp], [have_natpmp=no])],
                   [have_natpmp=no])
fi

if test "$build_BGL_wallet$build_BGL_cli$build_BGL_tx$build_BGLd$BGL_enable_qt$use_tests$use_bench" = "nonononononono"; then
  use_boost=no
else
  use_boost=yes
fi

if test "$use_boost" = "yes"; then

  dnl Check for Boost headers
  AX_BOOST_BASE([1.64.0],[],[AC_MSG_ERROR([Boost is not available!])])
  if test "$want_boost" = "no"; then
    AC_MSG_ERROR([only libBGLconsensus can be built without Boost])
  fi
  AX_BOOST_SYSTEM
  AX_BOOST_FILESYSTEM

  if test "$suppress_external_warnings" != "no"; then
    BOOST_CPPFLAGS=SUPPRESS_WARNINGS($BOOST_CPPFLAGS)
  fi

  BOOST_LIBS="$BOOST_LDFLAGS $BOOST_SYSTEM_LIB $BOOST_FILESYSTEM_LIB"
fi

if test "$use_external_signer" != "no"; then
  AC_DEFINE([ENABLE_EXTERNAL_SIGNER], [], [Define if external signer support is enabled])
fi
AM_CONDITIONAL([ENABLE_EXTERNAL_SIGNER], [test "$use_external_signer" = "yes"])

dnl Do not compile with syscall sandbox support when compiling under the sanitizers.
dnl The sanitizers introduce use of syscalls that are not typically used in BGLd
dnl (such as execve when the sanitizers execute llvm-symbolizer).
if test "$use_sanitizers" != ""; then
  AC_MSG_WARN([Specifying --with-sanitizers forces --without-seccomp since the sanitizers introduce use of syscalls not allowed by the BGLd syscall sandbox (-sandbox=<mode>).])
  seccomp_found=no
fi
if test "$seccomp_found" != "no"; then
  AC_MSG_CHECKING([for seccomp-bpf (Linux x86-64)])
  AC_PREPROC_IFELSE([AC_LANG_PROGRAM([[
      @%:@include <linux/seccomp.h>
    ]], [[
      #if !defined(__x86_64__)
      #  error Syscall sandbox is an experimental feature currently available only under Linux x86-64.
      #endif
    ]])],[
      AC_MSG_RESULT([yes])
      seccomp_found="yes"
      AC_DEFINE([USE_SYSCALL_SANDBOX], [1], [Define this symbol to build with syscall sandbox support.])
    ],[
      AC_MSG_RESULT([no])
      seccomp_found="no"
  ])
fi
dnl Currently only enable -sandbox=<mode> feature if seccomp is found.
dnl In the future, sandboxing could be also be supported with other
dnl sandboxing mechanisms besides seccomp.
use_syscall_sandbox=$seccomp_found
AM_CONDITIONAL([ENABLE_SYSCALL_SANDBOX], [test "$use_syscall_sandbox" != "no"])

dnl Check for reduced exports
if test "$use_reduce_exports" = "yes"; then
  AX_CHECK_COMPILE_FLAG([-fvisibility=hidden], [CXXFLAGS="$CXXFLAGS -fvisibility=hidden"],
  [AC_MSG_ERROR([Cannot set hidden symbol visibility. Use --disable-reduce-exports.])], [$CXXFLAG_WERROR])
  AX_CHECK_LINK_FLAG([-Wl,--exclude-libs,ALL], [RELDFLAGS="-Wl,--exclude-libs,ALL"], [], [$LDFLAG_WERROR])
fi

if test "$use_tests" = "yes"; then

  if test "$HEXDUMP" = ""; then
    AC_MSG_ERROR([hexdump is required for tests])
  fi

  if test "$use_boost" = "yes"; then

    AX_BOOST_UNIT_TEST_FRAMEWORK

    dnl Determine if -DBOOST_TEST_DYN_LINK is needed
    AC_MSG_CHECKING([for dynamic linked boost test])
    TEMP_LIBS="$LIBS"
    LIBS="$LIBS $BOOST_LDFLAGS $BOOST_UNIT_TEST_FRAMEWORK_LIB"
    TEMP_CPPFLAGS="$CPPFLAGS"
    CPPFLAGS="$CPPFLAGS $BOOST_CPPFLAGS"
    AC_LINK_IFELSE([AC_LANG_SOURCE([
         #define BOOST_TEST_DYN_LINK
         #define BOOST_TEST_MAIN
          #include <boost/test/unit_test.hpp>

         ])],
      [AC_MSG_RESULT([yes])]
      [TESTDEFS="$TESTDEFS -DBOOST_TEST_DYN_LINK"],
      [AC_MSG_RESULT([no])])
    LIBS="$TEMP_LIBS"
    CPPFLAGS="$TEMP_CPPFLAGS"

  fi
fi

dnl libevent check

if test "$build_BGL_cli$build_BGLd$BGL_enable_qt$use_tests$use_bench" != "nonononono"; then
  PKG_CHECK_MODULES([EVENT], [libevent >= 2.0.21], [use_libevent=yes], [AC_MSG_ERROR([libevent version 2.0.21 or greater not found.])])
  if test "$TARGET_OS" != "windows"; then
    PKG_CHECK_MODULES([EVENT_PTHREADS], [libevent_pthreads >= 2.0.21],, [AC_MSG_ERROR([libevent_pthreads version 2.0.21 or greater not found.])])
  fi

  if test "$suppress_external_warnings" != "no"; then
    EVENT_CFLAGS=SUPPRESS_WARNINGS($EVENT_CFLAGS)
  fi
fi

dnl QR Code encoding library check

if test "$use_qr" != "no"; then
  BGL_QT_CHECK([PKG_CHECK_MODULES([QR], [libqrencode], [have_qrencode=yes], [have_qrencode=no])])
fi

dnl ZMQ check

if test "$use_zmq" = "yes"; then
  PKG_CHECK_MODULES([ZMQ], [libzmq >= 4],
    AC_DEFINE([ENABLE_ZMQ], [1], [Define to 1 to enable ZMQ functions]),
    [AC_DEFINE([ENABLE_ZMQ], [0], [Define to 1 to enable ZMQ functions])
    AC_MSG_WARN([libzmq version 4.x or greater not found, disabling])
    use_zmq=no])
else
  AC_DEFINE_UNQUOTED([ENABLE_ZMQ], [0], [Define to 1 to enable ZMQ functions])
fi

if test "$use_zmq" = "yes"; then
  dnl Assume libzmq was built for static linking
  case $host in
    *mingw*)
      ZMQ_CFLAGS="$ZMQ_CFLAGS -DZMQ_STATIC"
    ;;
  esac
fi

dnl libmultiprocess library check

libmultiprocess_found=no
if test "$with_libmultiprocess" = "yes" || test "$with_libmultiprocess" = "auto"; then
  PKG_CHECK_MODULES([LIBMULTIPROCESS], [libmultiprocess], [
     libmultiprocess_found=yes;
     libmultiprocess_prefix=`$PKG_CONFIG --variable=prefix libmultiprocess`;
  ], [true])
elif test "$with_libmultiprocess" != "no"; then
  AC_MSG_ERROR([--with-libmultiprocess=$with_libmultiprocess value is not yes, auto, or no])
fi

dnl Enable multiprocess check

if test "$enable_multiprocess" = "yes"; then
  if test "$libmultiprocess_found" != "yes"; then
    AC_MSG_ERROR([--enable-multiprocess=yes option specified but libmultiprocess library was not found. May need to install libmultiprocess library, or specify install path with PKG_CONFIG_PATH environment variable. Running 'pkg-config --debug libmultiprocess' may be helpful for debugging.])
  fi
  build_multiprocess=yes
elif test "$enable_multiprocess" = "auto"; then
  build_multiprocess=$libmultiprocess_found
else
  build_multiprocess=no
fi

AM_CONDITIONAL([BUILD_MULTIPROCESS], [test "$build_multiprocess" = "yes"])
AM_CONDITIONAL([BUILD_BGL_NODE], [test "$build_multiprocess" = "yes"])
AM_CONDITIONAL([BUILD_BGL_GUI], [test "$build_multiprocess" = "yes"])

dnl codegen tools check

if test "$build_multiprocess" != "no"; then
  if test "$with_mpgen" = "yes" || test "$with_mpgen" = "auto"; then
    MPGEN_PREFIX="$libmultiprocess_prefix"
  elif test "$with_mpgen" != "no"; then
    MPGEN_PREFIX="$with_mpgen";
  fi
  AC_SUBST(MPGEN_PREFIX)
fi

AC_MSG_CHECKING([whether to build BGLd])
AM_CONDITIONAL([BUILD_BGLD], [test $build_BGLd = "yes"])
AC_MSG_RESULT($build_BGLd)

AC_MSG_CHECKING([whether to build BGL-cli])
AM_CONDITIONAL([BUILD_BGL_CLI], [test $build_BGL_cli = "yes"])
AC_MSG_RESULT($build_BGL_cli)

AC_MSG_CHECKING([whether to build BGL-tx])
AM_CONDITIONAL([BUILD_BGL_TX], [test $build_BGL_tx = "yes"])
AC_MSG_RESULT($build_BGL_tx)

AC_MSG_CHECKING([whether to build BGL-wallet])
AM_CONDITIONAL([BUILD_BGL_WALLET], [test $build_BGL_wallet = "yes"])
AC_MSG_RESULT($build_BGL_wallet)

AC_MSG_CHECKING([whether to build BGL-util])
AM_CONDITIONAL([BUILD_BGL_UTIL], [test $build_BGL_util = "yes"])
AC_MSG_RESULT($build_BGL_util)

AC_MSG_CHECKING([whether to build libraries])
AM_CONDITIONAL([BUILD_BGL_LIBS], [test $build_BGL_libs = "yes"])
if test "$build_BGL_libs" = "yes"; then
  AC_DEFINE([HAVE_CONSENSUS_LIB], [1], [Define this symbol if the consensus lib has been built])
  AC_CONFIG_FILES([libBGLconsensus.pc:libBGLconsensus.pc.in])
fi
AC_MSG_RESULT($build_BGL_libs)

AC_LANG_POP

if test "$use_ccache" != "no"; then
  AC_MSG_CHECKING([if ccache should be used])
  if test "$CCACHE" = ""; then
    if test "$use_ccache" = "yes"; then
      AC_MSG_ERROR([ccache not found.]);
    else
      use_ccache=no
    fi
  else
    use_ccache=yes
    CC="$ac_cv_path_CCACHE $CC"
    CXX="$ac_cv_path_CCACHE $CXX"
  fi
  AC_MSG_RESULT($use_ccache)
  if test "$use_ccache" = "yes"; then
    AX_CHECK_COMPILE_FLAG([-fdebug-prefix-map=A=B], [DEBUG_CXXFLAGS="$DEBUG_CXXFLAGS -fdebug-prefix-map=\$(abs_top_srcdir)=."], [], [$CXXFLAG_WERROR])
    AX_CHECK_PREPROC_FLAG([-fmacro-prefix-map=A=B], [DEBUG_CPPFLAGS="$DEBUG_CPPFLAGS -fmacro-prefix-map=\$(abs_top_srcdir)=."], [], [$CXXFLAG_WERROR])
  fi
fi

dnl enable wallet
AC_MSG_CHECKING([if wallet should be enabled])
if test "$enable_wallet" != "no"; then
  AC_MSG_RESULT([yes])
  AC_DEFINE_UNQUOTED([ENABLE_WALLET],[1],[Define to 1 to enable wallet functions])
  enable_wallet=yes

else
  AC_MSG_RESULT([no])
fi

dnl enable upnp support
AC_MSG_CHECKING([whether to build with support for UPnP])
if test "$have_miniupnpc" = "no"; then
  if test "$use_upnp" = "yes"; then
     AC_MSG_ERROR([UPnP requested but cannot be built. Use --without-miniupnpc])
  fi
  AC_MSG_RESULT([no])
  use_upnp=no
else
  if test "$use_upnp" != "no"; then
    AC_MSG_RESULT([yes])
    AC_MSG_CHECKING([whether to build with UPnP enabled by default])
    use_upnp=yes
    upnp_setting=0
    if test "$use_upnp_default" != "no"; then
      use_upnp_default=yes
      upnp_setting=1
    fi
    AC_MSG_RESULT([$use_upnp_default])
    AC_DEFINE_UNQUOTED([USE_UPNP],[$upnp_setting],[UPnP support not compiled if undefined, otherwise value (0 or 1) determines default state])
    if test "$TARGET_OS" = "windows"; then
      MINIUPNPC_CPPFLAGS="-DSTATICLIB -DMINIUPNP_STATICLIB"
    fi
  else
    AC_MSG_RESULT([no])
  fi
fi

dnl Enable NAT-PMP support.
AC_MSG_CHECKING([whether to build with support for NAT-PMP])
if test "$have_natpmp" = "no"; then
  if test "$use_natpmp" = "yes"; then
     AC_MSG_ERROR([NAT-PMP requested but cannot be built. Use --without-natpmp])
  fi
  AC_MSG_RESULT([no])
  use_natpmp=no
else
  if test "$use_natpmp" != "no"; then
    AC_MSG_RESULT([yes])
    AC_MSG_CHECKING([whether to build with NAT-PMP enabled by default])
    use_natpmp=yes
    natpmp_setting=0
    if test "$use_natpmp_default" != "no"; then
      use_natpmp_default=yes
      natpmp_setting=1
    fi
    AC_MSG_RESULT($use_natpmp_default)
    AC_DEFINE_UNQUOTED([USE_NATPMP], [$natpmp_setting], [NAT-PMP support not compiled if undefined, otherwise value (0 or 1) determines default state])
    if test "$TARGET_OS" = "windows"; then
      NATPMP_CPPFLAGS="-DSTATICLIB -DNATPMP_STATICLIB"
    fi
  else
    AC_MSG_RESULT([no])
  fi
fi

dnl these are only used when qt is enabled
BUILD_TEST_QT=""
if test "$BGL_enable_qt" != "no"; then
  dnl enable dbus support
  AC_MSG_CHECKING([whether to build GUI with support for D-Bus])
  if test "$BGL_enable_qt_dbus" != "no"; then
    AC_DEFINE([USE_DBUS], [1], [Define if dbus support should be compiled in])
  fi
  AC_MSG_RESULT($BGL_enable_qt_dbus)

  dnl enable qr support
  AC_MSG_CHECKING([whether to build GUI with support for QR codes])
  if test "$have_qrencode" = "no"; then
    if test "$use_qr" = "yes"; then
      AC_MSG_ERROR([QR support requested but cannot be built. Use --without-qrencode])
    fi
    use_qr=no
  else
    if test "$use_qr" != "no"; then
      AC_DEFINE([USE_QRCODE], [1], [Define if QR support should be compiled in])
      use_qr=yes
    fi
  fi
  AC_MSG_RESULT([$use_qr])

  if test "$XGETTEXT" = ""; then
    AC_MSG_WARN([xgettext is required to update qt translations])
  fi

  AC_MSG_CHECKING([whether to build test_BGL-qt])
  if test "$use_gui_tests$BGL_enable_qt_test" = "yesyes"; then
    AC_MSG_RESULT([yes])
    BUILD_TEST_QT="yes"
  else
    AC_MSG_RESULT([no])
  fi
fi

AM_CONDITIONAL([ENABLE_ZMQ], [test "$use_zmq" = "yes"])

AC_MSG_CHECKING([whether to build test_BGL])
if test "$use_tests" = "yes"; then
  if test "$enable_fuzz" = "yes"; then
    AC_MSG_RESULT([no, because fuzzing is enabled])
  else
    AC_MSG_RESULT([yes])
  fi
  BUILD_TEST="yes"
else
  AC_MSG_RESULT([no])
  BUILD_TEST=""
fi

AC_MSG_CHECKING([whether to reduce exports])
if test "$use_reduce_exports" = "yes"; then
  AC_MSG_RESULT([yes])
else
  AC_MSG_RESULT([no])
fi

if test "$build_BGL_wallet$build_BGL_cli$build_BGL_tx$build_BGL_libs$build_BGLd$BGL_enable_qt$use_bench$use_tests" = "nononononononono"; then
  AC_MSG_ERROR([No targets! Please specify at least one of: --with-utils --with-libs --with-daemon --with-gui --enable-bench or --enable-tests])
fi

if test "$enable_fuzz_binary" = "yes"; then
  CHECK_RUNTIME_LIB
fi

AM_CONDITIONAL([TARGET_DARWIN], [test "$TARGET_OS" = "darwin"])
AM_CONDITIONAL([BUILD_DARWIN], [test "$BUILD_OS" = "darwin"])
AM_CONDITIONAL([TARGET_LINUX], [test "$TARGET_OS" = "linux"])
AM_CONDITIONAL([TARGET_WINDOWS], [test "$TARGET_OS" = "windows"])
AM_CONDITIONAL([ENABLE_WALLET], [test "$enable_wallet" = "yes"])
AM_CONDITIONAL([USE_SQLITE], [test "$use_sqlite" = "yes"])
AM_CONDITIONAL([USE_BDB], [test "$use_bdb" = "yes"])
AM_CONDITIONAL([ENABLE_TESTS], [test "$BUILD_TEST" = "yes"])
AM_CONDITIONAL([ENABLE_FUZZ], [test "$enable_fuzz" = "yes"])
AM_CONDITIONAL([ENABLE_FUZZ_BINARY], [test "$enable_fuzz_binary" = "yes"])
AM_CONDITIONAL([ENABLE_QT], [test "$BGL_enable_qt" = "yes"])
AM_CONDITIONAL([ENABLE_QT_TESTS], [test "$BUILD_TEST_QT" = "yes"])
AM_CONDITIONAL([ENABLE_BENCH], [test "$use_bench" = "yes"])
AM_CONDITIONAL([USE_QRCODE], [test "$use_qr" = "yes"])
AM_CONDITIONAL([USE_LCOV], [test "$use_lcov" = "yes"])
AM_CONDITIONAL([USE_LIBEVENT], [test "$use_libevent" = "yes"])
AM_CONDITIONAL([HARDEN], [test "$use_hardening" = "yes"])
AM_CONDITIONAL([ENABLE_SSE42], [test "$enable_sse42" = "yes"])
AM_CONDITIONAL([ENABLE_SSE41], [test "$enable_sse41" = "yes"])
AM_CONDITIONAL([ENABLE_AVX2], [test "$enable_avx2" = "yes"])
AM_CONDITIONAL([ENABLE_SHANI], [test "$enable_shani" = "yes"])
AM_CONDITIONAL([ENABLE_ARM_CRC], [test "$enable_arm_crc" = "yes"])
AM_CONDITIONAL([USE_ASM], [test "$use_asm" = "yes"])
AM_CONDITIONAL([WORDS_BIGENDIAN], [test "$ac_cv_c_bigendian" = "yes"])
AM_CONDITIONAL([USE_NATPMP], [test "$use_natpmp" = "yes"])
AM_CONDITIONAL([USE_UPNP], [test "$use_upnp" = "yes"])

dnl for minisketch
AM_CONDITIONAL([ENABLE_CLMUL], [test "$enable_clmul" = "yes"])
AM_CONDITIONAL([HAVE_CLZ], [test "$have_clzl$have_clzll" = "yesyes"])

AC_DEFINE([CLIENT_VERSION_MAJOR], [_CLIENT_VERSION_MAJOR], [Major version])
AC_DEFINE([CLIENT_VERSION_MINOR], [_CLIENT_VERSION_MINOR], [Minor version])
AC_DEFINE([CLIENT_VERSION_BUILD], [_CLIENT_VERSION_BUILD], [Version Build])
AC_DEFINE([CLIENT_VERSION_IS_RELEASE], [_CLIENT_VERSION_IS_RELEASE], [Version is release])
AC_DEFINE([COPYRIGHT_YEAR], [_COPYRIGHT_YEAR], [Copyright year])
AC_DEFINE([COPYRIGHT_HOLDERS], ["_COPYRIGHT_HOLDERS"], [Copyright holder(s) before %s replacement])
AC_DEFINE([COPYRIGHT_HOLDERS_SUBSTITUTION], ["_COPYRIGHT_HOLDERS_SUBSTITUTION"], [Replacement for %s in copyright holders string])
define(_COPYRIGHT_HOLDERS_FINAL, [patsubst(_COPYRIGHT_HOLDERS, [%s], [_COPYRIGHT_HOLDERS_SUBSTITUTION])])
AC_DEFINE([COPYRIGHT_HOLDERS_FINAL], ["_COPYRIGHT_HOLDERS_FINAL"], [Copyright holder(s)])
AC_SUBST(CLIENT_VERSION_MAJOR, _CLIENT_VERSION_MAJOR)
AC_SUBST(CLIENT_VERSION_MINOR, _CLIENT_VERSION_MINOR)
AC_SUBST(CLIENT_VERSION_BUILD, _CLIENT_VERSION_BUILD)
AC_SUBST(CLIENT_VERSION_IS_RELEASE, _CLIENT_VERSION_IS_RELEASE)
AC_SUBST(COPYRIGHT_YEAR, _COPYRIGHT_YEAR)
AC_SUBST(COPYRIGHT_HOLDERS, "_COPYRIGHT_HOLDERS")
AC_SUBST(COPYRIGHT_HOLDERS_SUBSTITUTION, "_COPYRIGHT_HOLDERS_SUBSTITUTION")
AC_SUBST(COPYRIGHT_HOLDERS_FINAL, "_COPYRIGHT_HOLDERS_FINAL")
AC_SUBST(BGL_DAEMON_NAME)
AC_SUBST(BGL_GUI_NAME)
AC_SUBST(BGL_CLI_NAME)
AC_SUBST(BGL_TX_NAME)
AC_SUBST(BGL_UTIL_NAME)
AC_SUBST(BGL_WALLET_TOOL_NAME)
AC_SUBST(BGL_MP_NODE_NAME)
AC_SUBST(BGL_MP_GUI_NAME)

AC_SUBST(RELDFLAGS)
AC_SUBST(DEBUG_CPPFLAGS)
AC_SUBST(WARN_CXXFLAGS)
AC_SUBST(NOWARN_CXXFLAGS)
AC_SUBST(DEBUG_CXXFLAGS)
AC_SUBST(ERROR_CXXFLAGS)
AC_SUBST(GPROF_CXXFLAGS)
AC_SUBST(GPROF_LDFLAGS)
AC_SUBST(HARDENED_CXXFLAGS)
AC_SUBST(HARDENED_CPPFLAGS)
AC_SUBST(HARDENED_LDFLAGS)
AC_SUBST(LTO_CXXFLAGS)
AC_SUBST(LTO_LDFLAGS)
AC_SUBST(PIC_FLAGS)
AC_SUBST(PIE_FLAGS)
AC_SUBST(SANITIZER_CXXFLAGS)
AC_SUBST(SANITIZER_LDFLAGS)
AC_SUBST(SSE42_CXXFLAGS)
AC_SUBST(SSE41_CXXFLAGS)
AC_SUBST(CLMUL_CXXFLAGS)
AC_SUBST(AVX2_CXXFLAGS)
AC_SUBST(SHANI_CXXFLAGS)
AC_SUBST(ARM_CRC_CXXFLAGS)
AC_SUBST(LIBTOOL_APP_LDFLAGS)
AC_SUBST(USE_SQLITE)
AC_SUBST(USE_BDB)
AC_SUBST(ENABLE_EXTERNAL_SIGNER)
AC_SUBST(USE_UPNP)
AC_SUBST(USE_QRCODE)
AC_SUBST(BOOST_LIBS)
AC_SUBST(TESTDEFS)
AC_SUBST(MINIUPNPC_CPPFLAGS)
AC_SUBST(MINIUPNPC_LIBS)
AC_SUBST(NATPMP_CPPFLAGS)
AC_SUBST(NATPMP_LIBS)
AC_SUBST(HAVE_GMTIME_R)
AC_SUBST(HAVE_FDATASYNC)
AC_SUBST(HAVE_FULLFSYNC)
AC_SUBST(HAVE_O_CLOEXEC)
AC_SUBST(HAVE_BUILTIN_PREFETCH)
AC_SUBST(HAVE_MM_PREFETCH)
AC_SUBST(HAVE_STRONG_GETAUXVAL)
AC_SUBST(ANDROID_ARCH)
AC_CONFIG_FILES([Makefile src/Makefile doc/man/Makefile share/setup.nsi share/qt/Info.plist test/config.ini])
AC_CONFIG_FILES([contrib/devtools/split-debug.sh],[chmod +x contrib/devtools/split-debug.sh])
AM_COND_IF([HAVE_DOXYGEN], [AC_CONFIG_FILES([doc/Doxyfile])])
AC_CONFIG_LINKS([contrib/devtools/security-check.py:contrib/devtools/security-check.py])
AC_CONFIG_LINKS([contrib/devtools/symbol-check.py:contrib/devtools/symbol-check.py])
AC_CONFIG_LINKS([contrib/devtools/test-security-check.py:contrib/devtools/test-security-check.py])
AC_CONFIG_LINKS([contrib/devtools/test-symbol-check.py:contrib/devtools/test-symbol-check.py])
AC_CONFIG_LINKS([contrib/filter-lcov.py:contrib/filter-lcov.py])
AC_CONFIG_LINKS([contrib/macdeploy/background.tiff:contrib/macdeploy/background.tiff])
AC_CONFIG_LINKS([test/functional/test_runner.py:test/functional/test_runner.py])
AC_CONFIG_LINKS([test/fuzz/test_runner.py:test/fuzz/test_runner.py])
AC_CONFIG_LINKS([test/util/test_runner.py:test/util/test_runner.py])
AC_CONFIG_LINKS([test/util/rpcauth-test.py:test/util/rpcauth-test.py])

dnl boost's m4 checks do something really nasty: they export these vars. As a
dnl result, they leak into secp256k1's configure and crazy things happen.
dnl Until this is fixed upstream and we've synced, we'll just un-export them.
CPPFLAGS_TEMP="$CPPFLAGS"
unset CPPFLAGS
CPPFLAGS="$CPPFLAGS_TEMP"

LDFLAGS_TEMP="$LDFLAGS"
unset LDFLAGS
LDFLAGS="$LDFLAGS_TEMP"

LIBS_TEMP="$LIBS"
unset LIBS
LIBS="$LIBS_TEMP"

PKGCONFIG_PATH_TEMP="$PKG_CONFIG_PATH"
unset PKG_CONFIG_PATH
PKG_CONFIG_PATH="$PKGCONFIG_PATH_TEMP"

PKGCONFIG_LIBDIR_TEMP="$PKG_CONFIG_LIBDIR"
unset PKG_CONFIG_LIBDIR
PKG_CONFIG_LIBDIR="$PKGCONFIG_LIBDIR_TEMP"

ac_configure_args="${ac_configure_args} --disable-shared --with-pic --enable-benchmark=no --enable-module-recovery --enable-module-schnorrsig --enable-experimental"
AC_CONFIG_SUBDIRS([src/secp256k1])

AC_OUTPUT

dnl Replace the BUILDDIR path with the correct Windows path if compiling on Native Windows
case ${OS} in
   *Windows*)
     sed  's/BUILDDIR="\/\([[a-z]]\)/BUILDDIR="\1:/'  test/config.ini > test/config-2.ini
     mv test/config-2.ini test/config.ini
   ;;
esac

echo
echo "Build Options:"
echo "  with external callbacks = $use_external_default_callbacks"
echo "  with benchmarks         = $use_benchmark"
echo "  with tests              = $use_tests"
echo "  with coverage           = $enable_coverage"
echo "  module ecdh             = $enable_module_ecdh"
echo "  module recovery         = $enable_module_recovery"
echo "  module extrakeys        = $enable_module_extrakeys"
echo "  module schnorrsig       = $enable_module_schnorrsig"
echo
echo "  asm                     = $set_asm"
echo "  ecmult window size      = $set_ecmult_window"
echo "  ecmult gen prec. bits   = $set_ecmult_gen_precision"
# Hide test-only options unless they're used.
if test x"$set_widemul" != xauto; then
echo "  wide multiplication     = $set_widemul"
fi
echo "  with gui / qt   = $BGL_enable_qt"
if test $BGL_enable_qt != "no"; then
    echo "    with qr       = $use_qr"
fi
echo "  with zmq        = $use_zmq"
if test $enable_fuzz = "no"; then
    echo "  with test       = $use_tests"
else
    echo "  with test       = not building test_BGL because fuzzing is enabled"
    echo "    with fuzz     = $enable_fuzz"
fi
echo "  with bench      = $use_bench"
echo "  with upnp       = $use_upnp"
echo "  with natpmp     = $use_natpmp"
echo "  use asm         = $use_asm"
echo "  USDT tracing    = $use_usdt"
echo "  sanitizers      = $use_sanitizers"
echo "  debug enabled   = $enable_debug"
echo "  gprof enabled   = $enable_gprof"
echo "  werror          = $enable_werror"
echo "  LTO             = $enable_lto"
echo
echo "  target os       = $host_os"
echo "  build os        = $build_os"
echo
echo "  CC              = $CC"
echo "  CFLAGS          = $PTHREAD_CFLAGS $CFLAGS"
echo "  CPPFLAGS        = $DEBUG_CPPFLAGS $HARDENED_CPPFLAGS $CPPFLAGS"
echo "  CXX             = $CXX"
echo "  CXXFLAGS        = $LTO_CXXFLAGS $DEBUG_CXXFLAGS $HARDENED_CXXFLAGS $WARN_CXXFLAGS $NOWARN_CXXFLAGS $ERROR_CXXFLAGS $GPROF_CXXFLAGS $CXXFLAGS"
echo "  LDFLAGS         = $LTO_LDFLAGS $PTHREAD_LIBS $HARDENED_LDFLAGS $GPROF_LDFLAGS $LDFLAGS"
echo "  ARFLAGS         = $ARFLAGS"
echo
