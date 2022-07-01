#!/usr/bin/env python3
# Copyright (c) 2016-2021 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test RPC commands for signing messages with private key."""

from test_framework.test_framework import BGLTestFramework
from test_framework.util import assert_equal

class SignMessagesWithPrivTest(BGLTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 1

    def run_test(self):
        message = 'This is just a test message'

        self.log.info('test signing with priv_key')
        priv_key = 'cU2MAEpFKrHYzpUQUajkxoerJ33rKwF6ViLoHw2xRu7yy7dXkK5U'
        address = 'Ejt5fCe8NyLDC3nRk5ptc85PWSubNDUY4D'
        expected_signature = 'H28itpEwmM/PUOfLsKTHwtpl3nXwbenOYYW9WBkgYdybYJ71uwQL37f1Ahc0aKlyZ8D1pU5IlZpVSngJHhw2VNs='
        signature = self.nodes[0].signmessagewithprivkey(priv_key, message)
        assert_equal(expected_signature, signature)
        assert self.nodes[0].verifymessage(address, signature, message)

        self.log.info('test parameter validity and error codes')
        # signmessagewithprivkey has two required parameters
        for num_params in [0, 1, 3, 4, 5]:
            param_list = ["dummy"]*num_params
            assert_raises_rpc_error(-1, "signmessagewithprivkey", self.nodes[0].signmessagewithprivkey, *param_list)
        # verifymessage has three required parameters
        for num_params in [0, 1, 2, 4, 5]:
            param_list = ["dummy"]*num_params
            assert_raises_rpc_error(-1, "verifymessage", self.nodes[0].verifymessage, *param_list)
        # invalid key or address provided
        assert_raises_rpc_error(-5, "Invalid private key", self.nodes[0].signmessagewithprivkey, "invalid_key", message)
        assert_raises_rpc_error(-5, "Invalid address", self.nodes[0].verifymessage, "invalid_addr", signature, message)
        # malformed signature provided
        assert_raises_rpc_error(-3, "Malformed base64 encoding", self.nodes[0].verifymessage, 'mpLQjfK79b7CCV4VMJWEWAj5Mpx8Up5zxB', "invalid_sig", message)

if __name__ == '__main__':
    SignMessagesWithPrivTest().main()
