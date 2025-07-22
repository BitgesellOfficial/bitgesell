cmake_minimum_required(VERSION 3.22)

#=============================
# Project / Package metadata
#=============================
project(libsecp256k1
  # The package (a.k.a. release) version is based on semantic versioning 2.0.0 of
  # the API. All changes in experimental modules are treated as
  # backwards-compatible and therefore at most increase the minor version.
  VERSION 0.7.1
  DESCRIPTION "Optimized C library for ECDSA signatures and secret/public key operations on curve secp256k1."
  HOMEPAGE_URL "https://github.com/bitcoin-core/secp256k1"
  LANGUAGES C
)
enable_testing()
include(CTestUseLaunchers) # Allow users to set CTEST_USE_LAUNCHERS in custom `ctest -S` scripts.
list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

# The library version is based on libtool versioning of the ABI. The set of
# rules for updating the version can be found here:
# https://www.gnu.org/software/libtool/manual/html_node/Updating-version-info.html
# All changes in experimental modules are treated as if they don't affect the
# interface and therefore only increase the revision.
set(${PROJECT_NAME}_LIB_VERSION_CURRENT 6)
set(${PROJECT_NAME}_LIB_VERSION_REVISION 1)
set(${PROJECT_NAME}_LIB_VERSION_AGE 0)

#=============================
# Language setup
#=============================
if(CMAKE_SYSTEM_NAME STREQUAL "Darwin" AND NOT CMAKE_HOST_APPLE)
  # We do not use the install_name_tool when cross-compiling for macOS.
  # So disable this tool check in further enable_language() commands.
  set(CMAKE_PLATFORM_HAS_INSTALLNAME FALSE)
endif()
enable_language(CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake/module)
include(ProcessConfigurations)

# Flatten static lib dependencies.
# Without this, if libfoo.a depends on libbar.a, libfoo's objects can't begin
# to be compiled until libbar.a has been created.
if (NOT DEFINED CMAKE_OPTIMIZE_DEPENDENCIES)
  set(CMAKE_OPTIMIZE_DEPENDENCIES TRUE)
endif()

#=============================
# Configurable options
#=============================
include(CMakeDependentOption)
# When adding a new option, end the <help_text> with a full stop for consistency.
option(BUILD_BGL_BIN "Build BGL executable." ON)
option(BUILD_DAEMON "Build BGLd executable." ON)
option(BUILD_GUI "Build BGL-qt executable." OFF)
option(BUILD_CLI "Build BGL-cli executable." ON)

option(BUILD_TESTS "Build test_BGL executable." ON)
option(BUILD_TX "Build BGL-tx executable." ${BUILD_TESTS})
option(BUILD_UTIL "Build BGL-util executable." ${BUILD_TESTS})

option(SECP256K1_ENABLE_API_VISIBILITY_ATTRIBUTES "Enable visibility attributes in the API." ON)

## Modules

# We declare all options before processing them, to make sure we can express
# dependencies while processing.
option(SECP256K1_ENABLE_MODULE_ECDH "Enable ECDH module." ON)
option(SECP256K1_ENABLE_MODULE_RECOVERY "Enable ECDSA pubkey recovery module." OFF)
option(SECP256K1_ENABLE_MODULE_EXTRAKEYS "Enable extrakeys module." ON)
option(SECP256K1_ENABLE_MODULE_SCHNORRSIG "Enable schnorrsig module." ON)
option(SECP256K1_ENABLE_MODULE_MUSIG "Enable musig module." ON)
option(SECP256K1_ENABLE_MODULE_ELLSWIFT "Enable ElligatorSwift module." ON)

option(SECP256K1_USE_EXTERNAL_DEFAULT_CALLBACKS "Enable external default callback functions." OFF)
if(SECP256K1_USE_EXTERNAL_DEFAULT_CALLBACKS)
  add_compile_definitions(USE_EXTERNAL_DEFAULT_CALLBACKS=1)
endif()

