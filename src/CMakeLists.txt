add_library(secp256k1)

set_property(TARGET secp256k1 PROPERTY PUBLIC_HEADER
  ${PROJECT_SOURCE_DIR}/include/secp256k1.h
  ${PROJECT_SOURCE_DIR}/include/secp256k1_preallocated.h
)

# Processing must be done in a topological sorting of the dependency graph
# (dependent module first).
if(SECP256K1_ENABLE_MODULE_ELLSWIFT)
  add_compile_definitions(ENABLE_MODULE_ELLSWIFT=1)
  set_property(TARGET secp256k1 APPEND PROPERTY PUBLIC_HEADER ${PROJECT_SOURCE_DIR}/include/secp256k1_ellswift.h)
endif()

if(SECP256K1_ENABLE_MODULE_MUSIG)
  if(DEFINED SECP256K1_ENABLE_MODULE_SCHNORRSIG AND NOT SECP256K1_ENABLE_MODULE_SCHNORRSIG)
    message(FATAL_ERROR "Module dependency error: You have disabled the schnorrsig module explicitly, but it is required by the musig module.")
  endif()
  set(SECP256K1_ENABLE_MODULE_SCHNORRSIG ON)
  add_compile_definitions(ENABLE_MODULE_MUSIG=1)
  set_property(TARGET secp256k1 APPEND PROPERTY PUBLIC_HEADER ${PROJECT_SOURCE_DIR}/include/secp256k1_musig.h)
endif()

if(SECP256K1_ENABLE_MODULE_SCHNORRSIG)
  if(DEFINED SECP256K1_ENABLE_MODULE_EXTRAKEYS AND NOT SECP256K1_ENABLE_MODULE_EXTRAKEYS)
    message(FATAL_ERROR "Module dependency error: You have disabled the extrakeys module explicitly, but it is required by the schnorrsig module.")
  endif()
  set(SECP256K1_ENABLE_MODULE_EXTRAKEYS ON)
  add_compile_definitions(ENABLE_MODULE_SCHNORRSIG=1)
  set_property(TARGET secp256k1 APPEND PROPERTY PUBLIC_HEADER ${PROJECT_SOURCE_DIR}/include/secp256k1_schnorrsig.h)
endif()

if(SECP256K1_ENABLE_MODULE_EXTRAKEYS)
  add_compile_definitions(ENABLE_MODULE_EXTRAKEYS=1)
  set_property(TARGET secp256k1 APPEND PROPERTY PUBLIC_HEADER ${PROJECT_SOURCE_DIR}/include/secp256k1_extrakeys.h)
endif()

if(SECP256K1_ENABLE_MODULE_RECOVERY)
  add_compile_definitions(ENABLE_MODULE_RECOVERY=1)
  set_property(TARGET secp256k1 APPEND PROPERTY PUBLIC_HEADER ${PROJECT_SOURCE_DIR}/include/secp256k1_recovery.h)
endif()

if(SECP256K1_ENABLE_MODULE_ECDH)
  add_compile_definitions(ENABLE_MODULE_ECDH=1)
  set_property(TARGET secp256k1 APPEND PROPERTY PUBLIC_HEADER ${PROJECT_SOURCE_DIR}/include/secp256k1_ecdh.h)
endif()

include(AddWindowsResources)

# Add objects explicitly rather than linking to the object libs to keep them
# from being exported.
target_sources(secp256k1 PRIVATE secp256k1.c $<TARGET_OBJECTS:secp256k1_precomputed>)

if(NOT SECP256K1_ENABLE_API_VISIBILITY_ATTRIBUTES)
  target_compile_definitions(secp256k1 PRIVATE SECP256K1_NO_API_VISIBILITY_ATTRIBUTES)
endif()

# Create a helper lib that parent projects can use to link secp256k1 into a
# static lib.
add_library(secp256k1_objs INTERFACE)
target_sources(secp256k1_objs INTERFACE $<TARGET_OBJECTS:secp256k1> $<TARGET_OBJECTS:secp256k1_precomputed>)

