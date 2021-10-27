// Copyright (c) 2009-2010 Satoshi Nakamoto
// Copyright (c) 2009-2020 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <script/standard.h>

#include <crypto/sha256.h>
#include <hash.h>
#include <pubkey.h>
#include <script/interpreter.h>
#include <script/script.h>
#include <util/strencodings.h>

#include <string>

typedef std::vector<unsigned char> valtype;

bool fAcceptDatacarrier = DEFAULT_ACCEPT_DATACARRIER;
unsigned nMaxDatacarrierBytes = MAX_OP_RETURN_RELAY;

CScriptID::CScriptID(const CScript& in) : BaseHash(Hash160(in)) {}
CScriptID::CScriptID(const ScriptHash& in) : BaseHash(static_cast<uint160>(in)) {}

ScriptHash::ScriptHash(const CScript& in) : BaseHash(Hash160(in)) {}
ScriptHash::ScriptHash(const CScriptID& in) : BaseHash(static_cast<uint160>(in)) {}

PKHash::PKHash(const CPubKey& pubkey) : BaseHash(pubkey.GetID()) {}
PKHash::PKHash(const CKeyID& pubkey_id) : BaseHash(pubkey_id) {}

WitnessV0KeyHash::WitnessV0KeyHash(const CPubKey& pubkey) : BaseHash(pubkey.GetID()) {}
WitnessV0KeyHash::WitnessV0KeyHash(const PKHash& pubkey_hash) : BaseHash(static_cast<uint160>(pubkey_hash)) {}

CKeyID ToKeyID(const PKHash& key_hash)
{
    return CKeyID{static_cast<uint160>(key_hash)};
}

CKeyID ToKeyID(const WitnessV0KeyHash& key_hash)
{
    return CKeyID{static_cast<uint160>(key_hash)};
}

WitnessV0ScriptHash::WitnessV0ScriptHash(const CScript& in)
{
    CSHA256().Write(in.data(), in.size()).Finalize(begin());
}

std::string GetTxnOutputType(TxoutType t)
{
    switch (t)
    {
    case TxoutType::NONSTANDARD: return "nonstandard";
    case TxoutType::PUBKEY: return "pubkey";
    case TxoutType::PUBKEYHASH: return "pubkeyhash";
    case TxoutType::SCRIPTHASH: return "scripthash";
    case TxoutType::MULTISIG: return "multisig";
    case TxoutType::NULL_DATA: return "nulldata";
    case TxoutType::WITNESS_V0_KEYHASH: return "witness_v0_keyhash";
    case TxoutType::WITNESS_V0_SCRIPTHASH: return "witness_v0_scripthash";
    case TxoutType::WITNESS_V1_TAPROOT: return "witness_v1_taproot";
    case TxoutType::WITNESS_UNKNOWN: return "witness_unknown";
    } // no default case, so the compiler can warn about missing cases
    assert(false);
}

static bool MatchPayToPubkey(const CScript& script, valtype& pubkey)
{
    if (script.size() == CPubKey::SIZE + 2 && script[0] == CPubKey::SIZE && script.back() == OP_CHECKSIG) {
        pubkey = valtype(script.begin() + 1, script.begin() + CPubKey::SIZE + 1);
        return CPubKey::ValidSize(pubkey);
    }
    if (script.size() == CPubKey::COMPRESSED_SIZE + 2 && script[0] == CPubKey::COMPRESSED_SIZE && script.back() == OP_CHECKSIG) {
        pubkey = valtype(script.begin() + 1, script.begin() + CPubKey::COMPRESSED_SIZE + 1);
        return CPubKey::ValidSize(pubkey);
    }
    return false;
}

static bool MatchPayToPubkeyHash(const CScript& script, valtype& pubkeyhash)
{
    if (script.size() == 25 && script[0] == OP_DUP && script[1] == OP_HASH160 && script[2] == 20 && script[23] == OP_EQUALVERIFY && script[24] == OP_CHECKSIG) {
        pubkeyhash = valtype(script.begin () + 3, script.begin() + 23);
        return true;
    }
    return false;
}

/** Test for "small positive integer" script opcodes - OP_1 through OP_16. */
static constexpr bool IsSmallInteger(opcodetype opcode)
{
    return opcode >= OP_1 && opcode <= OP_16;
}

static constexpr bool IsPushdataOp(opcodetype opcode)
{
    return opcode > OP_FALSE && opcode <= OP_PUSHDATA4;
}

static constexpr bool IsValidMultisigKeyCount(int n_keys)
{
    return n_keys > 0 && n_keys <= MAX_PUBKEYS_PER_MULTISIG;
}

