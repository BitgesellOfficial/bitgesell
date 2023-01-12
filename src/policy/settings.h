// Copyright (c) 2009-2010 Satoshi Nakamoto
// Copyright (c) 2009-2019 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_POLICY_SETTINGS_H
#define BGL_POLICY_SETTINGS_H

#include <policy/feerate.h>
#include <policy/policy.h>

#include <cstdint>

class CTransaction;

extern CFeeRate dustRelayFee;
extern unsigned int nBytesPerSigOp;
extern bool fIsBareMultisigStd;

static inline int64_t GetVirtualTransactionSize(int64_t weight, int64_t sigop_cost)
{
    return GetVirtualTransactionSize(weight, sigop_cost, ::nBytesPerSigOp);
}

static inline int64_t GetVirtualTransactionSize(const CTransaction& tx, int64_t sigop_cost)
{
    return GetVirtualTransactionSize(tx, sigop_cost, ::nBytesPerSigOp);
}

#endif // BGL_POLICY_SETTINGS_H
