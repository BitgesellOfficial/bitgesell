// Copyright (c) 2017-2019 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_OPTIONAL_H
#define BGL_OPTIONAL_H

#include <utility>

#include <boost/optional.hpp>

//! Substitute for C++17 std::optional
template <typename T>
using Optional = boost::optional<T>;

//! Substitute for C++17 std::nullopt
static auto& nullopt = boost::none;

#endif // BGL_OPTIONAL_H