static bool GetMultisigKeyCount(opcodetype opcode, valtype data, int& count)
{
    if (IsSmallInteger(opcode)) {
        count = CScript::DecodeOP_N(opcode);
        return IsValidMultisigKeyCount(count);
    }

    if (IsPushdataOp(opcode)) {
        if (!CheckMinimalPush(data, opcode)) return false;
        try {
            count = CScriptNum(data, /* fRequireMinimal = */ true).getint();
            return IsValidMultisigKeyCount(count);
        } catch (const scriptnum_error&) {
            return false;
        }
    }

    return false;
}

static bool MatchMultisig(const CScript& script, int& required_sigs, std::vector<valtype>& pubkeys)
{
    opcodetype opcode;
    valtype data;
    int num_keys;

    CScript::const_iterator it = script.begin();
    if (script.size() < 1 || script.back() != OP_CHECKMULTISIG) return false;

    if (!script.GetOp(it, opcode, data) || !GetMultisigKeyCount(opcode, data, required_sigs)) return false;
    while (script.GetOp(it, opcode, data) && CPubKey::ValidSize(data)) {
        pubkeys.emplace_back(std::move(data));
    }
    if (!GetMultisigKeyCount(opcode, data, num_keys)) return false;

    if (pubkeys.size() != static_cast<unsigned long>(num_keys) || num_keys < required_sigs) return false;

    return (it + 1 == script.end());
}

TxoutType Solver(const CScript& scriptPubKey, std::vector<std::vector<unsigned char>>& vSolutionsRet)
{
    vSolutionsRet.clear();

    // Shortcut for pay-to-script-hash, which are more constrained than the other types:
    // it is always OP_HASH160 20 [20 byte hash] OP_EQUAL
    if (scriptPubKey.IsPayToScriptHash())
    {
        std::vector<unsigned char> hashBytes(scriptPubKey.begin()+2, scriptPubKey.begin()+22);
        vSolutionsRet.push_back(hashBytes);
        return TxoutType::SCRIPTHASH;
    }

    int witnessversion;
    std::vector<unsigned char> witnessprogram;
    if (scriptPubKey.IsWitnessProgram(witnessversion, witnessprogram)) {
        if (witnessversion == 0 && witnessprogram.size() == WITNESS_V0_KEYHASH_SIZE) {
            vSolutionsRet.push_back(std::move(witnessprogram));
            return TxoutType::WITNESS_V0_KEYHASH;
        }
        if (witnessversion == 0 && witnessprogram.size() == WITNESS_V0_SCRIPTHASH_SIZE) {
            vSolutionsRet.push_back(std::move(witnessprogram));
            return TxoutType::WITNESS_V0_SCRIPTHASH;
        }
        if (witnessversion == 1 && witnessprogram.size() == WITNESS_V1_TAPROOT_SIZE) {
            vSolutionsRet.push_back(std::move(witnessprogram));
            return TxoutType::WITNESS_V1_TAPROOT;
        }
        if (witnessversion != 0) {
            vSolutionsRet.push_back(std::vector<unsigned char>{(unsigned char)witnessversion});
            vSolutionsRet.push_back(std::move(witnessprogram));
            return TxoutType::WITNESS_UNKNOWN;
        }
        return TxoutType::NONSTANDARD;
    }

    // Provably prunable, data-carrying output
    //
    // So long as script passes the IsUnspendable() test and all but the first
    // byte passes the IsPushOnly() test we don't care what exactly is in the
    // script.
    if (scriptPubKey.size() >= 1 && scriptPubKey[0] == OP_RETURN && scriptPubKey.IsPushOnly(scriptPubKey.begin()+1)) {
        return TxoutType::NULL_DATA;
    }

    std::vector<unsigned char> data;
    if (MatchPayToPubkey(scriptPubKey, data)) {
        vSolutionsRet.push_back(std::move(data));
        return TxoutType::PUBKEY;
    }

    if (MatchPayToPubkeyHash(scriptPubKey, data)) {
        vSolutionsRet.push_back(std::move(data));
        return TxoutType::PUBKEYHASH;
    }

    int required;
    std::vector<std::vector<unsigned char>> keys;
    if (MatchMultisig(scriptPubKey, required, keys)) {
        vSolutionsRet.push_back({static_cast<unsigned char>(required)}); // safe as required is in range 1..20
        vSolutionsRet.insert(vSolutionsRet.end(), keys.begin(), keys.end());
        vSolutionsRet.push_back({static_cast<unsigned char>(keys.size())}); // safe as size is in range 1..20
        return TxoutType::MULTISIG;
    }

    vSolutionsRet.clear();
    return TxoutType::NONSTANDARD;
}

