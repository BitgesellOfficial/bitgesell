#!/usr/bin/env python3
# Copyright (c) 2021-2021 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test that a node in blocksonly mode does not request compact blocks."""

from test_framework.messages import (
    MSG_BLOCK,
    MSG_CMPCT_BLOCK,
    MSG_WITNESS_FLAG,
    CBlock,
    CBlockHeader,
    CInv,
    from_hex,
    msg_block,
    msg_headers,
    msg_sendcmpct,
)
from test_framework.p2p import P2PInterface
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal


class P2PCompactBlocksBlocksOnly(BitcoinTestFramework):
    def set_test_params(self):
        self.extra_args = [["-blocksonly"], [], []]
        self.num_nodes = 3

    def setup_network(self):
        self.setup_nodes()
        # Start network with everyone disconnected
        self.sync_all()

    def build_block_on_tip(self):
        blockhash = self.nodes[2].generate(1)[0]
        block_hex = self.nodes[2].getblock(blockhash=blockhash, verbosity=0)
        block = from_hex(CBlock(), block_hex)
        block.rehash()
        return block

    def run_test(self):
        # Nodes will only request hb compact blocks mode when they're out of IBD
        for node in self.nodes:
            assert not node.getblockchaininfo()['initialblockdownload']

        p2p_conn_blocksonly = self.nodes[0].add_p2p_connection(P2PInterface())
        p2p_conn_high_bw = self.nodes[1].add_p2p_connection(P2PInterface())
        for conn in [p2p_conn_blocksonly, p2p_conn_high_bw]:
            assert_equal(conn.message_count['sendcmpct'], 2)
            conn.send_and_ping(msg_sendcmpct(announce=False, version=2))

        # Nodes:
        #   0 -> blocksonly
        #   1 -> high bandwidth
        #   2 -> miner
        #
        # Topology:
        #   p2p_conn_blocksonly ---> node0
        #   p2p_conn_high_bw    ---> node1
        #   node2 (no connections)
        #
        # node2 produces blocks that are passed to the rest of the nodes
        # through the respective p2p connections.

        self.log.info("Test that -blocksonly nodes do not select peers for BIP152 high bandwidth mode")

        block0 = self.build_block_on_tip()

        # A -blocksonly node should not request BIP152 high bandwidth mode upon
        # receiving a new valid block at the tip.
        p2p_conn_blocksonly.send_and_ping(msg_block(block0))
        assert_equal(int(self.nodes[0].getbestblockhash(), 16), block0.sha256)
        assert_equal(p2p_conn_blocksonly.message_count['sendcmpct'], 2)
        assert_equal(p2p_conn_blocksonly.last_message['sendcmpct'].announce, False)

        # A normal node participating in transaction relay should request BIP152
        # high bandwidth mode upon receiving a new valid block at the tip.
        p2p_conn_high_bw.send_and_ping(msg_block(block0))
        assert_equal(int(self.nodes[1].getbestblockhash(), 16), block0.sha256)
        p2p_conn_high_bw.wait_until(lambda: p2p_conn_high_bw.message_count['sendcmpct'] == 3)
        assert_equal(p2p_conn_high_bw.last_message['sendcmpct'].announce, True)

if __name__ == '__main__':
    P2PCompactBlocksBlocksOnly().main()