set(SECP256K1_ECMULT_WINDOW_SIZE 15 CACHE STRING "Window size for ecmult precomputation for verification, specified as integer in range [2..24]. The default value is a reasonable setting for desktop machines (currently 15). [default=15]")
set_property(CACHE SECP256K1_ECMULT_WINDOW_SIZE PROPERTY STRINGS 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24)
include(CheckStringOptionValue)
check_string_option_value(SECP256K1_ECMULT_WINDOW_SIZE)
add_compile_definitions(ECMULT_WINDOW_SIZE=${SECP256K1_ECMULT_WINDOW_SIZE})

set(SECP256K1_ECMULT_GEN_KB 86 CACHE STRING "The size of the precomputed table for signing in multiples of 1024 bytes (on typical platforms). Larger values result in possibly better signing or key generation performance at the cost of a larger table. Valid choices are 2, 22, 86. The default value is a reasonable setting for desktop machines (currently 86). [default=86]")
set_property(CACHE SECP256K1_ECMULT_GEN_KB PROPERTY STRINGS 2 22 86)
check_string_option_value(SECP256K1_ECMULT_GEN_KB)
if(SECP256K1_ECMULT_GEN_KB EQUAL 2)
  add_compile_definitions(COMB_BLOCKS=2)
  add_compile_definitions(COMB_TEETH=5)
elseif(SECP256K1_ECMULT_GEN_KB EQUAL 22)
  add_compile_definitions(COMB_BLOCKS=11)
  add_compile_definitions(COMB_TEETH=6)
elseif(SECP256K1_ECMULT_GEN_KB EQUAL 86)
  add_compile_definitions(COMB_BLOCKS=43)
  add_compile_definitions(COMB_TEETH=6)
endif()

set(SECP256K1_TEST_OVERRIDE_WIDE_MULTIPLY "OFF" CACHE STRING "Test-only override of the (autodetected by the C code) \"widemul\" setting. Legal values are: \"OFF\", \"int128_struct\", \"int128\" or \"int64\". [default=OFF]")
set_property(CACHE SECP256K1_TEST_OVERRIDE_WIDE_MULTIPLY PROPERTY STRINGS "OFF" "int128_struct" "int128" "int64")
check_string_option_value(SECP256K1_TEST_OVERRIDE_WIDE_MULTIPLY)
if(SECP256K1_TEST_OVERRIDE_WIDE_MULTIPLY)
  string(TOUPPER "${SECP256K1_TEST_OVERRIDE_WIDE_MULTIPLY}" widemul_upper_value)
  add_compile_definitions(USE_FORCE_WIDEMUL_${widemul_upper_value}=1)
endif()
mark_as_advanced(FORCE SECP256K1_TEST_OVERRIDE_WIDE_MULTIPLY)

set(SECP256K1_ASM "AUTO" CACHE STRING "Assembly to use: \"AUTO\", \"OFF\", \"x86_64\" or \"arm32\" (experimental). [default=AUTO]")
set_property(CACHE SECP256K1_ASM PROPERTY STRINGS "AUTO" "OFF" "x86_64" "arm32")
check_string_option_value(SECP256K1_ASM)
if(SECP256K1_ASM STREQUAL "arm32")
  enable_language(ASM)
  include(CheckArm32Assembly)
  check_arm32_assembly()
  if(HAVE_ARM32_ASM)
    add_compile_definitions(USE_EXTERNAL_ASM=1)
  else()
    find_package(SQLite3 3.7.17 REQUIRED)
  endif()
endif()
cmake_dependent_option(BUILD_WALLET_TOOL "Build BGL-wallet tool." ${BUILD_TESTS} "ENABLE_WALLET" OFF)

option(ENABLE_HARDENING "Attempt to harden the resulting executables." ON)
option(REDUCE_EXPORTS "Attempt to reduce exported symbols in the resulting executables." OFF)
option(WERROR "Treat compiler warnings as errors." OFF)
option(WITH_CCACHE "Attempt to use ccache for compiling." ON)

