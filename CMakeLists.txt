# Copyright (c) 2019 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

cmake_minimum_required(VERSION 3.12)

project("Libmultiprocess" CXX)
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  set(CMAKE_CXX_STANDARD 20)
  set(CMAKE_CXX_STANDARD_REQUIRED YES)
endif()

include("cmake/compat_find.cmake")

#=============================
# Project / Package metadata
#=============================
set(CLIENT_NAME "Bitgesell Core")
set(CLIENT_VERSION_MAJOR 29)
set(CLIENT_VERSION_MINOR 99)
set(CLIENT_VERSION_BUILD 0)
set(CLIENT_VERSION_RC 0)
set(CLIENT_VERSION_IS_RELEASE "false")
set(COPYRIGHT_YEAR "2025")

# During the enabling of the CXX and CXXOBJ languages, we modify
# CMake's compiler/linker invocation strings by appending the content
# of the user-defined `APPEND_*` variables, which allows overriding
# any flag. We also ensure that the APPEND_* flags are considered
# during CMake's tests, which use the `try_compile()` command.
#
# CMake's docs state that the `CMAKE_TRY_COMPILE_PLATFORM_VARIABLES`
# variable "is meant to be set by CMake's platform information modules
# for the current toolchain, or by a toolchain file." We do our best
# to set it before the `project()` command.
set(CMAKE_TRY_COMPILE_PLATFORM_VARIABLES
  CMAKE_CXX_COMPILE_OBJECT
  CMAKE_OBJCXX_COMPILE_OBJECT
  CMAKE_CXX_LINK_EXECUTABLE
)

project(BGLCore
  VERSION ${CLIENT_VERSION_MAJOR}.${CLIENT_VERSION_MINOR}.${CLIENT_VERSION_BUILD}
  DESCRIPTION "Bitgesell client software"
  HOMEPAGE_URL "https://bitcoincore.org/"
  LANGUAGES NONE
)

set(CLIENT_VERSION_STRING ${PROJECT_VERSION})
if(CLIENT_VERSION_RC GREATER 0)
  string(APPEND CLIENT_VERSION_STRING "rc${CLIENT_VERSION_RC}")
endif()

set(COPYRIGHT_HOLDERS "The %s developers")
set(COPYRIGHT_HOLDERS_FINAL "The ${CLIENT_NAME} developers")
set(CLIENT_BUGREPORT "https://github.com/bitcoin/bitcoin/issues")

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
option(BUILD_DAEMON "Build BGLd executable." ON)
option(BUILD_GUI "Build BGL-qt executable." OFF)
option(BUILD_CLI "Build BGL-cli executable." ON)

option(BUILD_TESTS "Build test_BGL executable." ON)
option(BUILD_TX "Build BGL-tx executable." ${BUILD_TESTS})
option(BUILD_UTIL "Build BGL-util executable." ${BUILD_TESTS})

option(BUILD_UTIL_CHAINSTATE "Build experimental BGL-chainstate executable." OFF)
option(BUILD_KERNEL_LIB "Build experimental BGLkernel library." ${BUILD_UTIL_CHAINSTATE})

option(ENABLE_WALLET "Enable wallet." ON)
if(ENABLE_WALLET)
  if(VCPKG_TARGET_TRIPLET)
    # Use of the `unofficial::` namespace is a vcpkg package manager convention.
    find_package(unofficial-sqlite3 CONFIG REQUIRED)
  else()
    find_package(SQLite3 3.7.17 REQUIRED)
  endif()
endif()
option(WITH_BDB "Enable Berkeley DB (BDB) wallet support." OFF)
cmake_dependent_option(WARN_INCOMPATIBLE_BDB "Warn when using a Berkeley DB (BDB) version other than 4.8." ON "WITH_BDB" OFF)
if(WITH_BDB)
  find_package(BerkeleyDB 4.8 MODULE REQUIRED)
  set(USE_BDB ON)
  if(NOT BerkeleyDB_VERSION VERSION_EQUAL 4.8)
    message(WARNING "Found Berkeley DB (BDB) other than 4.8.\n"
                    "BDB (legacy) wallets opened by this build will not be portable!"
    )
    if(WARN_INCOMPATIBLE_BDB)
      message(WARNING "If this is intended, pass \"-DWARN_INCOMPATIBLE_BDB=OFF\".\n"
                      "Passing \"-DWITH_BDB=OFF\" will suppress this warning."
      )
    endif()
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

cmake_dependent_option(WITH_DBUS "Enable DBus support." ON "CMAKE_SYSTEM_NAME STREQUAL \"Linux\" AND BUILD_GUI" OFF)

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

# Use 64-bit off_t on 32-bit Linux.
if (CMAKE_SYSTEM_NAME STREQUAL "Linux" AND CMAKE_SIZEOF_VOID_P EQUAL 4)
  # Ensure 64-bit offsets are used for filesystem accesses for 32-bit compilation.
  target_compile_definitions(core_interface INTERFACE
    _FILE_OFFSET_BITS=64
  )
