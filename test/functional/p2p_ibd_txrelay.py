#!/usr/bin/env python3
# Copyright (c) 2020-2021 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test fee filters during and after IBD."""

from decimal import Decimal

from test_framework.messages import COIN
from test_framework.test_framework import BGLTestFramework

MAX_FEE_FILTER = Decimal(9170997) / COIN
NORMAL_FEE_FILTER = Decimal(100) / COIN


class P2PIBDTxRelayTest(BGLTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 2
        self.extra_args = [
            ["-minrelaytxfee={}".format(NORMAL_FEE_FILTER)],
            ["-minrelaytxfee={}".format(NORMAL_FEE_FILTER)],
        ]

    def run_test(self):
        self.log.info("Check that nodes set minfilter to MAX_MONEY while still in IBD")
        for node in self.nodes:
            assert node.getblockchaininfo()['initialblockdownload']
            self.wait_until(lambda: all(peer['minfeefilter'] == MAX_FEE_FILTER for peer in node.getpeerinfo()))

        self.log.info("Check that nodes don't send getdatas for transactions while still in IBD")
        peer_inver = self.nodes[0].add_p2p_connection(P2PDataStore())
        txid = 0xdeadbeef
        peer_inver.send_and_ping(msg_inv([CInv(t=MSG_WTX, h=txid)]))
        # The node should not send a getdata, but if it did, it would first delay 2 seconds
        self.nodes[0].setmocktime(int(time.time() + NONPREF_PEER_TX_DELAY))
        peer_inver.sync_with_ping()
        with p2p_lock:
            assert txid not in peer_inver.getdata_requests
        self.nodes[0].disconnect_p2ps()

        self.log.info("Check that nodes don't process unsolicited transactions while still in IBD")
        # A transaction hex pulled from tx_valid.json. There are no valid transactions since no UTXOs
        # exist yet, but it should be a well-formed transaction.
        rawhex = "0100000001b14bdcbc3e01bdaad36cc08e81e69c82e1060bc14e518db2b49aa43ad90ba260000000004a01ff473" + \
            "04402203f16c6f40162ab686621ef3000b04e75418a0c0cb2d8aebeac894ae360ac1e780220ddc15ecdfc3507ac48e168" + \
            "1a33eb60996631bf6bf5bc0a0682c4db743ce7ca2b01ffffffff0140420f00000000001976a914660d4ef3a743e3e696a" + \
            "d990364e555c271ad504b88ac00000000"
        assert self.nodes[1].decoderawtransaction(rawhex) # returns a dict, should not throw
        tx = from_hex(CTransaction(), rawhex)
        peer_txer = self.nodes[0].add_p2p_connection(P2PInterface())
        with self.nodes[0].assert_debug_log(expected_msgs=["received: tx"], unexpected_msgs=["was not accepted"]):
            peer_txer.send_and_ping(msg_tx(tx))
        self.nodes[0].disconnect_p2ps()

        # Come out of IBD by generating a block
        self.generate(self.nodes[0], 1)

        self.log.info("Check that nodes reset minfilter after coming out of IBD")
        for node in self.nodes:
            assert not node.getblockchaininfo()['initialblockdownload']
            self.wait_until(lambda: all(peer['minfeefilter'] == NORMAL_FEE_FILTER for peer in node.getpeerinfo()))


if __name__ == '__main__':
    P2PIBDTxRelayTest().main()
