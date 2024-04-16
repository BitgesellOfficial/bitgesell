// Copyright (c) 2024 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef BGL_NODE_TXDOWNLOADMAN_H
#define BGL_NODE_TXDOWNLOADMAN_H

#include <cstdint>
#include <memory>

class CBlock;
class CRollingBloomFilter;
class CTxMemPool;
class TxOrphanage;
class TxRequestTracker;
class CRollingBloomFilter;

namespace node {
class TxDownloadManagerImpl;

struct TxDownloadOptions {
    /** Read-only reference to mempool. */
    const CTxMemPool& m_mempool;
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

    // Responses to chain events. TxDownloadManager is not an actual client of ValidationInterface, these are called through PeerManager.
    void ActiveTipChange();
    void BlockConnected(const std::shared_ptr<const CBlock>& pblock);
    void BlockDisconnected();

    /** Check whether we already have this gtxid in:
     *  - mempool
     *  - orphanage
     *  - m_recent_rejects
     *  - m_recent_rejects_reconsiderable (if include_reconsiderable = true)
     *  - m_recent_confirmed_transactions
     *  */
    bool AlreadyHaveTx(const GenTxid& gtxid, bool include_reconsiderable);

    /** Creates a new PeerInfo. Saves the connection info to calculate tx announcement delays later. */
    void ConnectedPeer(NodeId nodeid, const TxDownloadConnectionInfo& info);

    /** Deletes all txrequest announcements and orphans for a given peer. */
    void DisconnectedPeer(NodeId nodeid);

    /** New inv has been received. May be added as a candidate to txrequest.
     * @param[in] p2p_inv     When true, only add this announcement if we don't already have the tx.
     * Returns true if this was a dropped inv (p2p_inv=true and we already have the tx), false otherwise. */
    bool AddTxAnnouncement(NodeId peer, const GenTxid& gtxid, std::chrono::microseconds now, bool p2p_inv);

    /** Get getdata requests to send. */
    std::vector<GenTxid> GetRequestsToSend(NodeId nodeid, std::chrono::microseconds current_time);

    /** Should be called when a notfound for a tx has been received. */
    void ReceivedNotFound(NodeId nodeid, const std::vector<uint256>& txhashes);
};
} // namespace node
#endif // BGL_NODE_TXDOWNLOADMAN_H
