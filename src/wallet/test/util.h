// Copyright (c) 2021-2022 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_WALLET_TEST_UTIL_H
#define BGL_WALLET_TEST_UTIL_H

#include <script/standard.h>
#include <memory>

class ArgsManager;
class CChain;
class CKey;
enum class OutputType;
namespace interfaces {
class Chain;
} // namespace interfaces

namespace wallet {
class CWallet;
struct DatabaseOptions;
class WalletDatabase;

std::unique_ptr<CWallet> CreateSyncedWallet(interfaces::Chain& chain, CChain& cchain, ArgsManager& args, const CKey& key);

/** Returns a new encoded destination from the wallet (hardcoded to BECH32) */
std::string getnewaddress(CWallet& w);
/** Returns a new destination, of an specific type, from the wallet */
CTxDestination getNewDestination(CWallet& w, OutputType output_type);

} // namespace wallet

#endif // BGL_WALLET_TEST_UTIL_H
