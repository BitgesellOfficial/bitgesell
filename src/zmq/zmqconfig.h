// Copyright (c) 2014-2018 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_ZMQ_ZMQCONFIG_H
#define BGL_ZMQ_ZMQCONFIG_H

#if defined(HAVE_CONFIG_H)
#include <config/BGL-config.h>
#endif

#include <stdarg.h>

#if ENABLE_ZMQ
#include <zmq.h>
#endif

#include <primitives/transaction.h>

void zmqError(const char *str);

#endif // BGL_ZMQ_ZMQCONFIG_H
