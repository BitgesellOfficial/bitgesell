#!/usr/bin/env python3
# Copyright (c) 2020 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test error messages for 'getaddressinfo' and 'validateaddress' RPC commands."""

from test_framework.test_framework import BGLTestFramework

from test_framework.util import (
    assert_equal,
    assert_raises_rpc_error,
)

BECH32_VALID = 'rbgl1qqymf0uykeha35u2m9kaq384xmg53rfl3t46ccx'
BECH32_INVALID_BECH32 = 'rbgl1zqymf0uykeha35u2m9kaq384xmg53rfl3aqawzs'
BECH32_INVALID_BECH32M = 'rbgl1qqymf0uykeha35u2m9kaq384xmg53rfl37f25ay'
BECH32_INVALID_VERSION = 'rbgl13qymf0uykeha35u2m9kaq384xmg53rfl3t46ccx'
BECH32_INVALID_SIZE = 'rbgl1pzem3xr'
BECH32_INVALID_V0_SIZE = 'rbgl1qqymf0uykeha35u2m9kaq384xmg53rfl3mg53rfcdu24t8'
BECH32_INVALID_PREFIX = 'rbgr1qqymf0uykeha35u2m9kaq384xmg53rfl3me9uen'

INVALID_ADDRESS = 'asfah14i8fajz0123f'

class InvalidAddressErrorMessageTest(BGLTestFramework):
    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 1

    def skip_test_if_missing_module(self):
        self.skip_if_no_wallet()

    def test_validateaddress(self):
        node = self.nodes[0]

        # Bech32
        info = node.validateaddress(BECH32_INVALID_SIZE)
        assert not info['isvalid']
        assert_equal(info['error'], 'Invalid Bech32 address data size')

        info = node.validateaddress(BECH32_INVALID_PREFIX)
        assert not info['isvalid']
        assert_equal(info['error'], 'Invalid prefix for Bech32 address')

        info = node.validateaddress(BECH32_INVALID_BECH32)
        assert not info['isvalid']
        assert_equal(info['error'], 'Version 1+ witness address must use Bech32m checksum')

        info = node.validateaddress(BECH32_INVALID_BECH32M)
        assert not info['isvalid']
        assert_equal(info['error'], 'Version 0 witness address must use Bech32 checksum')

        info = node.validateaddress(BECH32_INVALID_V0_SIZE)
        assert not info['isvalid']
        assert_equal(info['error'], 'Invalid Bech32 v0 address data size')

        info = node.validateaddress(BECH32_VALID)
        assert info['isvalid']
        assert 'error' not in info

        # Invalid address format
        info = node.validateaddress(INVALID_ADDRESS)
        assert not info['isvalid']
        assert_equal(info['error'], 'Invalid address format')

    def test_getaddressinfo(self):
        node = self.nodes[0]

        assert_raises_rpc_error(-5, "Invalid Bech32 address data size", node.getaddressinfo, BECH32_INVALID_SIZE)

        assert_raises_rpc_error(-5, "Invalid prefix for Bech32 address", node.getaddressinfo, BECH32_INVALID_PREFIX)

        assert_raises_rpc_error(-5, "Invalid address format", node.getaddressinfo, INVALID_ADDRESS)

    def run_test(self):
        self.test_validateaddress()
        self.test_getaddressinfo()


if __name__ == '__main__':
    InvalidAddressErrorMessageTest().main()
