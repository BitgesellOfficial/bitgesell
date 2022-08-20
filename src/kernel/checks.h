// Copyright (c) 2022 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_KERNEL_CHECKS_H
#define BGL_KERNEL_CHECKS_H

#include <optional>

namespace kernel {

struct Context;

enum class SanityCheckError {
    ERROR_ECC,
    ERROR_RANDOM,
    ERROR_CHRONO,
};

/**
 *  Ensure a usable environment with all necessary library support.
 */
std::optional<SanityCheckError> SanityChecks(const Context&);

}

#endif // BGL_KERNEL_CHECKS_H