add_library(secp256k1_asm INTERFACE)
if(SECP256K1_ASM STREQUAL "arm32")
  add_library(secp256k1_asm_arm OBJECT EXCLUDE_FROM_ALL)
  target_sources(secp256k1_asm_arm PUBLIC
    asm/field_10x26_arm.s
  )
  target_sources(secp256k1 PRIVATE $<TARGET_OBJECTS:secp256k1_asm_arm>)
  target_sources(secp256k1_objs INTERFACE $<TARGET_OBJECTS:secp256k1_asm_arm>)
  target_link_libraries(secp256k1_asm INTERFACE secp256k1_asm_arm)
endif()
include(../cmake/secp256k1.cmake)
add_secp256k1(secp256k1)

if(SECP256K1_BUILD_BENCHMARK)
  add_executable(bench bench.c)
  target_link_libraries(bench secp256k1)
  add_executable(bench_internal bench_internal.c)
  target_link_libraries(bench_internal secp256k1_precomputed secp256k1_asm)
  add_executable(bench_ecmult bench_ecmult.c)
  target_link_libraries(bench_ecmult secp256k1_precomputed secp256k1_asm)
endif()

if(SECP256K1_BUILD_TESTS)
  add_executable(noverify_tests tests.c)
  target_link_libraries(noverify_tests secp256k1_precomputed secp256k1_asm)
  add_test(NAME secp256k1_noverify_tests COMMAND noverify_tests)
  if(NOT CMAKE_BUILD_TYPE STREQUAL "Coverage")
    add_executable(tests tests.c)
    target_compile_definitions(tests PRIVATE VERIFY)
    target_link_libraries(tests secp256k1_precomputed secp256k1_asm)
    add_test(NAME secp256k1_tests COMMAND tests)
  endif()
endif()


# P2P and RPC server functionality used by `bitcoind` and `bitcoin-qt` executables.
add_library(BGL_node STATIC EXCLUDE_FROM_ALL
  addrdb.cpp
  addrman.cpp
  banman.cpp
  bip324.cpp
  blockencodings.cpp
  blockfilter.cpp
  consensus/tx_verify.cpp
  dbwrapper.cpp
  deploymentstatus.cpp
  flatfile.cpp
  headerssync.cpp
  httprpc.cpp
  httpserver.cpp
  i2p.cpp
  index/base.cpp
  index/blockfilterindex.cpp
  index/coinstatsindex.cpp
  index/txindex.cpp
  init.cpp
  kernel/chain.cpp
  kernel/checks.cpp
  kernel/coinstats.cpp
  kernel/context.cpp
  kernel/cs_main.cpp
  kernel/disconnected_transactions.cpp
  kernel/mempool_removal_reason.cpp
  mapport.cpp
  net.cpp
  net_processing.cpp
  netgroup.cpp
  node/abort.cpp
  node/blockmanager_args.cpp
  node/blockstorage.cpp
  node/caches.cpp
  node/chainstate.cpp
  node/chainstatemanager_args.cpp
  node/coin.cpp
  node/coins_view_args.cpp
  node/connection_types.cpp
  node/context.cpp
  node/database_args.cpp
  node/eviction.cpp
  node/interface_ui.cpp
  node/interfaces.cpp
  node/kernel_notifications.cpp
  node/mempool_args.cpp
  node/mempool_persist.cpp
  node/mempool_persist_args.cpp
  node/miner.cpp
  node/mini_miner.cpp
  node/minisketchwrapper.cpp
  node/peerman_args.cpp
  node/psbt.cpp
  node/timeoffsets.cpp
  node/transaction.cpp
  node/txdownloadman_impl.cpp
  node/txorphanage.cpp
  node/txreconciliation.cpp
  node/utxo_snapshot.cpp
  node/warnings.cpp
  noui.cpp
  policy/ephemeral_policy.cpp
  policy/fees.cpp
  policy/fees_args.cpp
  policy/packages.cpp
  policy/rbf.cpp
  policy/settings.cpp
  policy/truc_policy.cpp
  rest.cpp
  rpc/blockchain.cpp
  rpc/external_signer.cpp
  rpc/fees.cpp
  rpc/mempool.cpp
  rpc/mining.cpp
  rpc/net.cpp
  rpc/node.cpp
  rpc/output_script.cpp
  rpc/rawtransaction.cpp
  rpc/server.cpp
  rpc/server_util.cpp
  rpc/signmessage.cpp
  rpc/txoutproof.cpp
  script/sigcache.cpp
  signet.cpp
  torcontrol.cpp
  txdb.cpp
  txgraph.cpp
  txmempool.cpp
  txrequest.cpp
  validation.cpp
  validationinterface.cpp
  versionbits.cpp
  $<$<TARGET_EXISTS:BGL_wallet>:wallet/init.cpp>
  $<$<NOT:$<TARGET_EXISTS:BGL_wallet>>:dummywallet.cpp>
)
target_link_libraries(BGL_node
  PRIVATE
    core_interface
    BGL_common
    BGL_util
    $<TARGET_NAME_IF_EXISTS:BGL_zmq>
    leveldb
    minisketch
    univalue
    Boost::headers
    $<TARGET_NAME_IF_EXISTS:libevent::core>
    $<TARGET_NAME_IF_EXISTS:libevent::extra>
    $<TARGET_NAME_IF_EXISTS:libevent::pthreads>
    $<TARGET_NAME_IF_EXISTS:USDT::headers>
)

