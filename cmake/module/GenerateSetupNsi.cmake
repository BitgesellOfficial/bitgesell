# Copyright (c) 2023-present The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

function(generate_setup_nsi)
  set(abs_top_srcdir ${PROJECT_SOURCE_DIR})
  set(abs_top_builddir ${PROJECT_BINARY_DIR})
  set(CLIENT_URL ${PROJECT_HOMEPAGE_URL})
  set(CLIENT_TARNAME "Bitgesell")
  set(BGL_WRAPPER_NAME "BGL")
  set(BGL_GUI_NAME "BGL-qt")
  set(BGL_DAEMON_NAME "BGLd")
  set(BGL_CLI_NAME "BGL-cli")
  set(BGL_TX_NAME "BGL-tx")
  set(BGL_WALLET_TOOL_NAME "BGL-wallet")
  set(BGL_TEST_NAME "test_BGL")
  set(EXEEXT ${CMAKE_EXECUTABLE_SUFFIX})
  configure_file(${PROJECT_SOURCE_DIR}/share/setup.nsi.in ${PROJECT_BINARY_DIR}/BGL-win64-setup.nsi USE_SOURCE_PERMISSIONS @ONLY)
endfunction()