option(WITH_ZMQ "Enable ZMQ notifications." OFF)
if(WITH_ZMQ)
  find_package(ZeroMQ 4.0.0 MODULE REQUIRED)
endif()

option(WITH_USDT "Enable tracepoints for Userspace, Statically Defined Tracing." OFF)
if(WITH_USDT)
  find_package(USDT MODULE REQUIRED)
endif()

option(ENABLE_EXTERNAL_SIGNER "Enable external signer support." ON)

cmake_dependent_option(WITH_QRENCODE "Enable QR code support." ON "BUILD_GUI" OFF)
if(WITH_QRENCODE)
  find_package(QRencode MODULE REQUIRED)
  set(USE_QRCODE TRUE)
endif()

cmake_dependent_option(WITH_DBUS "Enable DBus support." ON "NOT CMAKE_SYSTEM_NAME MATCHES \"(Windows|Darwin)\" AND BUILD_GUI" OFF)

option(ENABLE_IPC "Build multiprocess BGL-node and BGL-gui executables in addition to monolithic BGLd and BGL-qt executables. Requires libmultiprocess library. Experimental." OFF)
cmake_dependent_option(WITH_EXTERNAL_LIBMULTIPROCESS "Build with external libmultiprocess library instead of with local git subtree when ENABLE_IPC is enabled. This is not normally recommended, but can be useful for developing libmultiprocess itself." OFF "ENABLE_IPC" OFF)
if(ENABLE_IPC AND WITH_EXTERNAL_LIBMULTIPROCESS)
  find_package(Libmultiprocess REQUIRED COMPONENTS Lib)
  find_package(LibmultiprocessNative REQUIRED COMPONENTS Bin
    NAMES Libmultiprocess
  )
endif()

cmake_dependent_option(BUILD_GUI_TESTS "Build test_BGL-qt executable." ON "BUILD_GUI;BUILD_TESTS" OFF)
if(BUILD_GUI)
  set(qt_components Core Gui Widgets LinguistTools)
  if(ENABLE_WALLET)
    list(APPEND qt_components Network)
  endif()
  if(WITH_DBUS)
    list(APPEND qt_components DBus)
    set(USE_DBUS TRUE)
  endif()
  if(BUILD_GUI_TESTS)
    list(APPEND qt_components Test)
  endif()
  find_package(Qt 6.2 MODULE REQUIRED
    COMPONENTS ${qt_components}
  )
  unset(qt_components)
endif()

option(BUILD_BENCH "Build bench_BGL executable." OFF)
option(BUILD_FUZZ_BINARY "Build fuzz binary." OFF)
option(BUILD_FOR_FUZZING "Build for fuzzing. Enabling this will disable all other targets and override BUILD_FUZZ_BINARY." OFF)

option(INSTALL_MAN "Install man pages." ON)

set(APPEND_CPPFLAGS "" CACHE STRING "Preprocessor flags that are appended to the command line after all other flags added by the build system. This variable is intended for debugging and special builds.")
set(APPEND_CFLAGS "" CACHE STRING "C compiler flags that are appended to the command line after all other flags added by the build system. This variable is intended for debugging and special builds.")
set(APPEND_CXXFLAGS "" CACHE STRING "(Objective) C++ compiler flags that are appended to the command line after all other flags added by the build system. This variable is intended for debugging and special builds.")
set(APPEND_LDFLAGS "" CACHE STRING "Linker flags that are appended to the command line after all other flags added by the build system. This variable is intended for debugging and special builds.")
# Appending to this low-level rule variables is the only way to
# guarantee that the flags appear at the end of the command line.
string(APPEND CMAKE_CXX_COMPILE_OBJECT " ${APPEND_CPPFLAGS} ${APPEND_CXXFLAGS}")
string(APPEND CMAKE_CXX_CREATE_SHARED_LIBRARY " ${APPEND_LDFLAGS}")
string(APPEND CMAKE_CXX_LINK_EXECUTABLE " ${APPEND_LDFLAGS}")

