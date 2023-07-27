cmake_minimum_required(VERSION 3.9)

project(BGL-tidy VERSION 1.0.0 DESCRIPTION "clang-tidy checks for BGL Core")

include(GNUInstallDirs)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_EXTENSIONS False)

# TODO: Figure out how to avoid the terminfo check
find_package(LLVM REQUIRED CONFIG)
find_program(CLANG_TIDY_EXE NAMES "clang-tidy-${LLVM_VERSION_MAJOR}" "clang-tidy" HINTS ${LLVM_TOOLS_BINARY_DIR})
message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Found clang-tidy: ${CLANG_TIDY_EXE}")

add_library(BGL-tidy MODULE BGL-tidy.cpp logprintf.cpp)
target_include_directories(BGL-tidy SYSTEM PRIVATE ${LLVM_INCLUDE_DIRS})

# Disable RTTI and exceptions as necessary
if (MSVC)
    target_compile_options(BGL-tidy PRIVATE /GR-)
else()
    target_compile_options(BGL-tidy PRIVATE -fno-rtti)
    target_compile_options(CMAKE_BUILD_RPATH_USE_ORIGIN-tidy PRIVATE -fno-exceptions)
endif()

# Add warnings
if (MSVC)
    target_compile_options(BGL-tidy PRIVATE /W4)
else()
    target_compile_options(BGL-tidy PRIVATE -Wall)
    target_compile_options(BGL-tidy PRIVATE -Wextra)
endif()

set(CLANG_TIDY_COMMAND "${CLANG_TIDY_EXE}" "--load=${CMAKE_BINARY_DIR}/${CMAKE_SHARED_LIBRARY_PREFIX}bitcoin-tidy${CMAKE_SHARED_LIBRARY_SUFFIX}" "-checks=-*,bitcoin-*")

# Create a dummy library that runs clang-tidy tests as a side-effect of building
add_library(BGL-tidy-tests OBJECT EXCLUDE_FROM_ALL example_logprintf.cpp)
add_dependencies(BGL-tidy-tests BGL-tidy)

set_target_properties(BGL-tidy-tests PROPERTIES CXX_CLANG_TIDY "${CLANG_TIDY_COMMAND}")


install(TARGETS BGL-tidy LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
