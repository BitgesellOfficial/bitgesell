AC_PREREQ([2.60])

# The package (a.k.a. release) version is based on semantic versioning 2.0.0 of
# the API. All changes in experimental modules are treated as
# backwards-compatible and therefore at most increase the minor version.
define(_PKG_VERSION_MAJOR, 0)
define(_PKG_VERSION_MINOR, 1)
define(_PKG_VERSION_BUILD, 0)
define(_PKG_VERSION_IS_RELEASE, false)

# The library version is based on libtool versioning of the ABI. The set of
# rules for updating the version can be found here:
# https://www.gnu.org/software/libtool/manual/html_node/Updating-version-info.html
# All changes in experimental modules are treated as if they don't affect the
# interface and therefore only increase the revision.
define(_LIB_VERSION_CURRENT, 0)
define(_LIB_VERSION_REVISION, 0)
define(_LIB_VERSION_AGE, 0)

AC_INIT([libsecp256k1],m4_join([.], _PKG_VERSION_MAJOR, _PKG_VERSION_MINOR, _PKG_VERSION_BUILD)m4_if(_PKG_VERSION_IS_RELEASE, [true], [], [-pre]),[https://github.com/bitcoin-core/secp256k1/issues],[libsecp256k1],[https://github.com/bitcoin-core/secp256k1])

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
BGL_CHAINSTATE_NAME=BGL-chainstate
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
AH_TOP([#ifndef LIBSECP256K1_CONFIG_H])
AH_TOP([#define LIBSECP256K1_CONFIG_H])
AH_BOTTOM([#endif /*LIBSECP256K1_CONFIG_H*/])

# Require Automake 1.11.2 for AM_PROG_AR
AM_INIT_AUTOMAKE([1.11.2 foreign subdir-objects])

# Make the compilation flags quiet unless V=1 is used.
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])

AC_PROG_CC
if test x"$ac_cv_prog_cc_c89" = x"no"; then
  AC_MSG_ERROR([c89 compiler support required])
fi
AM_PROG_AS
AM_PROG_AR

LT_INIT([win32-dll])

build_windows=no

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
   cygwin*|mingw*)
     build_windows=yes
   ;;
esac

AC_ARG_WITH([seccomp],
  [AS_HELP_STRING([--with-seccomp],
  [enable experimental syscall sandbox feature (-sandbox), default is yes if seccomp-bpf is detected under Linux x86_64])],
  [seccomp_found=$withval],
  [seccomp_found=auto])

AC_ARG_ENABLE([c++20],
  [AS_HELP_STRING([--enable-c++20],
  [enable compilation in c++20 mode (disabled by default)])],
  [use_cxx20=$enableval],
  [use_cxx20=no])

dnl Require C++17 compiler (no GNU extensions)
if test "$use_cxx20" = "no"; then
AX_CXX_COMPILE_STDCXX([17], [noext], [mandatory])
else
AX_CXX_COMPILE_STDCXX([20], [noext], [mandatory])
fi

dnl Check if -latomic is required for <std::atomic>
CHECK_ATOMIC

dnl check if additional link flags are required for std::filesystem
CHECK_FILESYSTEM

dnl Unless the user specified OBJCXX, force it to be the same as CXX. This ensures
dnl that we get the same -std flags for both.
m4_ifdef([AC_PROG_OBJCXX],[
if test "${OBJCXX+set}" = ""; then
  OBJCXX="${CXX}"
fi
AC_PROG_OBJCXX
])

dnl OpenBSD ships with 2.4.2
LT_PREREQ([2.4.2])
dnl Libtool init checks.
LT_INIT([pic-only win32-dll])

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

# In dev mode, we enable all binaries and modules by default but individual options can still be overridden explicitly.
# Check for dev mode first because SECP_SET_DEFAULT needs enable_dev_mode set.
AC_ARG_ENABLE(dev_mode, [], [],
    [enable_dev_mode=no])

AC_ARG_ENABLE(benchmark,
    AS_HELP_STRING([--enable-benchmark],[compile benchmark [default=yes]]), [],
    [SECP_SET_DEFAULT([enable_benchmark], [yes], [yes])])

AC_ARG_ENABLE(coverage,
    AS_HELP_STRING([--enable-coverage],[enable compiler flags to support kcov coverage analysis [default=no]]), [],
    [SECP_SET_DEFAULT([enable_coverage], [no], [no])])

if test "$enable_debug" = "yes"; then
  dnl If debugging is enabled, and the user hasn't overridden CXXFLAGS, clear
  dnl them, to prevent autoconfs "-g -O2" being added. Otherwise we'd end up
  dnl with "-O0 -g3 -g -O2".
  if test "$CXXFLAGS_overridden" = "no"; then
  CXXFLAGS=""
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
AX_CHECK_COMPILE_FLAG([-fno-extended-identifiers], [CORE_CXXFLAGS="$CORE_CXXFLAGS -fno-extended-identifiers"], [], [$CXXFLAG_WERROR])

enable_sse42=no
enable_sse41=no
enable_avx2=no
enable_x86_shani=no

if test "$use_asm" = "yes"; then

dnl Check for optional instruction set support. Enabling these does _not_ imply that all code will
dnl be compiled with them, rather that specific objects/libs may use them after checking for runtime
dnl compatibility.

dnl x86
AX_CHECK_COMPILE_FLAG([-msse4.2], [SSE42_CXXFLAGS="-msse4.2"], [], [$CXXFLAG_WERROR])
AX_CHECK_COMPILE_FLAG([-msse4.1], [SSE41_CXXFLAGS="-msse4.1"], [], [$CXXFLAG_WERROR])
AX_CHECK_COMPILE_FLAG([-mavx -mavx2], [AVX2_CXXFLAGS="-mavx -mavx2"], [], [$CXXFLAG_WERROR])
AX_CHECK_COMPILE_FLAG([-msse4 -msha], [X86_SHANI_CXXFLAGS="-msse4 -msha"], [], [$CXXFLAG_WERROR])

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
CXXFLAGS="$CXXFLAGS $X86_SHANI_CXXFLAGS"
AC_MSG_CHECKING([for x86 SHA-NI intrinsics])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[
    #include <stdint.h>
    #include <immintrin.h>
  ]],[[
    __m128i i = _mm_set1_epi32(0);
    __m128i j = _mm_set1_epi32(1);
    __m128i k = _mm_set1_epi32(2);
    return _mm_extract_epi32(_mm_sha256rnds2_epu32(i, i, k), 0);
  ]])],
 [ AC_MSG_RESULT([yes]); enable_x86_shani=yes; AC_DEFINE([ENABLE_X86_SHANI], [1], [Define this symbol to build code that uses x86 SHA-NI intrinsics]) ],
 [ AC_MSG_RESULT([no])]
)
CXXFLAGS="$TEMP_CXXFLAGS"

# ARM
AX_CHECK_COMPILE_FLAG([-march=armv8-a+crc+crypto], [ARM_CRC_CXXFLAGS="-march=armv8-a+crc+crypto"], [], [$CXXFLAG_WERROR])
AX_CHECK_COMPILE_FLAG([-march=armv8-a+crc+crypto], [ARM_SHANI_CXXFLAGS="-march=armv8-a+crc+crypto"], [], [$CXXFLAG_WERROR])

TEMP_CXXFLAGS="$CXXFLAGS"
CXXFLAGS="$CXXFLAGS $ARM_CRC_CXXFLAGS"
AC_MSG_CHECKING([for ARMv8 CRC32 intrinsics])
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

TEMP_CXXFLAGS="$CXXFLAGS"
CXXFLAGS="$CXXFLAGS $ARM_SHANI_CXXFLAGS"
AC_MSG_CHECKING([for ARMv8 SHA-NI intrinsics])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[
    #include <arm_acle.h>
    #include <arm_neon.h>
  ]],[[
    uint32x4_t a, b, c;
    vsha256h2q_u32(a, b, c);
    vsha256hq_u32(a, b, c);
    vsha256su0q_u32(a, b);
    vsha256su1q_u32(a, b, c);
  ]])],
 [ AC_MSG_RESULT([yes]); enable_arm_shani=yes; AC_DEFINE([ENABLE_ARM_SHANI], [1], [Define this symbol to build code that uses ARMv8 SHA-NI intrinsics]) ],
 [ AC_MSG_RESULT([no])]
)
CXXFLAGS="$TEMP_CXXFLAGS"