set(configure_warnings)

include(CheckLinkerSupportsPIE)
check_linker_supports_pie(configure_warnings)

# The core_interface library aims to encapsulate common build flags.
# It is a usage requirement for all targets except for secp256k1, which
# gets its flags by other means.
add_library(core_interface INTERFACE)
add_library(core_interface_relwithdebinfo INTERFACE)
add_library(core_interface_debug INTERFACE)
target_link_libraries(core_interface INTERFACE
  $<$<CONFIG:RelWithDebInfo>:core_interface_relwithdebinfo>
  $<$<CONFIG:Debug>:core_interface_debug>
)

if(BUILD_FOR_FUZZING)
  message(WARNING "BUILD_FOR_FUZZING=ON will disable all other targets and force BUILD_FUZZ_BINARY=ON.")
  set(BUILD_BGL_BIN OFF)
  set(BUILD_DAEMON OFF)
  set(BUILD_CLI OFF)
  set(BUILD_TX OFF)
  set(BUILD_UTIL OFF)
  set(BUILD_UTIL_CHAINSTATE OFF)
  set(BUILD_KERNEL_LIB OFF)
  set(BUILD_WALLET_TOOL OFF)
  set(BUILD_GUI OFF)
  set(ENABLE_EXTERNAL_SIGNER OFF)
  set(WITH_ZMQ OFF)
  set(BUILD_TESTS OFF)
  set(BUILD_GUI_TESTS OFF)
  set(BUILD_BENCH OFF)
  set(BUILD_FUZZ_BINARY ON)

  target_compile_definitions(core_interface INTERFACE
    FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION
  )
endif()

include(TryAppendCXXFlags)
include(TryAppendLinkerFlag)

# Redefine/adjust per-configuration flags.
target_compile_definitions(core_interface_debug INTERFACE
  DEBUG
  DEBUG_LOCKORDER
  DEBUG_LOCKCONTENTION
  RPC_DOC_CHECK
  ABORT_ON_FAILED_ASSUME
)

