# Copyright (c) 2023-present The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

project(Crypto LANGUAGES C CXX)

add_library(BGL_crypto STATIC EXCLUDE_FROM_ALL
  aes.cpp
  chacha20.cpp
  chacha20poly1305.cpp
  hex_base.cpp
  hkdf_sha256_32.cpp
  hmac_sha256.cpp
  hmac_sha512.cpp
  muhash.cpp
  poly1305.cpp
  ripemd160.cpp
  sha1.cpp
  sha256.cpp
  sha256_sse4.cpp
  sha3.cpp
  sha512.cpp
  siphash.cpp
  ./sha3/sha3.c
  ../support/cleanse.cpp
)

target_link_libraries(BGL_crypto
  PRIVATE
    core_interface
)

if(HAVE_SSE41)
  add_library(BGL_crypto_sse41 STATIC EXCLUDE_FROM_ALL
    sha256_sse41.cpp
  )
  target_compile_definitions(BGL_crypto_sse41 PUBLIC ENABLE_SSE41)
  target_compile_options(BGL_crypto_sse41 PRIVATE ${SSE41_CXXFLAGS})
  target_link_libraries(BGL_crypto_sse41 PRIVATE core_interface)
  target_link_libraries(BGL_crypto PRIVATE BGL_crypto_sse41)
endif()

if(HAVE_AVX2)
  add_library(BGL_crypto_avx2 STATIC EXCLUDE_FROM_ALL
    sha256_avx2.cpp
  )
  target_compile_definitions(BGL_crypto_avx2 PUBLIC ENABLE_AVX2)
  target_compile_options(BGL_crypto_avx2 PRIVATE ${AVX2_CXXFLAGS})
  target_link_libraries(BGL_crypto_avx2 PRIVATE core_interface)
  target_link_libraries(BGL_crypto PRIVATE BGL_crypto_avx2)
endif()

if(HAVE_SSE41 AND HAVE_X86_SHANI)
  add_library(BGL_crypto_x86_shani STATIC EXCLUDE_FROM_ALL
    sha256_x86_shani.cpp
  )
  target_compile_definitions(BGL_crypto_x86_shani PUBLIC ENABLE_SSE41 ENABLE_X86_SHANI)
  target_compile_options(BGL_crypto_x86_shani PRIVATE ${X86_SHANI_CXXFLAGS})
  target_link_libraries(BGL_crypto_x86_shani PRIVATE core_interface)
  target_link_libraries(BGL_crypto PRIVATE BGL_crypto_x86_shani)
endif()

if(HAVE_ARM_SHANI)
  add_library(BGL_crypto_arm_shani STATIC EXCLUDE_FROM_ALL
    sha256_arm_shani.cpp
  )
  target_compile_definitions(BGL_crypto_arm_shani PUBLIC ENABLE_ARM_SHANI)
  target_compile_options(BGL_crypto_arm_shani PRIVATE ${ARM_SHANI_CXXFLAGS})
  target_link_libraries(BGL_crypto_arm_shani PRIVATE core_interface)
  target_link_libraries(BGL_crypto PRIVATE BGL_crypto_arm_shani)
endif()