fi

CORE_CPPFLAGS="$CORE_CPPFLAGS -DHAVE_BUILD_INFO"

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

AC_ARG_ENABLE([experimental-util-chainstate],
  [AS_HELP_STRING([--enable-experimental-util-chainstate],
  [build experimental BGL-chainstate executable (default=no)])],
  [build_BGL_chainstate=$enableval],
  [build_BGL_chainstate=no])

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

     CORE_CPPFLAGS="$CORE_CPPFLAGS -D_MT -DWIN32 -D_WINDOWS -D_WIN32_WINNT=0x0601 -D_WIN32_IE=0x0501 -DWIN32_LEAN_AND_MEAN"

     dnl libtool insists upon adding -nostdlib and a list of objects/libs to link against.
     dnl That breaks our ability to build dll's with static libgcc/libstdc++/libssp. Override
     dnl its command here, with the predeps/postdeps removed, and -static inserted. Postdeps are
     dnl also overridden to prevent their insertion later.
     dnl This should only affect dll's.
     archive_cmds_CXX="\$CC -shared \$libobjs \$deplibs \$compiler_flags -static -o \$output_objdir/\$soname \${wl}--enable-auto-image-base -Xlinker --out-implib -Xlinker \$lib"
     postdeps_CXX=

     dnl We require Windows 7 (NT 6.1) or later
     AX_CHECK_LINK_FLAG([-Wl,--major-subsystem-version -Wl,6 -Wl,--minor-subsystem-version -Wl,1], [CORE_LDFLAGS="$CORE_LDFLAGS -Wl,--major-subsystem-version -Wl,6 -Wl,--minor-subsystem-version -Wl,1"], [], [$LDFLAG_WERROR])
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
                 CORE_CPPFLAGS="$CORE_CPPFLAGS -isystem $miniupnpc_prefix/include"
               else
                 CORE_CPPFLAGS="$CORE_CPPFLAGS -I$miniupnpc_prefix/include"
               fi
               CORE_LDFLAGS="$CORE_LDFLAGS -L$miniupnpc_prefix/lib"
             fi
             if test "$use_natpmp" != "no" && $BREW list --versions libnatpmp >/dev/null; then
               libnatpmp_prefix=$($BREW --prefix libnatpmp 2>/dev/null)
               if test "$suppress_external_warnings" != "no"; then
                 CORE_CPPFLAGS="$CORE_CPPFLAGS -isystem $libnatpmp_prefix/include"
               else
                 CORE_CPPFLAGS="$CORE_CPPFLAGS -I$libnatpmp_prefix/include"
               fi
               CORE_LDFLAGS="$CORE_LDFLAGS -L$libnatpmp_prefix/lib"
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

     AX_CHECK_LINK_FLAG([-Wl,-headerpad_max_install_names], [CORE_LDFLAGS="$CORE_LDFLAGS -Wl,-headerpad_max_install_names"], [], [$LDFLAG_WERROR])
     CORE_CPPFLAGS="$CORE_CPPFLAGS -DMAC_OSX -DOBJC_OLD_DISPATCH_PROTOTYPES=0"
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

  AX_CHECK_LINK_FLAG([--coverage], [CORE_LDFLAGS="$CORE_LDFLAGS --coverage"],
    [AC_MSG_ERROR([lcov testing requested but --coverage linker flag does not work])])
  AX_CHECK_COMPILE_FLAG([--coverage],[CORE_CXXFLAGS="$CORE_CXXFLAGS --coverage"],
    [AC_MSG_ERROR([lcov testing requested but --coverage flag does not work])])
  dnl If coverage is enabled, and the user hasn't overridden CXXFLAGS, clear
  dnl them, to prevent autoconfs "-g -O2" being added. Otherwise we'd end up
  dnl with "--coverage -Og -O0 -g -O2".
  if test "$CXXFLAGS_overridden" = "no"; then
  CXXFLAGS=""
  fi
  CORE_CXXFLAGS="$CORE_CXXFLAGS -Og -O0"
