// Copyright (c) 2016-2020 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_WALLET_RPCWALLET_H
#define BGL_WALLET_RPCWALLET_H

#include <span.h>

class CRPCCommand;

Span<const CRPCCommand> GetWalletRPCCommands();

RPCHelpMan getaddressinfo();
RPCHelpMan signrawtransactionwithwallet();
#endif //BGL_WALLET_RPCWALLET_H