if(WIN32)
  #[=[
  This build system supports two ways to build binaries for Windows.

  1. Building on Windows using MSVC.
  Implementation notes:
  - /DWIN32 and /D_WINDOWS definitions are included into the CMAKE_CXX_FLAGS_INIT
    and CMAKE_CXX_FLAGS_INIT variables by default.
  - A run-time library is selected using the CMAKE_MSVC_RUNTIME_LIBRARY variable.
  - MSVC-specific options, for example, /Zc:__cplusplus, are additionally required.

  2. Cross-compiling using MinGW.
  Implementation notes:
  - WIN32 and _WINDOWS definitions must be provided explicitly.
  - A run-time library must be specified explicitly using _MT definition.
  ]=]

  target_compile_definitions(core_interface INTERFACE
    _WIN32_WINNT=0x0A00
    _WIN32_IE=0x0A00
    WIN32_LEAN_AND_MEAN
    NOMINMAX
  )

  if(MSVC)
    if(VCPKG_TARGET_TRIPLET MATCHES "-static")
      set(msvc_library_linkage "")
    else()
      set(msvc_library_linkage "DLL")
    endif()
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>${msvc_library_linkage}")
    unset(msvc_library_linkage)

    target_compile_definitions(core_interface INTERFACE
      _UNICODE;UNICODE
    )
    target_compile_options(core_interface INTERFACE
      /utf-8
      /Zc:preprocessor
      /Zc:__cplusplus
      /sdl
    )
    target_link_options(core_interface INTERFACE
      # We embed our own manifests.
      /MANIFEST:NO
    )
    # Improve parallelism in MSBuild.
    # See: https://devblogs.microsoft.com/cppblog/improved-parallelism-in-msbuild/.
    list(APPEND CMAKE_VS_GLOBALS "UseMultiToolTask=true")
  endif()

  if(MINGW)
    target_compile_definitions(core_interface INTERFACE
      WIN32
      _WINDOWS
      _MT
    )
    # Avoid the use of aligned vector instructions when building for Windows.
    # See https://gcc.gnu.org/bugzilla/show_bug.cgi?id=54412.
    try_append_cxx_flags("-Wa,-muse-unaligned-vector-move" TARGET core_interface SKIP_LINK)
    try_append_linker_flag("-static" TARGET core_interface)
    # We support Windows 10+, however it's not possible to set these values accordingly,
    # due to a bug in mingw-w64. See https://sourceforge.net/p/mingw-w64/bugs/968/.
    # As a best effort, target Windows 8.
    try_append_linker_flag("-Wl,--major-subsystem-version,6" TARGET core_interface)
    try_append_linker_flag("-Wl,--minor-subsystem-version,2" TARGET core_interface)
  endif()

  # Workaround producing large object files, which cannot be handled by the assembler.
  # More likely to happen with no, or lower levels of optimisation.
  # See discussion in https://github.com/bitcoin/bitcoin/issues/28109.
  if(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    try_append_cxx_flags("/bigobj" TARGET core_interface_debug SKIP_LINK)
  else()
    try_append_cxx_flags("-Wa,-mbig-obj" TARGET core_interface_debug SKIP_LINK)
  endif()
endif()

include(TryAppendCFlags)
if(MSVC)
  # For both cl and clang-cl compilers.
  try_append_c_flags(/W3) # Production quality warning level.
  # Eliminate deprecation warnings for the older, less secure functions.
  add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
else()
  try_append_cxx_flags("-Wall" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wextra" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wgnu" TARGET warn_interface SKIP_LINK)
  # Some compilers will ignore -Wformat-security without -Wformat, so just combine the two here.
  try_append_cxx_flags("-Wformat -Wformat-security" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wvla" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wshadow-field" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wthread-safety" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wthread-safety-pointer" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wloop-analysis" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wredundant-decls" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wunused-member-function" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wdate-time" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wconditional-uninitialized" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wduplicated-branches" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wduplicated-cond" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wlogical-op" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Woverloaded-virtual" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wsuggest-override" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wimplicit-fallthrough" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wunreachable-code" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wdocumentation" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wself-assign" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wbidi-chars=any" TARGET warn_interface SKIP_LINK)
  try_append_cxx_flags("-Wundef" TARGET warn_interface SKIP_LINK)

  # Some compilers (gcc) ignore unknown -Wno-* options, but warn about all
  # unknown options if any other warning is produced. Test the -Wfoo case, and
  # set the -Wno-foo case if it works.
  try_append_cxx_flags("-Wunused-parameter" TARGET warn_interface SKIP_LINK
    IF_CHECK_PASSED "-Wno-unused-parameter"
  )
endif()

configure_file(cmake/script/Coverage.cmake Coverage.cmake USE_SOURCE_PERMISSIONS COPYONLY)
configure_file(cmake/script/CoverageFuzz.cmake CoverageFuzz.cmake USE_SOURCE_PERMISSIONS COPYONLY)
configure_file(cmake/script/CoverageInclude.cmake.in CoverageInclude.cmake USE_SOURCE_PERMISSIONS @ONLY)
configure_file(cmake/script/cov_tool_wrapper.sh.in cov_tool_wrapper.sh.in USE_SOURCE_PERMISSIONS COPYONLY)
configure_file(contrib/filter-lcov.py filter-lcov.py USE_SOURCE_PERMISSIONS COPYONLY)

# Don't allow extended (non-ASCII) symbols in identifiers. This is easier for code review.
try_append_cxx_flags("-fno-extended-identifiers" TARGET core_interface SKIP_LINK)

# Avoiding the `-ffile-prefix-map` compiler option because it implies
# `-fcoverage-prefix-map` on Clang or `-fprofile-prefix-map` on GCC,
# which can cause issues with coverage builds, particularly when using
# Clang in the OSS-Fuzz environment due to its use of other options
# and a third party script, or with GCC.
try_append_cxx_flags("-fdebug-prefix-map=A=B" TARGET core_interface SKIP_LINK
  IF_CHECK_PASSED "-fdebug-prefix-map=${PROJECT_SOURCE_DIR}/src=."
)
try_append_cxx_flags("-fmacro-prefix-map=A=B" TARGET core_interface SKIP_LINK
  IF_CHECK_PASSED "-fmacro-prefix-map=${PROJECT_SOURCE_DIR}/src=."
)

# Currently all versions of gcc are subject to a class of bugs, see the
# gccbug_90348 test case (only reproduces on GCC 11 and earlier) and
# https://gcc.gnu.org/bugzilla/show_bug.cgi?id=111843. To work around that, set
# -fstack-reuse=none for all gcc builds. (Only gcc understands this flag).
try_append_cxx_flags("-fstack-reuse=none" TARGET core_interface)

if(MSVC)
  try_append_linker_flag("/DYNAMICBASE" TARGET core_interface)
  try_append_linker_flag("/HIGHENTROPYVA" TARGET core_interface)
  try_append_linker_flag("/NXCOMPAT" TARGET core_interface)
else()
  # Keep the following commands ordered lexicographically.
  try_append_c_flags(-pedantic)
  try_append_c_flags(-Wcast-align) # GCC >= 2.95.
  try_append_c_flags(-Wcast-align=strict) # GCC >= 8.0.
  try_append_c_flags(-Wconditional-uninitialized) # Clang >= 3.0 only.
  try_append_c_flags(-Wextra) # GCC >= 3.4, this is the newer name of -W, which we don't use because older GCCs will warn about unused functions.
  try_append_c_flags(-Wnested-externs)
  try_append_c_flags(-Wno-long-long) # GCC >= 3.0, -Wlong-long is implied by -pedantic.
  try_append_c_flags(-Wno-overlength-strings) # GCC >= 4.2, -Woverlength-strings is implied by -pedantic.
  try_append_c_flags(-Wno-unused-function) # GCC >= 3.0, -Wunused-function is implied by -Wall.
  try_append_c_flags(-Wreserved-identifier) # Clang >= 13.0 only.
  try_append_c_flags(-Wshadow)
  try_append_c_flags(-Wstrict-prototypes)
  try_append_c_flags(-Wundef)
endif()

set(print_msan_notice)
if(SECP256K1_BUILD_CTIME_TESTS)
  include(CheckMemorySanitizer)
  check_memory_sanitizer(msan_enabled)
  if(msan_enabled)
    try_append_c_flags(-fno-sanitize-memory-param-retval)
    set(print_msan_notice YES)
  endif()
  try_append_cxx_flags(${werror_flag} TARGET core_interface SKIP_LINK RESULT_VAR compiler_supports_werror)
  if(NOT compiler_supports_werror)
    message(FATAL_ERROR "WERROR set but ${werror_flag} is not usable.")
  endif()
  unset(werror_flag)
endif()

# Prefer Unix-style package components over frameworks on macOS.
# This improves compatibility with Python version managers.
set(Python3_FIND_FRAMEWORK LAST CACHE STRING "")
# Search for generic names before more specialized ones. This
# improves compatibility with Python version managers that use shims.
set(Python3_FIND_UNVERSIONED_NAMES FIRST CACHE STRING "")
mark_as_advanced(Python3_FIND_FRAMEWORK Python3_FIND_UNVERSIONED_NAMES)
find_package(Python3 3.10 COMPONENTS Interpreter)
if(NOT TARGET Python3::Interpreter)
  list(APPEND configure_warnings
    "Minimum required Python not found."
  )
endif()

target_compile_definitions(core_interface INTERFACE ${DEPENDS_COMPILE_DEFINITIONS})
target_compile_definitions(core_interface_relwithdebinfo INTERFACE ${DEPENDS_COMPILE_DEFINITIONS_RELWITHDEBINFO})
target_compile_definitions(core_interface_debug INTERFACE ${DEPENDS_COMPILE_DEFINITIONS_DEBUG})

# If the {CXX,LD}FLAGS environment variables are defined during building depends
# and configuring this build system, their content might be duplicated.
if(DEFINED ENV{CXXFLAGS})
  deduplicate_flags(CMAKE_CXX_FLAGS)
endif()
if(DEFINED ENV{LDFLAGS})
  deduplicate_flags(CMAKE_EXE_LINKER_FLAGS)
endif()

if(BUILD_TESTS)
  enable_testing()
endif()

if(CMAKE_VERSION VERSION_GREATER_EQUAL 3.29)
  # have "make test" depend on "make all"
  set(CMAKE_SKIP_TEST_ALL_DEPENDENCY FALSE)
endif()

# TODO: The `CMAKE_SKIP_BUILD_RPATH` variable setting can be deleted
#       in the future after reordering Guix script commands to
#       perform binary checks after the installation step.
# Relevant discussions:
# - https://github.com/hebasto/bitcoin/pull/236#issuecomment-2183120953
# - https://github.com/bitcoin/bitcoin/pull/30312#issuecomment-2191235833
# NetBSD always requires runtime paths to be set for executables.
if(CMAKE_SYSTEM_NAME STREQUAL "NetBSD")
  set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
else()
  set(CMAKE_SKIP_BUILD_RPATH TRUE)
  set(CMAKE_SKIP_INSTALL_RPATH TRUE)
endif()
add_subdirectory(test)
add_subdirectory(doc)

add_subdirectory(src)

include(Maintenance)
setup_split_debug_script()
add_maintenance_targets()
add_windows_deploy_target()
add_macos_deploy_target()

message("\n")
message("Configure summary")
message("=================")
message("Executables:")
message("  BGL ............................. ${BUILD_BGL_BIN}")
message("  BGLd ............................ ${BUILD_DAEMON}")
if(BUILD_DAEMON AND ENABLE_IPC)
  set(BGL_daemon_status ON)
else()
  set(BGL_daemon_status OFF)
endif()
message("  BGL-node (multiprocess) ......... ${BGL_daemon_status}")
message("  BGL-qt (GUI) .................... ${BUILD_GUI}")
if(BUILD_GUI AND ENABLE_IPC)
  set(BGL_gui_status ON)
else()
  set(BGL_gui_status OFF)
endif()
message("  BGL-gui (GUI, multiprocess) ..... ${BGL_gui_status}")
message("  BGL-cli ......................... ${BUILD_CLI}")
message("  BGL-tx .......................... ${BUILD_TX}")
message("  BGL-util ........................ ${BUILD_UTIL}")
message("  BGL-wallet ...................... ${BUILD_WALLET_TOOL}")
message("  BGL-chainstate (experimental) ... ${BUILD_UTIL_CHAINSTATE}")
message("  libBGLkernel (experimental) ..... ${BUILD_KERNEL_LIB}")
message("Optional features:")
message("  wallet support ...................... ${ENABLE_WALLET}")
message("  external signer ..................... ${ENABLE_EXTERNAL_SIGNER}")
message("  ZeroMQ .............................. ${WITH_ZMQ}")
if(ENABLE_IPC)
  if (WITH_EXTERNAL_LIBMULTIPROCESS)
    set(ipc_status "ON (with external libmultiprocess)")
  else()
    set(ipc_status ON)
  endif()
else()
  set(ipc_status OFF)
endif()
message("  IPC ................................. ${ipc_status}")
message("  USDT tracing ........................ ${WITH_USDT}")
message("  QR code (GUI) ....................... ${WITH_QRENCODE}")
message("  DBus (GUI) .......................... ${WITH_DBUS}")
message("Tests:")
message("  test_BGL ........................ ${BUILD_TESTS}")
message("  test_BGL-qt ..................... ${BUILD_GUI_TESTS}")
message("  bench_BGL ....................... ${BUILD_BENCH}")
message("  fuzz binary ......................... ${BUILD_FUZZ_BINARY}")
message("")
if(CMAKE_CROSSCOMPILING)
  set(cross_status "TRUE, for ${CMAKE_SYSTEM_NAME}, ${CMAKE_SYSTEM_PROCESSOR}")
else()
  set(cross_status "FALSE")
endif()
message("Cross compiling ....................... ${cross_status}")
message("API visibility attributes ............. ${SECP256K1_ENABLE_API_VISIBILITY_ATTRIBUTES}")
message("Valgrind .............................. ${SECP256K1_VALGRIND}")
get_directory_property(definitions COMPILE_DEFINITIONS)
string(REPLACE ";" " " definitions "${definitions}")
message("Preprocessor defined macros ........... ${definitions}")
message("C compiler ............................ ${CMAKE_C_COMPILER_ID} ${CMAKE_C_COMPILER_VERSION}, ${CMAKE_C_COMPILER}")
message("CFLAGS ................................ ${CMAKE_C_FLAGS}")
get_directory_property(compile_options COMPILE_OPTIONS)
string(REPLACE ";" " " compile_options "${compile_options}")
message("Compile options ....................... " ${compile_options})
if(NOT is_multi_config)
  message("Build type:")
  message(" - CMAKE_BUILD_TYPE ................... ${CMAKE_BUILD_TYPE}")
  string(TOUPPER "${CMAKE_BUILD_TYPE}" build_type)
  message(" - CFLAGS ............................. ${CMAKE_C_FLAGS_${build_type}}")
  message(" - LDFLAGS for executables ............ ${CMAKE_EXE_LINKER_FLAGS_${build_type}}")
  message(" - LDFLAGS for shared libraries ....... ${CMAKE_SHARED_LINKER_FLAGS_${build_type}}")
else()
  message("Supported configurations .............. ${CMAKE_CONFIGURATION_TYPES}")
  message("RelWithDebInfo configuration:")
  message(" - CFLAGS ............................. ${CMAKE_C_FLAGS_RELWITHDEBINFO}")
  message(" - LDFLAGS for executables ............ ${CMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO}")
  message(" - LDFLAGS for shared libraries ....... ${CMAKE_SHARED_LINKER_FLAGS_RELWITHDEBINFO}")
  message("Debug configuration:")
  message(" - CFLAGS ............................. ${CMAKE_C_FLAGS_DEBUG}")
  message(" - LDFLAGS for executables ............ ${CMAKE_EXE_LINKER_FLAGS_DEBUG}")
  message(" - LDFLAGS for shared libraries ....... ${CMAKE_SHARED_LINKER_FLAGS_DEBUG}")
endif()
if(SECP256K1_APPEND_CFLAGS)
  message("SECP256K1_APPEND_CFLAGS ............... ${SECP256K1_APPEND_CFLAGS}")
endif()
if(SECP256K1_APPEND_LDFLAGS)
  message("SECP256K1_APPEND_LDFLAGS .............. ${SECP256K1_APPEND_LDFLAGS}")
endif()
message("")
if(print_msan_notice)
  message(
    "Note:\n"
    "  MemorySanitizer detected, tried to add -fno-sanitize-memory-param-retval to compile options\n"
    "  to avoid false positives in ctime_tests. Pass -DSECP256K1_BUILD_CTIME_TESTS=OFF to avoid this.\n"
  )
endif()
if(SECP256K1_EXPERIMENTAL)
  message(
    "  ******\n"
    "  WARNING: experimental build\n"
    "  Experimental features do not have stable APIs or properties, and may not be safe for production use.\n"
    "  ******\n"
  )
endif()

# We want all build properties to be encapsulated properly.
include(WarnAboutGlobalProperties)