fi

if test "$use_lcov_branch" != "no"; then
  AC_SUBST(LCOV_OPTS, "$LCOV_OPTS --rc lcov_branch_coverage=1")
fi

dnl Check for endianness
AC_C_BIGENDIAN

dnl Check for pthread compile/link requirements
AX_PTHREAD

dnl The following macro will add the necessary defines to BGL-config.h, but
dnl they also need to be passed down to any subprojects. Pull the results out of
dnl the cache and add them to CPPFLAGS.
AC_SYS_LARGEFILE
dnl detect POSIX or GNU variant of strerror_r
AC_FUNC_STRERROR_R

if test "$ac_cv_sys_file_offset_bits" != "" &&
   test "$ac_cv_sys_file_offset_bits" != "no" &&
   test "$ac_cv_sys_file_offset_bits" != "unknown"; then
  CORE_CPPFLAGS="$CORE_CPPFLAGS -D_FILE_OFFSET_BITS=$ac_cv_sys_file_offset_bits"
fi

if test "$ac_cv_sys_large_files" != "" &&
   test "$ac_cv_sys_large_files" != "no" &&
   test "$ac_cv_sys_large_files" != "unknown"; then
  CORE_CPPFLAGS="$CORE_CPPFLAGS -D_LARGE_FILES=$ac_cv_sys_large_files"
fi

AC_SEARCH_LIBS([clock_gettime],[rt])

if test "$enable_gprof" = "yes"; then
    dnl -pg is incompatible with -pie. Since hardening and profiling together doesn't make sense,
    dnl we simply make them mutually exclusive here. Additionally, hardened toolchains may force
    dnl -pie by default, in which case it needs to be turned off with -no-pie.

    if test "$use_hardening" = "yes"; then
        AC_MSG_ERROR([gprof profiling is not compatible with hardening. Reconfigure with --disable-hardening or --disable-gprof])
    fi
    use_hardening=no
    AX_CHECK_COMPILE_FLAG([-pg],[GPROF_CXXFLAGS="-pg"],
        [AC_MSG_ERROR([gprof profiling requested but not available])], [$CXXFLAG_WERROR])

    AX_CHECK_LINK_FLAG([-no-pie], [GPROF_LDFLAGS="-no-pie"])
    AX_CHECK_LINK_FLAG([-pg], [GPROF_LDFLAGS="$GPROF_LDFLAGS -pg"],
        [AC_MSG_ERROR([gprof profiling requested but not available])], [$GPROF_LDFLAGS])