endif()

if(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
  target_compile_definitions(core_interface INTERFACE OBJC_OLD_DISPATCH_PROTOTYPES=0)
  # These flags are specific to ld64, and may cause issues with other linkers.
  # For example: GNU ld will interpret -dead_strip as -de and then try and use
  # "ad_strip" as the symbol for the entry point.
  try_append_linker_flag("-Wl,-dead_strip" TARGET core_interface)
  try_append_linker_flag("-Wl,-dead_strip_dylibs" TARGET core_interface)
  if(CMAKE_HOST_APPLE)
    try_append_linker_flag("-Wl,-headerpad_max_install_names" TARGET core_interface)
  endif()
endif()

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

option(Libmultiprocess_ENABLE_CLANG_TIDY "Run clang-tidy with the compiler." OFF)
if(Libmultiprocess_ENABLE_CLANG_TIDY)
  find_program(CLANG_TIDY_EXECUTABLE NAMES clang-tidy)
  if(NOT CLANG_TIDY_EXECUTABLE)
    message(FATAL_ERROR "Libmultiprocess_ENABLE_CLANG_TIDY is ON but clang-tidy is not found.")
  endif()
  set(CMAKE_CXX_CLANG_TIDY "${CLANG_TIDY_EXECUTABLE}")
endif()

set(MPGEN_EXECUTABLE "" CACHE FILEPATH "If specified, should be full path to an external mpgen binary to use rather than the one built internally.")

include("cmake/compat_config.cmake")
include("cmake/pthread_checks.cmake")
include(GNUInstallDirs)

# Set MP_INCLUDE_DIR as a global property so target_capnp_sources function can
# use it, and its callers don't need to specify the include directory manually
# to avoid "error: Import failed: /mp/proxy.capnp" failures from capnproto.
set_property(GLOBAL PROPERTY MP_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")

# Set a convenience variable for subdirectories.
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  set(MP_STANDALONE TRUE)
  include(CTest)
else()
  set(MP_STANDALONE FALSE)
endif()

# Prevent include directories from parent project from leaking into this one.
set_property(DIRECTORY PROPERTY INCLUDE_DIRECTORIES "")

# Generated C++ preprocessor defines
configure_file(include/mp/config.h.in "${CMAKE_CURRENT_BINARY_DIR}/include/mp/config.h")

# Generated C++ Capn'Proto schema files
capnp_generate_cpp(MP_PROXY_SRCS MP_PROXY_HDRS include/mp/proxy.capnp)

# util library
add_library(mputil OBJECT src/mp/util.cpp)
target_include_directories(mputil PRIVATE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/include>)
target_link_libraries(mputil PUBLIC CapnProto::kj)

# libmultiprocess.a runtime library
set(MP_PUBLIC_HEADERS
  ${MP_PROXY_HDRS}
  include/mp/proxy-io.h
  include/mp/proxy-types.h
  include/mp/proxy.h
  include/mp/type-char.h
  include/mp/type-chrono.h
  include/mp/type-context.h
  include/mp/type-data.h
  include/mp/type-decay.h
  include/mp/type-exception.h
  include/mp/type-function.h
  include/mp/type-interface.h
  include/mp/type-map.h
  include/mp/type-message.h
  include/mp/type-number.h
  include/mp/type-optional.h
  include/mp/type-pair.h
  include/mp/type-pointer.h
  include/mp/type-set.h
  include/mp/type-string.h
  include/mp/type-struct.h
  include/mp/type-threadmap.h
  include/mp/type-tuple.h
  include/mp/type-vector.h
  include/mp/type-void.h
  include/mp/util.h)
add_library(multiprocess STATIC
  ${MP_PROXY_SRCS}
  ${MP_PUBLIC_HEADERS}
  src/mp/proxy.cpp
  $<TARGET_OBJECTS:mputil>)
add_library(Libmultiprocess::multiprocess ALIAS multiprocess)
target_include_directories(multiprocess PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/include>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)
target_link_libraries(multiprocess PUBLIC CapnProto::capnp)
target_link_libraries(multiprocess PUBLIC CapnProto::capnp-rpc)
target_link_libraries(multiprocess PUBLIC CapnProto::kj)
target_link_libraries(multiprocess PUBLIC CapnProto::kj-async)
set_target_properties(multiprocess PROPERTIES
    PUBLIC_HEADER "${MP_PUBLIC_HEADERS}")
install(TARGETS multiprocess EXPORT LibTargets
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR} COMPONENT lib
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/mp COMPONENT lib)

# mpgen code generator
add_executable(mpgen src/mp/gen.cpp $<TARGET_OBJECTS:mputil>)
add_executable(Libmultiprocess::mpgen ALIAS mpgen)
target_include_directories(mpgen PRIVATE $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/include>)
target_include_directories(mpgen PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)
target_link_libraries(mpgen PRIVATE CapnProto::capnp)
target_link_libraries(mpgen PRIVATE CapnProto::capnp-rpc)
target_link_libraries(mpgen PRIVATE CapnProto::capnpc)
target_link_libraries(mpgen PRIVATE CapnProto::kj)
target_link_libraries(mpgen PRIVATE Threads::Threads)
set_target_properties(mpgen PROPERTIES
    INSTALL_RPATH_USE_LINK_PATH TRUE)
set_target_properties(mpgen PROPERTIES
    PUBLIC_HEADER include/mp/proxy.capnp)
install(TARGETS mpgen EXPORT BinTargets
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} COMPONENT bin
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/mp COMPONENT bin)

