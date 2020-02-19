// Copyright (c) 2018-2021 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <chainparamsbase.h>
#include <key_io.h>
#include <rpc/server.h>
#include <util/strencodings.h>
#include <wallet/rpcsigner.h>
#include <wallet/wallet.h>

#ifdef ENABLE_EXTERNAL_SIGNER

// CRPCCommand table won't compile with an empty array
static RPCHelpMan dummy()
{
    return RPCHelpMan{"dummy",
                "\nDoes nothing.\n"
                "",
                {},
                RPCResult{RPCResult::Type::NONE, "", ""},
                RPCExamples{""},
        [&](const RPCHelpMan& self, const JSONRPCRequest& request) -> UniValue
{
    return NullUniValue;
},
    };
}

static RPCHelpMan signerdisplayaddress()
{
    return RPCHelpMan{
        "signerdisplayaddress",
        "Display address on an external signer for verification.\n",
        {
            {"address",     RPCArg::Type::STR, RPCArg::Optional::NO, /* default_val */ "", "BGL address to display"},
        },
        RPCResult{RPCResult::Type::NONE,"",""},
        RPCExamples{""},
        [](const RPCHelpMan& self, const JSONRPCRequest& request) -> UniValue {
            std::shared_ptr<CWallet> const wallet = GetWalletForJSONRPCRequest(request);
            if (!wallet) return NullUniValue;
            CWallet* const pwallet = wallet.get();

            LOCK(pwallet->cs_wallet);

            CTxDestination dest = DecodeDestination(request.params[0].get_str());

            // Make sure the destination is valid
            if (!IsValidDestination(dest)) {
                throw JSONRPCError(RPC_INVALID_ADDRESS_OR_KEY, "Invalid address");
            }

            if (!pwallet->DisplayAddress(dest)) {
                throw JSONRPCError(RPC_WALLET_ERROR, "Failed to display address");
            }

            UniValue result(UniValue::VOBJ);
            result.pushKV("address", request.params[0].get_str());
            return result;
        }
    };
}

Span<const CRPCCommand> GetSignerRPCCommands()
{
// clang-format off
static const CRPCCommand commands[] =
{ // category              actor (function)
  // --------------------- ------------------------
  { "signer",              &enumeratesigners,      },
  { "signer",              &signerdisplayaddress,  },
};
// clang-format on
    return MakeSpan(commands);
}


#endif // ENABLE_EXTERNAL_SIGNER