# Bitcoin wrapper executable that can call other executables.
if(BUILD_BGL_BIN)
  add_executable(BGL BGL.cpp)
  add_windows_resources(BGL BGL-res.rc)
  add_windows_application_manifest(BGL)
  target_link_libraries(BGL core_interface BGL_util)
  install_binary_component(BGL)
endif()

# Bitcoin Core bitcoind.
if(BUILD_DAEMON)
  add_executable(BGLd
    BGLd.cpp
    init/BGLd.cpp
  )
  add_windows_resources(BGLd BGLd-res.rc)
  add_windows_application_manifest(BGLd)
  target_link_libraries(BGLd
    core_interface
    BGL_node
    $<TARGET_NAME_IF_EXISTS:BGL_wallet>
  )
  install_binary_component(BGLd HAS_MANPAGE)
endif()
if(ENABLE_IPC AND BUILD_DAEMON)
  add_executable(BGL-node
    BGLd.cpp
    init/BGL-node.cpp
  )
  target_link_libraries(BGL-node
    core_interface
    BGL_node
    BGL_ipc
    $<TARGET_NAME_IF_EXISTS:BGL_wallet>
  )
  install_binary_component(BGL-node INTERNAL)
endif()

if(SECP256K1_INSTALL)
  include(GNUInstallDirs)
  target_include_directories(secp256k1 INTERFACE
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
  )
  install(TARGETS secp256k1
    EXPORT ${PROJECT_NAME}-targets
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  )

  install(EXPORT ${PROJECT_NAME}-targets
    FILE ${PROJECT_NAME}-targets.cmake
    NAMESPACE ${PROJECT_NAME}::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}
  )

  include(CMakePackageConfigHelpers)
  configure_package_config_file(
    ${PROJECT_SOURCE_DIR}/cmake/config.cmake.in
    ${PROJECT_NAME}-config.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}
    NO_SET_AND_CHECK_MACRO
  )
  write_basic_package_version_file(${PROJECT_NAME}-config-version.cmake
    COMPATIBILITY SameMinorVersion
  )

  install(
    FILES
      ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-config.cmake
      ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-config-version.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}
  )

  include(GeneratePkgConfigFile)
  generate_pkg_config_file(${PROJECT_SOURCE_DIR}/libsecp256k1.pc.in)
  install(
    FILES
      ${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}.pc
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/pkgconfig
  )
endif()