bool ExtractDestination(const CScript& scriptPubKey, CTxDestination& addressRet)
{
    std::vector<valtype> vSolutions;
    TxoutType whichType = Solver(scriptPubKey, vSolutions);

    if (whichType == TxoutType::PUBKEY) {
        CPubKey pubKey(vSolutions[0]);
        if (!pubKey.IsValid())
            return false;

        addressRet = PKHash(pubKey);
        return true;
    }
    else if (whichType == TxoutType::PUBKEYHASH)
    {
        addressRet = PKHash(uint160(vSolutions[0]));
        return true;
    }
    else if (whichType == TxoutType::SCRIPTHASH)
    {
        addressRet = ScriptHash(uint160(vSolutions[0]));
        return true;
    } else if (whichType == TxoutType::WITNESS_V0_KEYHASH) {
        WitnessV0KeyHash hash;
        std::copy(vSolutions[0].begin(), vSolutions[0].end(), hash.begin());
        addressRet = hash;
        return true;
    } else if (whichType == TxoutType::WITNESS_V0_SCRIPTHASH) {
        WitnessV0ScriptHash hash;
        std::copy(vSolutions[0].begin(), vSolutions[0].end(), hash.begin());
        addressRet = hash;
        return true;
    }
    case TxoutType::WITNESS_V1_TAPROOT: {
        /* For now, no WitnessV1Taproot variant in CTxDestination exists, so map
         * this to WitnessUnknown. */
        WitnessUnknown unk;
        unk.version = 1;
        std::copy(vSolutions[0].begin(), vSolutions[0].end(), unk.program);
        unk.length = vSolutions[0].size();
        addressRet = unk;
        return true;
    }
    case TxoutType::WITNESS_UNKNOWN: {
        WitnessUnknown unk;
        unk.version = vSolutions[0][0];
        std::copy(vSolutions[1].begin(), vSolutions[1].end(), unk.program);
        unk.length = vSolutions[1].size();
        addressRet = unk;
        return true;
    }
    // Multisig txns have more than one address...
    return false;
}

// TODO: from v23 ("addresses" and "reqSigs" deprecated) "ExtractDestinations" should be removed
bool ExtractDestinations(const CScript& scriptPubKey, TxoutType& typeRet, std::vector<CTxDestination>& addressRet, int& nRequiredRet)
{
    addressRet.clear();
    std::vector<valtype> vSolutions;
    typeRet = Solver(scriptPubKey, vSolutions);
    if (typeRet == TxoutType::NONSTANDARD) {
        return false;
    } else if (typeRet == TxoutType::NULL_DATA) {
        // This is data, not addresses
        return false;
    }

    if (typeRet == TxoutType::MULTISIG)
    {
        nRequiredRet = vSolutions.front()[0];
        for (unsigned int i = 1; i < vSolutions.size()-1; i++)
        {
            CPubKey pubKey(vSolutions[i]);
            if (!pubKey.IsValid())
                continue;

            CTxDestination address = PKHash(pubKey);
            addressRet.push_back(address);
        }

        if (addressRet.empty())
            return false;
    }
    else
    {
        nRequiredRet = 1;
        CTxDestination address;
        if (!ExtractDestination(scriptPubKey, address))
           return false;
        addressRet.push_back(address);
    }

    return true;
}

namespace {
class CScriptVisitor
{
public:
    CScript operator()(const CNoDestination& dest) const
    {
        return CScript();
    }

    CScript operator()(const PKHash& keyID) const
    {
        return CScript() << OP_DUP << OP_HASH160 << ToByteVector(keyID) << OP_EQUALVERIFY << OP_CHECKSIG;
    }

    CScript operator()(const ScriptHash& scriptID) const
    {
        return CScript() << OP_HASH160 << ToByteVector(scriptID) << OP_EQUAL;
    }

    CScript operator()(const WitnessV0KeyHash& id) const
    {
        return CScript() << OP_0 << ToByteVector(id);
    }

    CScript operator()(const WitnessV0ScriptHash& id) const
    {
        return CScript() << OP_0 << ToByteVector(id);
    }

    CScript operator()(const WitnessUnknown& id) const
    {
        return CScript() << CScript::EncodeOP_N(id.version) << std::vector<unsigned char>(id.program, id.program + id.length);
    }
};
} // namespace

CScript GetScriptForDestination(const CTxDestination& dest)
{
    return std::visit(CScriptVisitor(), dest);
}

CScript GetScriptForRawPubKey(const CPubKey& pubKey)
{
    return CScript() << std::vector<unsigned char>(pubKey.begin(), pubKey.end()) << OP_CHECKSIG;
}

