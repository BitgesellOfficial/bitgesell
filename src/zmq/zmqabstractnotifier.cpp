// Copyright (c) 2015-2020 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <zmq/zmqabstractnotifier.h>

#include <cassert>

const int CZMQAbstractNotifier::DEFAULT_ZMQ_SNDHWM;

CZMQAbstractNotifier::~CZMQAbstractNotifier()
{
    assert(!psocket);
}

bool CZMQAbstractNotifier::NotifyBlock([[maybe_unused]] const CBlockIndex * /*CBlockIndex*/)
{
    return true;
}

bool CZMQAbstractNotifier::NotifyTransaction([[maybe_unused]] const CTransaction &/*transaction*/)
{
    return true;
}

bool CZMQAbstractNotifier::NotifyBlockConnect([[maybe_unused]] const CBlockIndex * /*CBlockIndex*/)
{
    return true;
}

bool CZMQAbstractNotifier::NotifyBlockDisconnect([[maybe_unused]] const CBlockIndex * /*CBlockIndex*/)
{
    return true;
}

bool CZMQAbstractNotifier::NotifyTransactionAcceptance([[maybe_unused]] const CTransaction &/*transaction*/, [[maybe_unused]] uint64_t mempool_sequence)
{
    return true;
}

bool CZMQAbstractNotifier::NotifyTransactionRemoval([[maybe_unused]] const CTransaction &/*transaction*/, [[maybe_unused]] uint64_t mempool_sequence)
{
    return true;
}