fi

if test "$TARGET_OS" != "windows"; then
  dnl All windows code is PIC, forcing it on just adds useless compile warnings
  AX_CHECK_COMPILE_FLAG([-fPIC], [PIC_FLAGS="-fPIC"])
fi

dnl All versions of gcc that we commonly use for building are subject to bug
dnl https://gcc.gnu.org/bugzilla/show_bug.cgi?id=90348. To work around that, set
dnl -fstack-reuse=none for all gcc builds. (Only gcc understands this flag)
AX_CHECK_COMPILE_FLAG([-fstack-reuse=none], [HARDENED_CXXFLAGS="$HARDENED_CXXFLAGS -fstack-reuse=none"])
if test "$use_hardening" != "no"; then
  use_hardening=yes
  AX_CHECK_COMPILE_FLAG([-Wstack-protector], [HARDENED_CXXFLAGS="$HARDENED_CXXFLAGS -Wstack-protector"])
  AX_CHECK_COMPILE_FLAG([-fstack-protector-all], [HARDENED_CXXFLAGS="$HARDENED_CXXFLAGS -fstack-protector-all"])

  dnl -fcf-protection used with Clang 7 causes ld to emit warnings:
  dnl ld: error: ... <corrupt x86 feature size: 0x8>
  dnl Use CHECK_LINK_FLAG & --fatal-warnings to ensure we won't use the flag in this case.
  AX_CHECK_LINK_FLAG([-fcf-protection=full], [HARDENED_CXXFLAGS="$HARDENED_CXXFLAGS -fcf-protection=full"], [], [$LDFLAG_WERROR])

  case $host in
    *mingw*)
      dnl stack-clash-protection doesn't currently work, and likely should just be skipped for Windows.
      dnl See https://gcc.gnu.org/bugzilla/show_bug.cgi?id=90458 for more details.
      ;;
    *)
      AX_CHECK_COMPILE_FLAG([-fstack-clash-protection], [HARDENED_CXXFLAGS="$HARDENED_CXXFLAGS -fstack-clash-protection"], [], [$CXXFLAG_WERROR])
      ;;
  esac


  dnl When enable_debug is yes, all optimizations are disabled.
  dnl However, FORTIFY_SOURCE requires that there is some level of optimization, otherwise it does nothing and just creates a compiler warning.
  dnl Since FORTIFY_SOURCE is a no-op without optimizations, do not enable it when enable_debug is yes.
  if test "$enable_debug" != "yes"; then
    AX_CHECK_PREPROC_FLAG([-D_FORTIFY_SOURCE=2],[
      AX_CHECK_PREPROC_FLAG([-U_FORTIFY_SOURCE],[
        HARDENED_CPPFLAGS="$HARDENED_CPPFLAGS -U_FORTIFY_SOURCE"
      ])
      HARDENED_CPPFLAGS="$HARDENED_CPPFLAGS -D_FORTIFY_SOURCE=2"
    ])
  fi

  AX_CHECK_LINK_FLAG([-Wl,--enable-reloc-section], [HARDENED_LDFLAGS="$HARDENED_LDFLAGS -Wl,--enable-reloc-section"], [], [$LDFLAG_WERROR])
  AX_CHECK_LINK_FLAG([-Wl,--dynamicbase], [HARDENED_LDFLAGS="$HARDENED_LDFLAGS -Wl,--dynamicbase"], [], [$LDFLAG_WERROR])
  AX_CHECK_LINK_FLAG([-Wl,--nxcompat], [HARDENED_LDFLAGS="$HARDENED_LDFLAGS -Wl,--nxcompat"], [], [$LDFLAG_WERROR])
  AX_CHECK_LINK_FLAG([-Wl,--high-entropy-va], [HARDENED_LDFLAGS="$HARDENED_LDFLAGS -Wl,--high-entropy-va"], [], [$LDFLAG_WERROR])
  AX_CHECK_LINK_FLAG([-Wl,-z,relro], [HARDENED_LDFLAGS="$HARDENED_LDFLAGS -Wl,-z,relro"], [], [$LDFLAG_WERROR])
  AX_CHECK_LINK_FLAG([-Wl,-z,now], [HARDENED_LDFLAGS="$HARDENED_LDFLAGS -Wl,-z,now"], [], [$LDFLAG_WERROR])
  AX_CHECK_LINK_FLAG([-Wl,-z,separate-code], [HARDENED_LDFLAGS="$HARDENED_LDFLAGS -Wl,-z,separate-code"], [], [$LDFLAG_WERROR])
  AX_CHECK_LINK_FLAG([-fPIE -pie], [PIE_FLAGS="-fPIE"; HARDENED_LDFLAGS="$HARDENED_LDFLAGS -pie"], [], [$CXXFLAG_WERROR])

  case $host in
    *mingw*)
       AC_CHECK_LIB([ssp], [main], [], [AC_MSG_ERROR([libssp missing])])
    ;;
  esac
