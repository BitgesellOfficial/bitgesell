// Copyright (c) 2023 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_TEST_IPC_TEST_H
#define BGL_TEST_IPC_TEST_H

#include <primitives/transaction.h>

class FooImplementation
{
public:
    int add(int a, int b) { return a + b; }
    COutPoint passOutPoint(COutPoint o) { return o; }
};

void IpcTest();

#endif // BGL_TEST_IPC_TEST_H
