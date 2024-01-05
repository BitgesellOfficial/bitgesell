# Copyright (c) 2020 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

# Custom test targets for convenience, based on
# https://gitlab.kitware.com/cmake/community/-/wikis/doc/tutorials/EmulateMakeCheck.
#
# CTest already provides a "make test" target, but it just runs existing tests
# that were previously built, without building anything itself. Define "make
# tests" here as a custom target to build all available tests and "make check"
# as a custom target to build and run them.
add_custom_target(mptests)
add_custom_target(mpcheck COMMAND ${CMAKE_CTEST_COMMAND} DEPENDS mptests)

# Only add more convenient tests and check targets if project is being built
# standlone, to prevent clashes with external projects.
if (MP_STANDALONE)
  add_custom_target(tests DEPENDS mptests)
  add_custom_target(check DEPENDS mpcheck)
endif()

  set_configure_variable(ENABLE_WALLET ENABLE_WALLET)
  set_configure_variable(BUILD_CLI BUILD_BGL_CLI)
  set_configure_variable(BUILD_UTIL BUILD_BGL_UTIL)
  set_configure_variable(BUILD_UTIL_CHAINSTATE BUILD_BGL_CHAINSTATE)
  set_configure_variable(BUILD_WALLET_TOOL BUILD_BGL_WALLET)
  set_configure_variable(BUILD_DAEMON BUILD_BGLD)
  set_configure_variable(BUILD_FUZZ_BINARY ENABLE_FUZZ_BINARY)
  set_configure_variable(WITH_ZMQ ENABLE_ZMQ)
  set_configure_variable(ENABLE_EXTERNAL_SIGNER ENABLE_EXTERNAL_SIGNER)
  set_configure_variable(WITH_USDT ENABLE_USDT_TRACEPOINTS)

  add_executable(mptest
    ${MP_PROXY_HDRS}
    mp/test/foo-types.h
    mp/test/foo.h
    mp/test/test.cpp
  )
  include(${PROJECT_SOURCE_DIR}/cmake/TargetCapnpSources.cmake)
  target_capnp_sources(mptest ${CMAKE_CURRENT_SOURCE_DIR} mp/test/foo.capnp)
  target_include_directories(mptest PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
  target_link_libraries(mptest PRIVATE CapnProto::kj-test)
  target_link_libraries(mptest PRIVATE Threads::Threads)

  add_dependencies(mptests mptest)
  add_test(NAME mptest COMMAND mptest)
endif()