CScript GetScriptForMultisig(int nRequired, const std::vector<CPubKey>& keys)
{
    CScript script;

    script << nRequired;
    for (const CPubKey& key : keys)
        script << ToByteVector(key);
    script << keys.size() << OP_CHECKMULTISIG;

    return script;
}

bool IsValidDestination(const CTxDestination& dest) {
    return dest.index() != 0;
}

/*static*/ TaprootBuilder::NodeInfo TaprootBuilder::Combine(NodeInfo&& a, NodeInfo&& b)
{
    NodeInfo ret;
    /* Lexicographically sort a and b's hash, and compute parent hash. */
    if (a.hash < b.hash) {
        ret.hash = (CHashWriter(HASHER_TAPBRANCH) << a.hash << b.hash).GetSHA256();
    } else {
        ret.hash = (CHashWriter(HASHER_TAPBRANCH) << b.hash << a.hash).GetSHA256();
    }
    return ret;
}

void TaprootBuilder::Insert(TaprootBuilder::NodeInfo&& node, int depth)
{
    assert(depth >= 0 && (size_t)depth <= TAPROOT_CONTROL_MAX_NODE_COUNT);
    /* We cannot insert a leaf at a lower depth while a deeper branch is unfinished. Doing
     * so would mean the Add() invocations do not correspond to a DFS traversal of a
     * binary tree. */
    if ((size_t)depth + 1 < m_branch.size()) {
        m_valid = false;
        return;
    }
    /* As long as an entry in the branch exists at the specified depth, combine it and propagate up.
     * The 'node' variable is overwritten here with the newly combined node. */
    while (m_valid && m_branch.size() > (size_t)depth && m_branch[depth].has_value()) {
        node = Combine(std::move(node), std::move(*m_branch[depth]));
        m_branch.pop_back();
        if (depth == 0) m_valid = false; /* Can't propagate further up than the root */
        --depth;
    }
    if (m_valid) {
        /* Make sure the branch is big enough to place the new node. */
        if (m_branch.size() <= (size_t)depth) m_branch.resize((size_t)depth + 1);
        assert(!m_branch[depth].has_value());
        m_branch[depth] = std::move(node);
    }
}

/*static*/ bool TaprootBuilder::ValidDepths(const std::vector<int>& depths)
{
    std::vector<bool> branch;
    for (int depth : depths) {
        // This inner loop corresponds to effectively the same logic on branch
        // as what Insert() performs on the m_branch variable. Instead of
        // storing a NodeInfo object, just remember whether or not there is one
        // at that depth.
        if (depth < 0 || (size_t)depth > TAPROOT_CONTROL_MAX_NODE_COUNT) return false;
        if ((size_t)depth + 1 < branch.size()) return false;
        while (branch.size() > (size_t)depth && branch[depth]) {
            branch.pop_back();
            if (depth == 0) return false;
            --depth;
        }
        if (branch.size() <= (size_t)depth) branch.resize((size_t)depth + 1);
        assert(!branch[depth]);
        branch[depth] = true;
    }
    // And this check corresponds to the IsComplete() check on m_branch.
    return branch.size() == 0 || (branch.size() == 1 && branch[0]);
}

TaprootBuilder& TaprootBuilder::Add(int depth, const CScript& script, int leaf_version)
{
    assert((leaf_version & ~TAPROOT_LEAF_MASK) == 0);
    if (!IsValid()) return *this;
    /* Construct NodeInfo object with leaf hash. */
    NodeInfo node;
    node.hash = (CHashWriter{HASHER_TAPLEAF} << uint8_t(leaf_version) << script).GetSHA256();
    /* Insert into the branch. */
    Insert(std::move(node), depth);
    return *this;
}

TaprootBuilder& TaprootBuilder::AddOmitted(int depth, const uint256& hash)
{
    if (!IsValid()) return *this;
    /* Construct NodeInfo object with the hash directly, and insert it into the branch. */
    NodeInfo node;
    node.hash = hash;
    Insert(std::move(node), depth);
    return *this;
}

TaprootBuilder& TaprootBuilder::Finalize(const XOnlyPubKey& internal_key)
{
    /* Can only call this function when IsComplete() is true. */
    assert(IsComplete());
    m_internal_key = internal_key;
    auto ret = m_internal_key.CreateTapTweak(m_branch.size() == 0 ? nullptr : &m_branch[0]->hash);
    assert(ret.has_value());
    std::tie(m_output_key, std::ignore) = *ret;
    return *this;
}

WitnessV1Taproot TaprootBuilder::GetOutput() { return WitnessV1Taproot{m_output_key}; }