fi

# Select assembly optimization
enable_external_asm=no

case $set_asm in
x86_64)
  AC_DEFINE(USE_ASM_X86_64, 1, [Define this symbol to enable x86_64 assembly optimizations])
  ;;
arm)
  enable_external_asm=yes
  ;;
no)
  ;;
*)
  AC_MSG_ERROR([invalid assembly optimizations])
  ;;
esac

if test x"$enable_external_asm" = x"yes"; then
  AC_DEFINE(USE_EXTERNAL_ASM, 1, [Define this symbol if an external (non-inline) assembly implementation is used])
fi

dnl check for gmtime_r(), fallback to gmtime_s() if that is unavailable
dnl fail if neither are available.
AC_MSG_CHECKING([for gmtime_r])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[#include <ctime>]],
  [[ gmtime_r((const time_t *) nullptr, (struct tm *) nullptr); ]])],
  [ AC_MSG_RESULT([yes]); AC_DEFINE([HAVE_GMTIME_R], [1], [Define this symbol if gmtime_r is available]) ],
  [ AC_MSG_RESULT([no]);
    AC_MSG_CHECKING([for gmtime_s]);
    AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[#include <ctime>]],
       [[ gmtime_s((struct tm *) nullptr, (const time_t *) nullptr); ]])],
       [ AC_MSG_RESULT([yes])],
       [ AC_MSG_RESULT([no]); AC_MSG_ERROR([Both gmtime_r and gmtime_s are unavailable]) ]
    )
  ]
)

dnl Check for different ways of gathering OS randomness
AC_MSG_CHECKING([for Linux getrandom syscall])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[#include <unistd.h>
  #include <sys/syscall.h>
  #include <linux/random.h>]],
 [[ syscall(SYS_getrandom, nullptr, 32, 0); ]])],
 [ AC_MSG_RESULT([yes]); AC_DEFINE([HAVE_SYS_GETRANDOM], [1], [Define this symbol if the Linux getrandom system call is available]) ],
 [ AC_MSG_RESULT([no])]
)

AC_MSG_CHECKING([for getentropy via random.h])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[#include <unistd.h>
 #include <sys/random.h>]],
 [[ getentropy(nullptr, 32) ]])],
 [ AC_MSG_RESULT([yes]); AC_DEFINE([HAVE_GETENTROPY_RAND], [1], [Define this symbol if the BSD getentropy system call is available with sys/random.h]) ],
 [ AC_MSG_RESULT([no])]
)

AC_MSG_CHECKING([for sysctl])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[#include <sys/types.h>
  #include <sys/sysctl.h>]],
 [[ #ifdef __linux__
    #error "Don't use sysctl on Linux, it's deprecated even when it works"
    #endif
    sysctl(nullptr, 2, nullptr, nullptr, nullptr, 0); ]])],
 [ AC_MSG_RESULT([yes]); AC_DEFINE([HAVE_SYSCTL], [1], [Define this symbol if the BSD sysctl() is available]) ],
 [ AC_MSG_RESULT([no])]
)

AC_MSG_CHECKING([for sysctl KERN_ARND])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[#include <sys/types.h>
  #include <sys/sysctl.h>]],
 [[ #ifdef __linux__
    #error "Don't use sysctl on Linux, it's deprecated even when it works"
    #endif
    static int name[2] = {CTL_KERN, KERN_ARND};
    sysctl(name, 2, nullptr, nullptr, nullptr, 0); ]])],
 [ AC_MSG_RESULT([yes]); AC_DEFINE([HAVE_SYSCTL_ARND], [1], [Define this symbol if the BSD sysctl(KERN_ARND) is available]) ],
 [ AC_MSG_RESULT([no])]
)

AC_MSG_CHECKING([for if type char equals int8_t])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[#include <stdint.h>
  #include <type_traits>]],
 [[ static_assert(std::is_same<int8_t, char>::value, ""); ]])],
 [ AC_MSG_RESULT([yes]); AC_DEFINE([CHAR_EQUALS_INT8], [1], [Define this symbol if type char equals int8_t]) ],
 [ AC_MSG_RESULT([no])]
)

AC_MSG_CHECKING([for fdatasync])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[#include <unistd.h>]],
 [[ fdatasync(0); ]])],
 [ AC_MSG_RESULT([yes]); HAVE_FDATASYNC=1 ],
 [ AC_MSG_RESULT([no]); HAVE_FDATASYNC=0 ]
)
AC_DEFINE_UNQUOTED([HAVE_FDATASYNC], [$HAVE_FDATASYNC], [Define to 1 if fdatasync is available.])

