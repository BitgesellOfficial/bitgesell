// Copyright (c) 2023 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_NODE_ABORT_H
#define BGL_NODE_ABORT_H

#include <atomic>

struct bilingual_str;

namespace util {
class SignalInterrupt;
} // namespace util

namespace node {
class Warnings;
void AbortNode(util::SignalInterrupt* shutdown, std::atomic<int>& exit_status, const bilingual_str& message, node::Warnings* warnings);
} // namespace node

#endif // BGL_NODE_ABORT_H