# makefile include to invoke mpgen code generator, for downstream Make projects
install(FILES "include/mpgen.mk"
  DESTINATION ${CMAKE_INSTALL_INCLUDEDIR} COMPONENT bin)

# pkg-config module to build against libmultiprocess library, for downstream autoconf projects
configure_file(pkgconfig/libmultiprocess.pc.in "${CMAKE_CURRENT_BINARY_DIR}/pkgconfig/libmultiprocess.pc" @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/pkgconfig/libmultiprocess.pc"
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig COMPONENT lib)

# cmake include to invoke mpgen code generator, for downstream CMake projects
install(
  FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/TargetCapnpSources.cmake
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Libmultiprocess COMPONENT bin)

# CMake target import files, for downstream CMake projects
install(EXPORT BinTargets
  NAMESPACE Libmultiprocess::
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Libmultiprocess COMPONENT bin)
install(EXPORT LibTargets
  NAMESPACE Libmultiprocess::
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Libmultiprocess COMPONENT lib)

# CMake find_package config file, for downstream CMake projects
include(CMakePackageConfigHelpers)
configure_package_config_file(
  ${PROJECT_SOURCE_DIR}/cmake/Config.cmake.in
  LibmultiprocessConfig.cmake
  INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Libmultiprocess
  NO_SET_AND_CHECK_MACRO)
install(
  FILES
    ${CMAKE_CURRENT_BINARY_DIR}/LibmultiprocessConfig.cmake
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Libmultiprocess
  COMPONENT common)

# Makefile targets to support "make install-bin" "make install-lib"
add_custom_target(install-bin
  COMMAND ${CMAKE_COMMAND} -DCOMPONENT=bin -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_install.cmake
  COMMAND ${CMAKE_COMMAND} -DCOMPONENT=common -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_install.cmake
  VERBATIM)
add_dependencies(install-bin mpgen)
add_custom_target(install-lib
  COMMAND ${CMAKE_COMMAND} -DCOMPONENT=lib -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_install.cmake
  COMMAND ${CMAKE_COMMAND} -DCOMPONENT=common -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_install.cmake
  VERBATIM)
add_dependencies(install-lib multiprocess)

# Prefer Unix-style package components over frameworks on macOS.
# This improves compatibility with Python version managers.
set(Python3_FIND_FRAMEWORK LAST CACHE STRING "")
# Search for generic names before more specialized ones. This
# improves compatibility with Python version managers that use shims.
set(Python3_FIND_UNVERSIONED_NAMES FIRST CACHE STRING "")
mark_as_advanced(Python3_FIND_FRAMEWORK Python3_FIND_UNVERSIONED_NAMES)
find_package(Python3 3.10 COMPONENTS Interpreter)
if(Python3_EXECUTABLE)
  set(PYTHON_COMMAND ${Python3_EXECUTABLE})
else()
  list(APPEND configure_warnings
    "Minimum required Python not found. Utils and rpcauth tests are disabled."
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

include(cmake/tests.cmake)

include(Maintenance)
setup_split_debug_script()
add_maintenance_targets()
add_windows_deploy_target()
add_macos_deploy_target()

message("\n")
message("Configure summary")
message("=================")
message("Executables:")
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
if(ENABLE_WALLET)
  message("   - legacy wallets (Berkeley DB) ..... ${WITH_BDB}")
endif()
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
message("  DBus (GUI, Linux only) .............. ${WITH_DBUS}")
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
message("C++ compiler .......................... ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}, ${CMAKE_CXX_COMPILER}")
include(FlagsSummary)
flags_summary()
message("Attempt to harden executables ......... ${ENABLE_HARDENING}")
message("Treat compiler warnings as errors ..... ${WERROR}")
message("Use ccache for compiling .............. ${WITH_CCACHE}")
message("\n")
if(configure_warnings)
    message("  ******\n")
    foreach(warning IN LISTS configure_warnings)
      message(WARNING "${warning}")
    endforeach()
    message("  ******\n")
endif()

# We want all build properties to be encapsulated properly.
include(WarnAboutGlobalProperties)