AC_MSG_CHECKING([for F_FULLFSYNC])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[#include <fcntl.h>]],
 [[ fcntl(0, F_FULLFSYNC, 0); ]])],
 [ AC_MSG_RESULT([yes]); HAVE_FULLFSYNC=1 ],
 [ AC_MSG_RESULT([no]); HAVE_FULLFSYNC=0 ]
)

AC_MSG_CHECKING([for O_CLOEXEC])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[#include <fcntl.h>]],
 [[ open("", O_CLOEXEC); ]])],
 [ AC_MSG_RESULT([yes]); HAVE_O_CLOEXEC=1 ],
 [ AC_MSG_RESULT([no]); HAVE_O_CLOEXEC=0 ]
)
AC_DEFINE_UNQUOTED([HAVE_O_CLOEXEC], [$HAVE_O_CLOEXEC], [Define to 1 if O_CLOEXEC flag is available.])

dnl crc32c platform checks
AC_MSG_CHECKING([for __builtin_prefetch])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[ ]], [[
  char data = 0;
  const char* address = &data;
  __builtin_prefetch(address, 0, 0);
  ]])],
 [ AC_MSG_RESULT([yes]); HAVE_BUILTIN_PREFETCH=1 ],
 [ AC_MSG_RESULT([no]); HAVE_BUILTIN_PREFETCH=0 ]
)

AC_MSG_CHECKING([for _mm_prefetch])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[#include <xmmintrin.h>]], [[
  char data = 0;
  const char* address = &data;
  _mm_prefetch(address, _MM_HINT_NTA);
  ]])],
 [ AC_MSG_RESULT([yes]); HAVE_MM_PREFETCH=1 ],
 [ AC_MSG_RESULT([no]); HAVE_MM_PREFETCH=0 ]
)

AC_MSG_CHECKING([for strong getauxval support in the system headers])
AC_COMPILE_IFELSE([AC_LANG_PROGRAM([[
    #include <sys/auxv.h>
  ]], [[
    getauxval(AT_HWCAP);
  ]])],
 [ AC_MSG_RESULT([yes]); HAVE_STRONG_GETAUXVAL=1; AC_DEFINE([HAVE_STRONG_GETAUXVAL], [1], [Define this symbol to build code that uses getauxval)]) ],
 [ AC_MSG_RESULT([no]); HAVE_STRONG_GETAUXVAL=0 ]
)

