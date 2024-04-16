// Copyright (c) 2024 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_NODE_TXDOWNLOADMAN_H
#define BGL_NODE_TXDOWNLOADMAN_H

#include <net.h>
#include <policy/packages.h>

#include <cstdint>
#include <memory>

class CBlock;
class CRollingBloomFilter;
class TxOrphanage;
class TxRequestTracker;
namespace node {
class TxDownloadManagerImpl;

struct TxDownloadOptions {
    /** Read-only reference to mempool. */
    const CTxMemPool& m_mempool;
    /** RNG provided by caller. */
    FastRandomContext& m_rng;
};
struct TxDownloadConnectionInfo {
    /** Whether this peer is preferred for transaction download. */
    const bool m_preferred;
    /** Whether this peer has Relay permissions. */
    const bool m_relay_permissions;
    /** Whether this peer supports wtxid relay. */
    const bool m_wtxid_relay;
};
struct PackageToValidate {
    Package m_txns;
    std::vector<NodeId> m_senders;
    /** Construct a 1-parent-1-child package. */
    explicit PackageToValidate(const CTransactionRef& parent,
                               const CTransactionRef& child,
                               NodeId parent_sender,
                               NodeId child_sender) :
        m_txns{parent, child},
        m_senders{parent_sender, child_sender}
    {}

    // Move ctor
    PackageToValidate(PackageToValidate&& other) : m_txns{std::move(other.m_txns)}, m_senders{std::move(other.m_senders)} {}

    // Move assignment
    PackageToValidate& operator=(PackageToValidate&& other) {
        this->m_txns = std::move(other.m_txns);
        this->m_senders = std::move(other.m_senders);
        return *this;
    }

    std::string ToString() const {
        Assume(m_txns.size() == 2);
        return strprintf("parent %s (wtxid=%s, sender=%d) + child %s (wtxid=%s, sender=%d)",
                         m_txns.front()->GetHash().ToString(),
                         m_txns.front()->GetWitnessHash().ToString(),
                         m_senders.front(),
                         m_txns.back()->GetHash().ToString(),
                         m_txns.back()->GetWitnessHash().ToString(),
                         m_senders.back());
    }
};

/**
 * Class responsible for deciding what transactions to request and, once
 * downloaded, whether and how to validate them. It is also responsible for
 * deciding what transaction packages to validate and how to resolve orphan
 * transactions. Its data structures include TxRequestTracker for scheduling
 * requests, rolling bloom filters for remembering transactions that have
 * already been {accepted, rejected, confirmed}, an orphanage, and a registry of
 * each peer's transaction relay-related information.
 *
 * Caller needs to interact with TxDownloadManager:
 * - ValidationInterface callbacks.
 * - When a potential transaction relay peer connects or disconnects.
 * - When a transaction or package is accepted or rejected from mempool
 * - When a inv, notfound, or tx message is received
 * - To get instructions for which getdata messages to send
 *
 * This class is not thread-safe. Access must be synchronized using an
 * external mutex.
 */
class TxDownloadManager {
    const std::unique_ptr<TxDownloadManagerImpl> m_impl;

public:
    explicit TxDownloadManager(const TxDownloadOptions& options);
    ~TxDownloadManager();

    // Get references to internal data structures. Outside access to these data structures should be
    // temporary and removed later once logic has been moved internally.
    TxOrphanage& GetOrphanageRef();
    TxRequestTracker& GetTxRequestRef();
    CRollingBloomFilter& RecentRejectsFilter();
    CRollingBloomFilter& RecentRejectsReconsiderableFilter();
    CRollingBloomFilter& RecentConfirmedTransactionsFilter();

    // Responses to chain events. TxDownloadManager is not an actual client of ValidationInterface, these are called through PeerManager.
    void ActiveTipChange();
    void BlockConnected(const std::shared_ptr<const CBlock>& pblock);
    void BlockDisconnected();
};
} // namespace node
#endif // BGL_NODE_TXDOWNLOADMAN_H
