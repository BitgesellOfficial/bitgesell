// Copyright (c) 2016-2020 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <policy/rbf.h>

#include <policy/settings.h>
#include <tinyformat.h>
#include <util/moneystr.h>
#include <util/rbf.h>

RBFTransactionState IsRBFOptIn(const CTransaction& tx, const CTxMemPool& pool)
{
    AssertLockHeld(pool.cs);

    CTxMemPool::setEntries setAncestors;

    // First check the transaction itself.
    if (SignalsOptInRBF(tx)) {
        return RBFTransactionState::REPLACEABLE_BIP125;
    }

    // If this transaction is not in our mempool, then we can't be sure
    // we will know about all its inputs.
    if (!pool.exists(tx.GetHash())) {
        return RBFTransactionState::UNKNOWN;
    }

    // If all the inputs have nSequence >= maxint-1, it still might be
    // signaled for RBF if any unconfirmed parents have signaled.
    uint64_t noLimit = std::numeric_limits<uint64_t>::max();
    std::string dummy;
    CTxMemPoolEntry entry = *pool.mapTx.find(tx.GetHash());
    pool.CalculateMemPoolAncestors(entry, setAncestors, noLimit, noLimit, noLimit, noLimit, dummy, false);

    for (CTxMemPool::txiter it : setAncestors) {
        if (SignalsOptInRBF(it->GetTx())) {
            return RBFTransactionState::REPLACEABLE_BIP125;
        }
    }
    return RBFTransactionState::FINAL;
}

RBFTransactionState IsRBFOptInEmptyMempool(const CTransaction& tx)
{
    // If we don't have a local mempool we can only check the transaction itself.
    return SignalsOptInRBF(tx) ? RBFTransactionState::REPLACEABLE_BIP125 : RBFTransactionState::UNKNOWN;
}

std::optional<std::string> GetEntriesForConflicts(const CTransaction& tx,
                            CTxMemPool& m_pool,
                            const CTxMemPool::setEntries& setIterConflicting,
                            CTxMemPool::setEntries& allConflicting)
{
    AssertLockHeld(m_pool.cs);
    const uint256 hash = tx.GetHash();
    uint64_t nConflictingCount = 0;
    for (const auto& mi : setIterConflicting) {
        nConflictingCount += mi->GetCountWithDescendants();
        // This potentially overestimates the number of actual descendants but we just want to be
        // conservative to avoid doing too much work.
        if (nConflictingCount > MAX_BIP125_REPLACEMENT_CANDIDATES) {
            return strprintf("rejecting replacement %s; too many potential replacements (%d > %d)\n",
                             txid.ToString(),
                             nConflictingCount,
                             MAX_BIP125_REPLACEMENT_CANDIDATES);
        }
    }
    // If not too many to replace, then calculate the set of
    // transactions that would have to be evicted
    for (CTxMemPool::txiter it : setIterConflicting) {
        m_pool.CalculateDescendants(it, allConflicting);
    }
    return std::nullopt;
}

std::optional<std::string> HasNoNewUnconfirmed(const CTransaction& tx,
                                               const CTxMemPool& m_pool,
                                               const CTxMemPool::setEntries& setIterConflicting)
{
    AssertLockHeld(pool.cs);
    std::set<uint256> parents_of_conflicts;
    for (const auto& mi : iters_conflicting) {
        for (const CTxIn &txin : mi->GetTx().vin) {
            parents_of_conflicts.insert(txin.prevout.hash);
        }
    }

    for (unsigned int j = 0; j < tx.vin.size(); j++) {
        // We don't want to accept replacements that require low feerate junk to be mined first.
        // Ideally we'd keep track of the ancestor feerates and make the decision based on that, but
        // for now requiring all new inputs to be confirmed works.
        //
        // Note that if you relax this to make RBF a little more useful, this may break the
        // CalculateMempoolAncestors RBF relaxation, above. See the comment above the first
        // CalculateMempoolAncestors call for more info.
        if (!parents_of_conflicts.count(tx.vin[j].prevout.hash)) {
            // Rather than check the UTXO set - potentially expensive - it's cheaper to just check
            // if the new input refers to a tx that's in the mempool.
            if (pool.exists(tx.vin[j].prevout.hash)) {
                return strprintf("replacement %s adds unconfirmed input, idx %d",
                                 tx.GetHash().ToString(), j);
            }
        }
    }
    return std::nullopt;
}

std::optional<std::string> EntriesAndTxidsDisjoint(const CTxMemPool::setEntries& setAncestors,
                                                   const std::set<uint256>& setConflicts,
                                                   const uint256& txid)
{
    for (CTxMemPool::txiter ancestorIt : setAncestors)
    {
        const uint256 &hashAncestor = ancestorIt->GetTx().GetHash();
        if (setConflicts.count(hashAncestor))
        {
            return strprintf("%s spends conflicting transaction %s",
                             txid.ToString(),
                             hashAncestor.ToString());
        }
    }
    return std::nullopt;
}

std::optional<std::string> PaysMoreThanConflicts(const CTxMemPool::setEntries& setIterConflicting,
                                                 CFeeRate newFeeRate,
                                                 const uint256& hash)
{
    for (const auto& mi : setIterConflicting) {
        // Don't allow the replacement to reduce the feerate of the
        // mempool.
        //
        // We usually don't want to accept replacements with lower
        // feerates than what they replaced as that would lower the
        // feerate of the next block. Requiring that the feerate always
        // be increased is also an easy-to-reason about way to prevent
        // DoS attacks via replacements.
        //
        // We only consider the feerates of transactions being directly
        // replaced, not their indirect descendants. While that does
        // mean high feerate children are ignored when deciding whether
        // or not to replace, we do require the replacement to pay more
        // overall fees too, mitigating most cases.
        CFeeRate oldFeeRate(mi->GetModifiedFee(), mi->GetTxSize());
        if (newFeeRate <= oldFeeRate)
        {
            return strprintf("rejecting replacement %s; new feerate %s <= old feerate %s",
                             hash.ToString(),
                             newFeeRate.ToString(),
                             oldFeeRate.ToString());
        }
    }
    return std::nullopt;
}

std::optional<std::string> PaysForRBF(CAmount nConflictingFees,
                                      CAmount nModifiedFees,
                                      size_t nSize,
                                      const uint256& hash)
{
    // The replacement must pay greater fees than the transactions it
    // replaces - if we did the bandwidth used by those conflicting
    // transactions would not be paid for.
    if (nModifiedFees < nConflictingFees)
    {
        return strprintf("rejecting replacement %s, less fees than conflicting txs; %s < %s",
                         hash.ToString(), FormatMoney(nModifiedFees), FormatMoney(nConflictingFees));
    }

    // Finally in addition to paying more fees than the conflicts the
    // new transaction must pay for its own bandwidth.
    CAmount nDeltaFees = nModifiedFees - nConflictingFees;
    if (nDeltaFees < ::incrementalRelayFee.GetFee(nSize))
    {
        return strprintf("rejecting replacement %s, not enough additional fees to relay; %s < %s",
                         hash.ToString(),
                         FormatMoney(nDeltaFees),
                         FormatMoney(::incrementalRelayFee.GetFee(nSize)));
    }
    return std::nullopt;
}