have_any_system=no
AC_MSG_CHECKING([for std::system])
AC_LINK_IFELSE(
    [ AC_LANG_PROGRAM(
        [[ #include <cstdlib> ]],
        [[ int nErr = std::system(""); ]]
    )],
    [ AC_MSG_RESULT([yes]); have_any_system=yes],
    [ AC_MSG_RESULT([no]) ]
)

AC_MSG_CHECKING([for ::_wsystem])
AC_LINK_IFELSE(
    [ AC_LANG_PROGRAM(
        [[ ]],
        [[ int nErr = ::_wsystem(""); ]]
    )],
    [ AC_MSG_RESULT([yes]); have_any_system=yes],
    [ AC_MSG_RESULT([no]) ]
)

if test "$have_any_system" != "no"; then
  AC_DEFINE([HAVE_SYSTEM], [1], [Define to 1 if std::system or ::wsystem is available.])
fi

dnl SUPPRESSED_CPPFLAGS=SUPPRESS_WARNINGS([$SOME_CPPFLAGS])
dnl Replace -I with -isystem in $SOME_CPPFLAGS to suppress warnings from
dnl headers from its include directories and return the result.
dnl See -isystem documentation:
dnl https://gcc.gnu.org/onlinedocs/gcc/Directory-Options.html
dnl https://clang.llvm.org/docs/ClangCommandLineReference.html#cmdoption-clang-isystem-directory
dnl Do not change "-I/usr/include" to "-isystem /usr/include" because that
dnl is not necessary (/usr/include is already a system directory) and because
dnl it would break GCC's #include_next.
AC_DEFUN([SUPPRESS_WARNINGS],
         [[$(echo $1 |${SED} -E -e 's/(^| )-I/\1-isystem /g' -e 's;-isystem /usr/include/*( |$);-I/usr/include\1;g')]])

dnl enable-fuzz should disable all other targets
if test "$enable_fuzz" = "yes"; then
  AC_MSG_WARN([enable-fuzz will disable all other targets and force --enable-fuzz-binary=yes])
  build_BGL_utils=no
  build_BGL_cli=no
  build_BGL_tx=no
  build_BGL_util=no
  build_BGL_chainstate=no
  build_BGL_wallet=no
  build_BGLd=no
  build_BGL_libs=no
  BGL_enable_qt=no
  BGL_enable_qt_test=no
  BGL_enable_qt_dbus=no
  use_bench=no
  use_external_signer=no
  use_upnp=no
  use_natpmp=no
  use_zmq=no
  enable_fuzz_binary=yes

  AX_CHECK_PREPROC_FLAG([-DABORT_ON_FAILED_ASSUME], [DEBUG_CPPFLAGS="$DEBUG_CPPFLAGS -DABORT_ON_FAILED_ASSUME"], [], [$CXXFLAG_WERROR])
else
  BGL_QT_INIT

  dnl sets $BGL_enable_qt, $BGL_enable_qt_test, $BGL_enable_qt_dbus
  BGL_QT_CONFIGURE([5.11.3])

  dnl Keep a copy of the original $QT_INCLUDES and use it when invoking qt's moc
  QT_INCLUDES_UNSUPPRESSED=$QT_INCLUDES
  if test "$suppress_external_warnings" != "no" ; then
    QT_INCLUDES=SUPPRESS_WARNINGS($QT_INCLUDES)
    QT_DBUS_INCLUDES=SUPPRESS_WARNINGS($QT_DBUS_INCLUDES)
    QT_TEST_INCLUDES=SUPPRESS_WARNINGS($QT_TEST_INCLUDES)
  fi
fi

if test "$enable_fuzz_binary" = "yes"; then
  AC_MSG_CHECKING([whether main function is needed for fuzz binary])
  AX_CHECK_LINK_FLAG(
    [],
    [AC_MSG_RESULT([no])],
    [AC_MSG_RESULT([yes]); CORE_CPPFLAGS="$CORE_CPPFLAGS -DPROVIDE_FUZZ_MAIN_FUNCTION"],
    [$SANITIZER_LDFLAGS],
    [AC_LANG_PROGRAM([[
      #include <cstdint>
      #include <cstddef>
      extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) { return 0; }
      /* comment to remove the main function ...
     ]],[[
      */ int not_main() {
     ]])])

  CHECK_RUNTIME_LIB
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
AM_CONDITIONAL([ENABLE_USDT_TRACEPOINTS], [test "$use_usdt" = "yes"])

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

  dnl we don't use multi_index serialization
  BOOST_CPPFLAGS="$BOOST_CPPFLAGS -DBOOST_MULTI_INDEX_DISABLE_SERIALIZATION"

  if test "$suppress_external_warnings" != "no"; then
    BOOST_CPPFLAGS=SUPPRESS_WARNINGS($BOOST_CPPFLAGS)
  fi
fi

if test "$use_external_signer" != "no"; then
  case $host in
    *mingw*)
      dnl Boost Process uses Boost Filesystem when targeting Windows. Also,
      dnl since Boost 1.71.0, Process does not work with mingw-w64 without
      dnl workarounds. See 67669ab425b52a2b6be3d2f3b3b7e3939b676a2c.
      if test "$use_external_signer" = "yes"; then
        AC_MSG_ERROR([External signing is not supported on Windows])
      fi
      use_external_signer="no";
    ;;
    *)
      AC_MSG_CHECKING([whether Boost.Process can be used])
      TEMP_CXXFLAGS="$CXXFLAGS"
      dnl Boost 1.78 requires the following workaround.
      dnl See: https://github.com/boostorg/process/issues/235
      CXXFLAGS="$CXXFLAGS -Wno-error=narrowing"
      TEMP_CPPFLAGS="$CPPFLAGS"
      CPPFLAGS="$CPPFLAGS $BOOST_CPPFLAGS"
      TEMP_LDFLAGS="$LDFLAGS"
      dnl Boost 1.73 and older require the following workaround.
      LDFLAGS="$LDFLAGS $PTHREAD_CFLAGS"
      AC_LINK_IFELSE([AC_LANG_PROGRAM([[#include <boost/process.hpp>]])],
        [have_boost_process="yes"],
        [have_boost_process="no"])
      LDFLAGS="$TEMP_LDFLAGS"
      CPPFLAGS="$TEMP_CPPFLAGS"
      CXXFLAGS="$TEMP_CXXFLAGS"
      AC_MSG_RESULT([$have_boost_process])
      if test "$have_boost_process" = "yes"; then
        use_external_signer="yes"
        AC_DEFINE([ENABLE_EXTERNAL_SIGNER], [1], [Define if external signer support is enabled])
      else
        if test "$use_external_signer" = "yes"; then
          AC_MSG_ERROR([External signing is not supported for this Boost version])
        fi
        use_external_signer="no";
      fi
    ;;
  esac
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
  AX_CHECK_COMPILE_FLAG([-fvisibility=hidden], [CORE_CXXFLAGS="$CORE_CXXFLAGS -fvisibility=hidden"],
  [AC_MSG_ERROR([Cannot set hidden symbol visibility. Use --disable-reduce-exports.])], [$CXXFLAG_WERROR])
  AX_CHECK_LINK_FLAG([-Wl,--exclude-libs,ALL], [RELDFLAGS="-Wl,--exclude-libs,ALL"], [], [$LDFLAG_WERROR])
fi

if test "$use_tests" = "yes"; then

  if test "$HEXDUMP" = ""; then
    AC_MSG_ERROR([hexdump is required for tests])
  fi
fi

dnl libevent check

if test "$build_BGL_cli$build_BGLd$BGL_enable_qt$use_tests$use_bench" != "nonononono"; then
  PKG_CHECK_MODULES([EVENT], [libevent >= 2.1.8], [use_libevent=yes], [AC_MSG_ERROR([libevent version 2.1.8 or greater not found.])])
  if test "$TARGET_OS" != "windows"; then
    PKG_CHECK_MODULES([EVENT_PTHREADS], [libevent_pthreads >= 2.1.8], [], [AC_MSG_ERROR([libevent_pthreads version 2.1.8 or greater not found.])])
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

if test x"$enable_external_default_callbacks" = x"yes"; then
  AC_DEFINE(USE_EXTERNAL_DEFAULT_CALLBACKS, 1, [Define this symbol if an external implementation of the default callbacks is used])
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

if test x"$enable_experimental" = x"yes"; then
  AC_MSG_NOTICE([******])
  AC_MSG_NOTICE([WARNING: experimental build])
  AC_MSG_NOTICE([Experimental features do not have stable APIs or properties, and may not be safe for production use.])
  AC_MSG_NOTICE([******])
else
  if test x"$set_asm" = x"arm"; then
    AC_MSG_ERROR([ARM assembly optimization is experimental. Use --enable-experimental to allow.])
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

###
### Generate output
###

AC_CONFIG_HEADERS([src/libsecp256k1-config.h])
AC_CONFIG_FILES([Makefile libsecp256k1.pc])
AC_SUBST(SECP_INCLUDES)
AC_SUBST(SECP_LIBS)
AC_SUBST(SECP_TEST_LIBS)
AC_SUBST(SECP_TEST_INCLUDES)
AC_SUBST(SECP_CFLAGS)
AM_CONDITIONAL([ENABLE_COVERAGE], [test x"$enable_coverage" = x"yes"])
AM_CONDITIONAL([USE_TESTS], [test x"$enable_tests" != x"no"])
AM_CONDITIONAL([USE_EXHAUSTIVE_TESTS], [test x"$enable_exhaustive_tests" != x"no"])
AM_CONDITIONAL([USE_EXAMPLES], [test x"$enable_examples" != x"no"])
AM_CONDITIONAL([USE_BENCHMARK], [test x"$enable_benchmark" = x"yes"])
AM_CONDITIONAL([ENABLE_MODULE_ECDH], [test x"$enable_module_ecdh" = x"yes"])
AM_CONDITIONAL([ENABLE_MODULE_RECOVERY], [test x"$enable_module_recovery" = x"yes"])
AM_CONDITIONAL([ENABLE_MODULE_EXTRAKEYS], [test x"$enable_module_extrakeys" = x"yes"])
AM_CONDITIONAL([ENABLE_MODULE_SCHNORRSIG], [test x"$enable_module_schnorrsig" = x"yes"])
AM_CONDITIONAL([USE_EXTERNAL_ASM], [test x"$enable_external_asm" = x"yes"])
AM_CONDITIONAL([USE_ASM_ARM], [test x"$set_asm" = x"arm"])
AM_CONDITIONAL([BUILD_WINDOWS], [test "$build_windows" = "yes"])
AC_SUBST(LIB_VERSION_CURRENT, _LIB_VERSION_CURRENT)
AC_SUBST(LIB_VERSION_REVISION, _LIB_VERSION_REVISION)
AC_SUBST(LIB_VERSION_AGE, _LIB_VERSION_AGE)

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
echo "  with external callbacks = $enable_external_default_callbacks"
echo "  with benchmarks         = $enable_benchmark"
echo "  with tests              = $enable_tests"
echo "  with coverage           = $enable_coverage"
echo "  with examples           = $enable_examples"
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
fi
echo "  with fuzz binary = $enable_fuzz_binary"
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
echo "  CPPFLAGS        = $DEBUG_CPPFLAGS $HARDENED_CPPFLAGS $CORE_CPPFLAGS $CPPFLAGS"
echo "  CXX             = $CXX"
echo "  CXXFLAGS        = $LTO_CXXFLAGS $DEBUG_CXXFLAGS $HARDENED_CXXFLAGS $WARN_CXXFLAGS $NOWARN_CXXFLAGS $ERROR_CXXFLAGS $GPROF_CXXFLAGS $CORE_CXXFLAGS $CXXFLAGS"
echo "  LDFLAGS         = $LTO_LDFLAGS $PTHREAD_LIBS $HARDENED_LDFLAGS $GPROF_LDFLAGS $CORE_LDFLAGS $LDFLAGS"
echo "  ARFLAGS         = $ARFLAGS"
echo
